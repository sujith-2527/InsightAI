from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd
import os
import re
import uvicorn
import google.generativeai as genai
import json
from difflib import get_close_matches
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
    df.columns = df.columns.str.strip().str.lower()
    print(f"Loaded CSV: {csv_path}")
    print("Columns:", list(df.columns))

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


def normalize_chart_type(value: str | None, query_text: str, groupby: str) -> str:
    if value in {"bar", "line", "area", "pie", "donut"}:
        return value

    q = query_text.lower()
    if any(token in q for token in ["trend", "over time", "monthly", "yearly", "quarter", "timeline"]):
        return "line"
    if any(token in q for token in ["share", "distribution", "percentage", "proportion", "parts"]):
        return "donut"
    if "year" in groupby or "month" in groupby or "date" in groupby:
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
        r"by\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        r"grouped\s+by\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        r"breakdown\s+by\s+([a-zA-Z_][a-zA-Z0-9_]*)",
    ]
    for pattern in patterns:
        match = re.search(pattern, query_text.lower())
        if match:
            return match.group(1)
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


def build_local_plan(query_text: str) -> dict[str, Any]:
    q = query_text.lower().strip()
    metric = default_metric(df)
    groupby = default_groupby(df)
    aggregation = "mean"

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

    tokens = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", q)
    for token in tokens:
        if token in df.columns and token in numeric_columns(df):
            metric = token
            break

    requested_groupby = detect_requested_groupby(q)
    if requested_groupby and requested_groupby in df.columns:
        groupby = requested_groupby
    else:
        for token in tokens:
            if token in df.columns and token != metric:
                groupby = token
                break

    top_n = None
    top_match = re.search(r"top\s+(\d+)", q)
    if top_match:
        top_n = int(top_match.group(1))

    return {
        "metric": metric,
        "groupby": groupby,
        "aggregation": aggregation,
        "chart_type": normalize_chart_type(None, q, groupby),
        "filters": infer_filters_local(q, df),
        "top_n": top_n,
        "sort_order": "desc" if "top" in q or "highest" in q else "asc" if "lowest" in q else "desc",
        "confidence": 0.65,
        "warnings": [],
    }


def build_gemini_plan(query_text: str, context: list[str]) -> dict[str, Any] | None:
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

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        parsed = extract_json(response.text)
        return parsed if isinstance(parsed, dict) else None
    except Exception as exc:
        print(f"Gemini planning error: {exc}. Falling back to local planner.")
        return None


def build_plan(query_text: str, context: list[str]) -> dict[str, Any]:
    gemini = build_gemini_plan(query_text, context)
    local = build_local_plan(query_text)
    candidate = gemini if gemini else local

    metric = sanitize_column(candidate.get("metric"), default_metric(df), df)
    groupby = sanitize_column(candidate.get("groupby"), default_groupby(df), df)
    aggregation = normalize_aggregation(candidate.get("aggregation"))

    if aggregation != "count" and metric not in numeric_columns(df):
        metric = default_metric(df)

    if groupby not in df.columns:
        groupby = default_groupby(df)

    requested_group = detect_requested_groupby(query_text)
    warnings = list(candidate.get("warnings") or [])
    if requested_group and requested_group not in df.columns:
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
            filters.append(
                {
                    "column": col,
                    "operator": "eq",
                    "value": str(item.get("value", "")).strip().lower(),
                }
            )

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
    }


def apply_filters(frame: pd.DataFrame, filters: list[dict[str, str]]) -> pd.DataFrame:
    filtered = frame.copy()
    for flt in filters:
        col = flt["column"]
        val = flt["value"]
        if not val or col not in filtered.columns:
            continue
        if pd.api.types.is_numeric_dtype(filtered[col]):
            numeric_val = pd.to_numeric(val, errors="coerce")
            if pd.notnull(numeric_val):
                filtered = filtered[filtered[col] == numeric_val]
        else:
            filtered = filtered[filtered[col].astype(str).str.lower().str.contains(re.escape(val), na=False)]
    return filtered


def aggregate(frame: pd.DataFrame, metric: str, groupby: str, aggregation: str) -> pd.DataFrame:
    if aggregation == "count":
        return frame.groupby(groupby).size().reset_index(name="count")
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

        try:
            working = apply_filters(df, plan["filters"])

            if working.empty:
                return {
                    "error": "No rows matched the requested filters.",
                    "meta": {
                        "query_parsed": f"{aggregation}({metric}) grouped by {groupby}",
                        "warnings": plan["warnings"],
                    },
                }

            result = aggregate(working, metric, groupby, aggregation)

            result = result.dropna()

            value_col = "count" if aggregation == "count" else metric
            if value_col in result.columns and pd.api.types.is_numeric_dtype(result[value_col]):
                result[value_col] = result[value_col].round(2)

            sort_ascending = plan["sort_order"] == "asc"
            if value_col in result.columns:
                result = result.sort_values(by=value_col, ascending=sort_ascending)

            top_n = plan.get("top_n")
            if isinstance(top_n, int) and top_n > 0:
                result = result.head(top_n)

            record_count = len(result)
            if record_count > 50:
                result = result.head(50)
                plan["warnings"].append("Result limited to first 50 groups for readability.")

            return {
                "data": result.to_dict(orient="records"),
                "meta": {
                    "chart_type": plan["chart_type"],
                    "x": groupby,
                    "y": value_col,
                    "aggregation": aggregation,
                    "query_parsed": f"{aggregation}({metric}) grouped by {groupby}",
                    "record_count": record_count,
                    "confidence": round(plan["confidence"], 2),
                    "filters_applied": plan["filters"],
                    "warnings": plan["warnings"],
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