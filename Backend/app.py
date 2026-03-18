from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd
import os
import re
import uvicorn
import google.generativeai as genai
import json
from difflib import get_close_matches, SequenceMatcher
from typing import Any

app = FastAPI(title="Conversational BI API", version="2.0.0")

# Enable CORS so the frontend can call the backend from the browser.
# In production, set CORS_ORIGINS to a comma-separated list of allowed origins.
allowed_origins_env = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080,http://127.0.0.1:8080",
)
allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
allow_origin_regex = os.getenv("CORS_ORIGIN_REGEX", r"https://.*\.vercel\.app")
allow_all_origins = os.getenv("CORS_ALLOW_ALL", "false").lower() in {"1", "true", "yes"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all_origins else allowed_origins,
    allow_origin_regex=None if allow_all_origins else allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    GEMINI_AVAILABLE = True
    print("Gemini API configured successfully")
else:
    GEMINI_AVAILABLE = False
    print("Gemini API key not configured. Using local query parser.")

GEMINI_MODEL_CANDIDATES = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
ACTIVE_GEMINI_MODEL: str | None = None

# Use absolute path to CSV file
csv_path = os.path.join(os.path.dirname(__file__), "cars.csv")

# Global DataFrame used by all endpoints
# It can be replaced by uploading a new CSV file.
df = pd.read_csv(csv_path)

# clean column names

def load_data(path: str):
    """Load a CSV file into the global dataframe and normalize column names."""
    global df, csv_path
    csv_path = path
    df = pd.read_csv(csv_path)
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace('"', "", regex=False)
        .str.replace("'", "", regex=False)
    )
    object_cols = df.select_dtypes(include=["object"]).columns
    for col in object_cols:
        df[col] = df[col].astype(str).str.strip()
    print(f"Loaded CSV: {csv_path}")
    print("Columns:", list(df.columns))


def canonical_name(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def has_groupby_intent(query_text: str) -> bool:
    return any(
        token in query_text
        for token in [" by ", "group by", "grouped by", "breakdown", "per ", "for each", "across "]
    )


def has_count_intent(query_text: str) -> bool:
    return any(token in query_text for token in ["how many", "count", "number of"])


def has_unique_intent(query_text: str) -> bool:
    return any(token in query_text for token in ["unique", "distinct", "different types", "distinct values"])


def has_list_intent(query_text: str) -> bool:
    return any(token in query_text for token in ["show", "list", "display", "find"]) and any(
        token in query_text for token in [" where ", " with ", " that ", " whose "]
    )


def infer_limit(query_text: str) -> int | None:
    top_match = re.search(r"(?:top|first|last)\s+(\d+)", query_text)
    if top_match:
        return int(top_match.group(1))
    limit_match = re.search(r"(?:limit|show)\s+(\d+)", query_text)
    if limit_match:
        return int(limit_match.group(1))
    return None


def match_column_from_query(query_text: str, frame: pd.DataFrame, candidates: list[str]) -> str | None:
    """Pick the best matching column by exact token, phrase, then fuzzy similarity."""
    q = query_text.lower()
    tokens = set(re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", q))
    canonical_tokens = {canonical_name(t) for t in tokens}
    canonical_map = {canonical_name(c): c for c in candidates}

    for col in candidates:
        if col in tokens or canonical_name(col) in canonical_tokens:
            return col

    for col in candidates:
        if re.search(rf"\b{re.escape(col)}\b", q) or canonical_name(col) in canonical_name(q):
            return col

    aliases = {
        "car": "model",
        "cars": "model",
        "vehicle": "model",
        "vehicles": "model",
        "cost": "price",
        "value": "price",
        "amount": "price",
        "fuel": "fueltype",
        "engine": "enginesize",
        "miles": "mileage",
        "mile": "mileage",
        "distance": "mileage",
        "age": "year",
    }
    for token in tokens:
        mapped = aliases.get(token)
        if mapped and mapped in candidates:
            return mapped
    for token in tokens:
        mapped = aliases.get(token)
        if mapped and canonical_name(mapped) in canonical_map:
            return canonical_map[canonical_name(mapped)]

    best_col = None
    best_score = 0.0
    for col in candidates:
        col_tokens = col.replace("_", " ").split()
        score = max((SequenceMatcher(None, token, part).ratio() for token in tokens for part in col_tokens), default=0.0)
        if score > best_score:
            best_score = score
            best_col = col

    return best_col if best_score >= 0.8 else None

load_data(csv_path)


def numeric_columns(frame: pd.DataFrame) -> list[str]:
    return [col for col in frame.columns if pd.api.types.is_numeric_dtype(frame[col])]


def categorical_columns(frame: pd.DataFrame) -> list[str]:
    return [col for col in frame.columns if not pd.api.types.is_numeric_dtype(frame[col])]


def extract_json(text: str) -> dict[str, Any] | None:
    cleaned = text.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    if "```json" in cleaned:
        maybe = cleaned.split("```json", 1)[1].split("```", 1)[0].strip()
        try:
            return json.loads(maybe)
        except json.JSONDecodeError:
            return None
    if "```" in cleaned:
        maybe = cleaned.split("```", 1)[1].split("```", 1)[0].strip()
        try:
            return json.loads(maybe)
        except json.JSONDecodeError:
            return None
    return None


def normalize_chart_type(value: str | None, query_text: str, groupby: str | None) -> str:
    if value in {"bar", "line", "area", "pie", "donut"}:
        return value

    q = query_text.lower()
    if any(token in q for token in ["trend", "over time", "monthly", "yearly", "quarter", "timeline"]):
        return "line"
    if any(token in q for token in ["share", "distribution", "percentage", "proportion", "parts"]):
        return "donut"
    if groupby and ("year" in groupby or "month" in groupby or "date" in groupby):
        return "line"
    return "bar"


def sanitize_column(candidate: str | None, default_col: str, frame: pd.DataFrame) -> str:
    if candidate and candidate in frame.columns:
        return candidate
    if not candidate:
        return default_col

    lower_map = {c.lower(): c for c in frame.columns}
    if candidate.lower() in lower_map:
        return lower_map[candidate.lower()]

    canonical_map = {canonical_name(c): c for c in frame.columns}
    candidate_canonical = canonical_name(candidate)
    if candidate_canonical in canonical_map:
        return canonical_map[candidate_canonical]

    close = get_close_matches(candidate.lower(), list(lower_map.keys()), n=1, cutoff=0.75)
    if close:
        return lower_map[close[0]]
    return default_col


def normalize_aggregation(value: str | None) -> str:
    valid = {"mean", "sum", "count", "min", "max", "median", "std"}
    if value in valid:
        return value
    return "mean"


def detect_requested_groupby(query_text: str) -> str | None:
    patterns = [
        r"by\s+([a-zA-Z_][a-zA-Z0-9_\s]*)",
        r"grouped\s+by\s+([a-zA-Z_][a-zA-Z0-9_\s]*)",
        r"breakdown\s+by\s+([a-zA-Z_][a-zA-Z0-9_\s]*)",
        r"per\s+([a-zA-Z_][a-zA-Z0-9_\s]*)",
        r"for each\s+([a-zA-Z_][a-zA-Z0-9_\s]*)",
    ]
    for pattern in patterns:
        match = re.search(pattern, query_text.lower())
        if match:
            return match.group(1).strip()
    return None


def default_metric(frame: pd.DataFrame) -> str:
    preferred = ["price", "sales", "revenue", "amount", "tax", "mileage"]
    numeric = numeric_columns(frame)
    for col in preferred:
        if col in numeric:
            return col
    return numeric[0] if numeric else frame.columns[0]


def default_groupby(frame: pd.DataFrame) -> str:
    preferred = ["model", "region", "category", "year", "month", "transmission", "fueltype"]
    for col in preferred:
        if col in frame.columns:
            return col
    categorical = categorical_columns(frame)
    return categorical[0] if categorical else frame.columns[0]


def infer_filters_local(query_text: str, frame: pd.DataFrame) -> list[dict[str, str]]:
    filters: list[dict[str, str]] = []
    q = query_text.lower()

    for col in frame.columns:
        if pd.api.types.is_numeric_dtype(frame[col]):
            continue
        values = frame[col].dropna().astype(str).str.lower().unique().tolist()
        for value in values[:200]:
            if re.search(rf"\b{re.escape(value)}\b", q):
                filters.append({"column": col, "operator": "eq", "value": value})
                break

    return filters


def infer_numeric_filters_local(query_text: str, frame: pd.DataFrame) -> list[dict[str, str]]:
    filters: list[dict[str, str]] = []
    q = query_text.lower()

    comparison_map = {
        "greater than": "gt",
        "more than": "gt",
        "above": "gt",
        "less than": "lt",
        "below": "lt",
        "at least": "gte",
        "at most": "lte",
    }

    for col in numeric_columns(frame):
        col_pattern = re.escape(col)

        between = re.search(rf"\b{col_pattern}\b\s*(?:between|from)\s*(-?\d+(?:\.\d+)?)\s*(?:and|to)\s*(-?\d+(?:\.\d+)?)", q)
        if between:
            low_val = between.group(1)
            high_val = between.group(2)
            filters.append({"column": col, "operator": "gte", "value": low_val})
            filters.append({"column": col, "operator": "lte", "value": high_val})
            continue

        symbolic = re.search(rf"\b{col_pattern}\b\s*(>=|<=|>|<|=)\s*(-?\d+(?:\.\d+)?)", q)
        if symbolic:
            op = symbolic.group(1)
            op_map = {">": "gt", "<": "lt", ">=": "gte", "<=": "lte", "=": "eq"}
            filters.append({"column": col, "operator": op_map[op], "value": symbolic.group(2)})
            continue

        for phrase, op in comparison_map.items():
            verbal = re.search(rf"\b{col_pattern}\b\s*(?:is\s+)?{re.escape(phrase)}\s*(-?\d+(?:\.\d+)?)", q)
            if verbal:
                filters.append({"column": col, "operator": op, "value": verbal.group(1)})
                break

        standalone = re.search(rf"{re.escape(col.replace('_', ' '))}\s*(\d+(?:\.\d+)?)", q)
        if standalone:
            filters.append({"column": col, "operator": "eq", "value": standalone.group(1)})

    if "year" in frame.columns:
        older = re.search(r"(older than|before)\s*(\d{4})", q)
        newer = re.search(r"(newer than|after)\s*(\d{4})", q)
        if older:
            filters.append({"column": "year", "operator": "lt", "value": older.group(2)})
        if newer:
            filters.append({"column": "year", "operator": "gt", "value": newer.group(2)})

    # Handle natural phrases like "1.5 litre capacity" or "2.0L engine".
    if "enginesize" in frame.columns:
        litre_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:l|litre|liter)\b", q)
        capacity_hint = any(token in q for token in ["capacity", "engine", "engine size", "enginesize"])
        if litre_match and capacity_hint:
            filters.append({"column": "enginesize", "operator": "eq", "value": litre_match.group(1)})

    return filters


def build_local_plan(query_text: str) -> dict[str, Any]:
    q = query_text.lower().strip()
    metric = default_metric(df)
    groupby = None
    aggregation = "mean"
    matched_metric = False
    matched_groupby = False

    agg_keywords = {
        "average": "mean",
        "avg": "mean",
        "mean": "mean",
        "total": "sum",
        "sum": "sum",
        "count": "count",
        "how many": "count",
        "number": "count",
        "minimum": "min",
        "min": "min",
        "maximum": "max",
        "max": "max",
        "highest": "max",
        "lowest": "min",
        "median": "median",
        "std": "std",
        "standard deviation": "std",
    }
    for key, value in agg_keywords.items():
        if key in q:
            aggregation = value
            break

    numeric_cols = numeric_columns(df)
    categorical_cols = categorical_columns(df)
    tokens = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", q)

    of_match = re.search(r"(?:of|for)\s+([a-zA-Z_][a-zA-Z0-9_]*)", q)
    if of_match and of_match.group(1) in numeric_cols:
        metric = of_match.group(1)
        matched_metric = True
    else:
        matched_metric = match_column_from_query(q, df, numeric_cols)
        if matched_metric:
            metric = matched_metric
            matched_metric = True

    requested_groupby = detect_requested_groupby(q)
    if requested_groupby:
        groupby = sanitize_column(requested_groupby, default_groupby(df), df)
        matched_groupby = True
    elif has_groupby_intent(q):
        matched_groupby = match_column_from_query(q, df, [c for c in categorical_cols if c != metric])
        groupby = matched_groupby if matched_groupby else default_groupby(df)
        matched_groupby = bool(matched_groupby)
    else:
        groupby = None

    top_n = infer_limit(q)

    # Handle phrases like "top 5 models by price" by treating "models" as groupby and "price" as metric.
    by_phrase = re.search(r"(?:top\s+\d+\s+)?([a-zA-Z_][a-zA-Z0-9_\s]*)\s+by\s+([a-zA-Z_][a-zA-Z0-9_\s]*)", q)
    if by_phrase:
        left = sanitize_column(by_phrase.group(1).strip(), "", df)
        right = sanitize_column(by_phrase.group(2).strip(), "", df)
        if right in numeric_cols:
            metric = right
        if left and left in df.columns and left != metric:
            groupby = left

    if groupby == metric:
        alternatives = [c for c in categorical_cols if c != metric]
        groupby = match_column_from_query(q, df, alternatives) or default_groupby(df)
        matched_groupby = True

    # Deterministic intent rules for superlative questions.
    # Example: "what's the oldest car I have" -> min(year) by model, top 1.
    if "oldest" in q and "year" in df.columns:
        metric = "year"
        aggregation = "min"
        if "model" in df.columns:
            groupby = "model"
        top_n = 1
    elif "newest" in q and "year" in df.columns:
        metric = "year"
        aggregation = "max"
        if "model" in df.columns:
            groupby = "model"
        top_n = 1
    elif any(token in q for token in ["cheapest", "lowest price", "least expensive"]) and "price" in df.columns:
        metric = "price"
        aggregation = "min"
        if "model" in df.columns:
            groupby = "model"
        top_n = 1
    elif any(token in q for token in ["most expensive", "costliest", "highest price"]) and "price" in df.columns:
        metric = "price"
        aggregation = "max"
        if "model" in df.columns:
            groupby = "model"
        top_n = 1

    sort_order = "desc" if "top" in q or "highest" in q else "asc" if "lowest" in q else "desc"
    if "oldest" in q or "cheapest" in q or "lowest price" in q or "least expensive" in q:
        sort_order = "asc"
    if "newest" in q or "most expensive" in q or "costliest" in q:
        sort_order = "desc"

    if has_unique_intent(q):
        aggregation = "count"
        if not groupby:
            groupby = match_column_from_query(q, df, categorical_cols) or default_groupby(df)

    if has_count_intent(q):
        aggregation = "count"
        if not has_groupby_intent(q):
            groupby = None

    # "show/list ... where/with ..." without explicit aggregate defaults to count of matching rows.
    if has_list_intent(q) and not any(k in q for k in ["average", "avg", "sum", "total", "min", "max", "median", "std"]):
        aggregation = "count"
        if not has_groupby_intent(q):
            groupby = None

    if any(token in q for token in ["highest", "lowest"]) and top_n is None:
        top_n = 1

    local_filters = infer_filters_local(q, df) + infer_numeric_filters_local(q, df)

    # Avoid returning misleading defaults for unrelated/random prompts.
    intent_tokens = any(
        token in q
        for token in [
            "average",
            "avg",
            "mean",
            "sum",
            "total",
            "count",
            "how many",
            "number",
            "min",
            "max",
            "median",
            "std",
            "top",
            "trend",
            "show",
            "list",
            "find",
            "by",
            "where",
            "greater than",
            "less than",
            "between",
            "older",
            "newer",
        ]
    )
    has_domain_signal = matched_metric or matched_groupby or bool(local_filters)
    unmapped_query = not has_domain_signal and not intent_tokens

    return {
        "metric": metric,
        "groupby": groupby,
        "aggregation": aggregation,
        "chart_type": normalize_chart_type(None, q, groupby),
        "filters": local_filters,
        "top_n": top_n,
        "sort_order": sort_order,
        "confidence": 0.0 if unmapped_query else 0.65,
        "warnings": ["Could not map query to dataset columns."] if unmapped_query else [],
        "unmapped_query": unmapped_query,
    }


def build_gemini_plan(query_text: str, context: list[str]) -> dict[str, Any] | None:
    global GEMINI_AVAILABLE, ACTIVE_GEMINI_MODEL
    if not GEMINI_AVAILABLE:
        return None

    available_columns = list(df.columns)
    prompt = f"""
You are a strict query planner for a Business Intelligence application.
Dataset columns: {available_columns}
Numeric columns: {numeric_columns(df)}
User query: {query_text}
Conversation context (latest first): {context}

Return ONLY a JSON object with this shape:
{{
  "metric": "column name",
  "groupby": "column name",
  "aggregation": "mean|sum|count|min|max|median|std",
  "chart_type": "bar|line|area|pie|donut",
  "filters": [{{"column":"column","operator":"eq","value":"text"}}],
  "top_n": 5,
  "sort_order": "asc|desc",
  "confidence": 0.0,
  "warnings": ["string"]
}}

Rules:
- Use only existing columns.
- If uncertain, use defaults metric={default_metric(df)} groupby={default_groupby(df)} aggregation=mean.
- For trend/time requests use line.
- For part-to-whole requests use donut.
""".strip()

    candidates = [ACTIVE_GEMINI_MODEL] if ACTIVE_GEMINI_MODEL else GEMINI_MODEL_CANDIDATES
    for model_name in [m for m in candidates if m]:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            parsed = extract_json(response.text)
            if isinstance(parsed, dict):
                ACTIVE_GEMINI_MODEL = model_name
                return parsed
        except Exception as exc:
            print(f"Gemini planning error using {model_name}: {exc}")

    GEMINI_AVAILABLE = False
    print("Gemini planning unavailable for configured key. Falling back to local planner.")
    return None


def build_plan(query_text: str, context: list[str]) -> dict[str, Any]:
    llm_candidate = build_gemini_plan(query_text, context)
    local = build_local_plan(query_text)
    candidate = llm_candidate if llm_candidate else local

    metric = sanitize_column(candidate.get("metric"), default_metric(df), df)
    raw_groupby = candidate.get("groupby")
    groupby = sanitize_column(raw_groupby, default_groupby(df), df) if raw_groupby else None
    aggregation = normalize_aggregation(candidate.get("aggregation"))

    if aggregation != "count" and metric not in numeric_columns(df):
        metric = default_metric(df)

    if aggregation == "count" and metric not in df.columns:
        metric = default_metric(df)

    if groupby and groupby not in df.columns:
        groupby = default_groupby(df)

    requested_group = detect_requested_groupby(query_text)
    warnings = list(candidate.get("warnings") or [])
    if requested_group and sanitize_column(requested_group, "", df) not in df.columns:
        suggestions = get_close_matches(requested_group, list(df.columns), n=3, cutoff=0.5)
        if suggestions:
            warnings.append(
                f"Column '{requested_group}' not found. Closest matches: {', '.join(suggestions)}."
            )
        else:
            warnings.append(f"Column '{requested_group}' not found in current dataset.")

    raw_filters = candidate.get("filters") or []
    filters: list[dict[str, str]] = []
    for item in raw_filters:
        if not isinstance(item, dict):
            continue
        col = sanitize_column(item.get("column"), "", df)
        if col and col in df.columns:
            operator = str(item.get("operator", "eq")).strip().lower()
            if operator not in {"eq", "contains", "lt", "lte", "gt", "gte"}:
                operator = "eq"
            filters.append(
                {
                    "column": col,
                    "operator": operator,
                    "value": str(item.get("value", "")).strip().lower(),
                }
            )

    unmapped_query = bool(candidate.get("unmapped_query", False))
    if float(candidate.get("confidence", 0.6)) < 0.2 and not filters and not groupby:
        unmapped_query = True

    return {
        "metric": metric,
        "groupby": groupby,
        "aggregation": aggregation,
        "chart_type": normalize_chart_type(candidate.get("chart_type"), query_text, groupby),
        "filters": filters,
        "top_n": candidate.get("top_n"),
        "sort_order": candidate.get("sort_order") if candidate.get("sort_order") in {"asc", "desc"} else "desc",
        "confidence": float(candidate.get("confidence", local.get("confidence", 0.6))),
        "warnings": warnings,
        "unmapped_query": unmapped_query,
    }


def apply_filters(frame: pd.DataFrame, filters: list[dict[str, str]]) -> pd.DataFrame:
    filtered = frame.copy()
    for flt in filters:
        col = flt["column"]
        val = flt["value"]
        op = flt.get("operator", "eq")
        if not val or col not in filtered.columns:
            continue
        if pd.api.types.is_numeric_dtype(filtered[col]):
            numeric_val = pd.to_numeric(val, errors="coerce")
            if pd.notnull(numeric_val):
                if op == "gt":
                    filtered = filtered[filtered[col] > numeric_val]
                elif op == "gte":
                    filtered = filtered[filtered[col] >= numeric_val]
                elif op == "lt":
                    filtered = filtered[filtered[col] < numeric_val]
                elif op == "lte":
                    filtered = filtered[filtered[col] <= numeric_val]
                else:
                    filtered = filtered[filtered[col] == numeric_val]
        else:
            if op == "eq":
                filtered = filtered[filtered[col].astype(str).str.lower() == val]
            else:
                filtered = filtered[filtered[col].astype(str).str.lower().str.contains(re.escape(val), na=False)]
    return filtered


def aggregate(frame: pd.DataFrame, metric: str, groupby: str, aggregation: str) -> pd.DataFrame:
    if aggregation == "count":
        return frame.groupby(groupby, dropna=False).size().reset_index(name="count")
    if aggregation == "mean":
        return frame.groupby(groupby)[metric].mean().reset_index()
    if aggregation == "sum":
        return frame.groupby(groupby)[metric].sum().reset_index()
    if aggregation == "min":
        return frame.groupby(groupby)[metric].min().reset_index()
    if aggregation == "max":
        return frame.groupby(groupby)[metric].max().reset_index()
    if aggregation == "median":
        return frame.groupby(groupby)[metric].median().reset_index()
    if aggregation == "std":
        return frame.groupby(groupby)[metric].std().reset_index()
    return frame.groupby(groupby)[metric].mean().reset_index()


def aggregate_scalar(frame: pd.DataFrame, metric: str, aggregation: str) -> float | int:
    if aggregation == "count":
        return int(len(frame))
    if aggregation == "mean":
        return float(frame[metric].mean())
    if aggregation == "sum":
        return float(frame[metric].sum())
    if aggregation == "min":
        return float(frame[metric].min())
    if aggregation == "max":
        return float(frame[metric].max())
    if aggregation == "median":
        return float(frame[metric].median())
    if aggregation == "std":
        return float(frame[metric].std())
    return float(frame[metric].mean())

class Query(BaseModel):
    user_query: str
    context: list[str] = Field(default_factory=list)

@app.get("/")
def home():
    return {"message": "Server running"}

@app.get("/columns")
def get_columns():
    return {
        "columns": list(df.columns),
        "numeric_columns": numeric_columns(df),
        "categorical_columns": categorical_columns(df),
        "row_count": len(df),
    }

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Upload a new CSV file and replace the current dataset."""

    if not file.filename.lower().endswith(".csv"):
        return {"error": "Only CSV files are supported."}

    dest_path = os.path.join(os.path.dirname(__file__), "uploaded.csv")
    try:
        contents = await file.read()
        with open(dest_path, "wb") as f:
            f.write(contents)

        load_data(dest_path)
        return {
            "message": "CSV uploaded successfully.",
            "columns": list(df.columns),
            "numeric_columns": numeric_columns(df),
            "row_count": len(df),
        }
    except Exception as e:
        return {"error": f"Failed to upload CSV: {str(e)}"}

@app.post("/query")
def process_query(q: Query):
    try:
        query_text = q.user_query.strip()

        if not query_text:
            return {"error": "Query text cannot be empty"}

        plan = build_plan(query_text, q.context)
        metric = plan["metric"]
        groupby = plan["groupby"]
        aggregation = plan["aggregation"]

        if plan.get("unmapped_query"):
            return {
                "error": "I could not map that question to your dataset. Please ask with your column names or metrics.",
                "meta": {
                    "query_parsed": "unmapped_query",
                    "warnings": plan["warnings"],
                },
            }

        try:
            working = apply_filters(df, plan["filters"])

            if working.empty:
                return {
                    "error": "No rows matched the requested filters.",
                    "meta": {
                        "query_parsed": f"{aggregation}({metric}) grouped by {groupby}" if groupby else f"{aggregation}({metric})",
                        "warnings": plan["warnings"],
                    },
                }
            value_col = "count" if aggregation == "count" else metric

            if groupby:
                result = aggregate(working, metric, groupby, aggregation)
                result = result.dropna()

                if value_col in result.columns and pd.api.types.is_numeric_dtype(result[value_col]):
                    result[value_col] = result[value_col].round(2)

                sort_ascending = plan["sort_order"] == "asc"
                if value_col in result.columns:
                    result = result.sort_values(by=value_col, ascending=sort_ascending)

                top_n = plan.get("top_n")
                if isinstance(top_n, int) and top_n > 0:
                    result = result.head(top_n)
                x_axis = groupby
            else:
                scalar_value = aggregate_scalar(working, metric, aggregation)
                if isinstance(scalar_value, float):
                    scalar_value = round(scalar_value, 2)
                result = pd.DataFrame([{"scope": "all", value_col: scalar_value}])
                x_axis = "scope"

            record_count = len(result)
            if record_count > 50:
                result = result.head(50)
                plan["warnings"].append("Result limited to first 50 groups for readability.")

            kpis: dict[str, float | int] = {
                "source_row_count": int(len(working))
            }
            if aggregation == "count":
                kpis["count"] = int(len(working))
            elif metric in working.columns and pd.api.types.is_numeric_dtype(working[metric]):
                series = working[metric].dropna()
                if not series.empty:
                    kpis.update(
                        {
                            "average": round(float(series.mean()), 2),
                            "total": round(float(series.sum()), 2),
                            "minimum": round(float(series.min()), 2),
                            "maximum": round(float(series.max()), 2),
                        }
                    )

            return {
                "data": result.to_dict(orient="records"),
                "meta": {
                    "chart_type": plan["chart_type"],
                    "x": x_axis,
                    "y": value_col,
                    "aggregation": aggregation,
                    "query_parsed": (
                        f"{aggregation}({metric}) grouped by {groupby}"
                        if groupby
                        else "count(rows)" if aggregation == "count" else f"{aggregation}({metric})"
                    ),
                    "record_count": record_count,
                    "confidence": round(plan["confidence"], 2),
                    "filters_applied": plan["filters"],
                    "warnings": plan["warnings"],
                    "kpis": kpis,
                },
            }
        except Exception as agg_error:
            return {
                "error": f"Failed to aggregate data: {str(agg_error)}",
                "suggestion": f"Tried to calculate {aggregation} of '{metric}' grouped by '{groupby}'"
            }

    except Exception as e:
        return {"error": f"Query processing failed: {str(e)}"}


if __name__ == "__main__":
    # Allow overriding host/port via environment variables for deployment
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", os.getenv("PORT", "8080")))
    reload = os.getenv("DEBUG_MODE", "false").lower() in ["1", "true", "yes"]

    uvicorn.run(app, host=host, port=port, log_level="info", reload=reload)