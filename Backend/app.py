from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
import uvicorn
import socket
import google.generativeai as genai
import json
from typing import Optional

app = FastAPI()

# Enable CORS so the frontend can call the backend from the browser.
# In production, set CORS_ORIGINS to a comma-separated list of allowed origins.
allowed_origins_env = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080,http://127.0.0.1:8080",
)
allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    GEMINI_AVAILABLE = True
    print("✓ Gemini API configured successfully")
else:
    GEMINI_AVAILABLE = False
    print("⚠ Gemini API key not configured. Using local query parser.")

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
    print("Columns:", df.columns)

load_data(csv_path)

class Query(BaseModel):
    user_query: str

@app.get("/")
def home():
    return {"message": "Server running 🚀"}

@app.get("/columns")
def get_columns():
    return {"columns": list(df.columns)}

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
        return {"message": "CSV uploaded successfully.", "columns": list(df.columns)}
    except Exception as e:
        return {"error": f"Failed to upload CSV: {str(e)}"}

def parse_query(query_text):
    """
    Intelligent query parser that understands various natural language patterns
    
    Examples:
    - "What is the average price by model?"
    - "Show me total tax grouped by transmission"
    - "How many cars by year?"
    - "Sum of mileage by fueltype"
    - "Min and max price by year"
    - "Price comparison across models"
    """
    query_lower = query_text.lower().strip()
    available_columns = list(df.columns)
    
    # Default values
    metric = "price"
    groupby = "model"
    aggregation = "mean"
    
    # Define aggregation keywords
    agg_keywords = {
        "average": "mean",
        "avg": "mean",
        "mean": "mean",
        "total": "sum",
        "sum": "sum",
        "count": "count",
        "number": "count",
        "how many": "count",
        "minimum": "min",
        "min": "min",
        "maximum": "max",
        "max": "max",
        "highest": "max",
        "lowest": "min",
        "largest": "max",
        "smallest": "min",
        "median": "median",
        "std": "std",
        "standard deviation": "std",
    }
    
    # Detect aggregation function from keywords
    for keyword, agg_func in agg_keywords.items():
        if keyword in query_lower:
            aggregation = agg_func
            break
    
    # Remove common words and special characters to find column names
    tokens = query_lower.replace("?", "").replace("!", "").replace(",", "").split()
    
    # Find columns mentioned in query
    mentioned_metrics = []
    mentioned_groupby = []
    
    for token in tokens:
        clean_token = token.strip('.,!?;:')
        # Check if token matches any column name (case-insensitive partial match)
        for col in available_columns:
            col_lower = col.lower()
            if clean_token == col_lower or col_lower in clean_token or clean_token in col_lower:
                # If preceded by "by", it's likely a groupby column
                if tokens.index(token) > 0 and tokens[tokens.index(token) - 1] == "by":
                    mentioned_groupby.append(col)
                else:
                    mentioned_metrics.append(col)
    
    # Remove duplicates while preserving order
    mentioned_metrics = list(dict.fromkeys(mentioned_metrics))
    mentioned_groupby = list(dict.fromkeys(mentioned_groupby))
    
    # Set metric (prefer first mentioned metric, or use default)
    if mentioned_metrics:
        metric = mentioned_metrics[0]
    
    # Set groupby (prefer first mentioned groupby, or use default)
    if mentioned_groupby:
        groupby = mentioned_groupby[0]
    
    # Validate columns exist
    if metric not in df.columns:
        metric = "price"
    if groupby not in df.columns:
        groupby = "model"
    
    # Simple validation: ignore non-numeric columns for aggregation
    if df[metric].dtype not in ['float64', 'float32', 'int64', 'int32']:
        metric = "price"
    
    return metric, groupby, aggregation

def parse_query_with_gemini(query_text):
    """
    Enhanced query parser using Google Gemini API for better understanding
    of natural language queries. Falls back to local parser if API is unavailable.
    """
    if not GEMINI_AVAILABLE:
        return parse_query(query_text)
    
    try:
        available_columns = list(df.columns)
        
        prompt = f"""You are a data analysis assistant. Given a user query about a cars dataset, extract:
1. The metric column to analyze (one of: {', '.join(available_columns)})
2. The groupby column (one of: {', '.join(available_columns)})
3. The aggregation function (mean, sum, count, min, max, median, or std)

User Query: {query_text}

Respond in this exact JSON format:
{{
    "metric": "column_name",
    "groupby": "column_name",
    "aggregation": "function_name"
}}

If the query is ambiguous, make reasonable defaults:
- metric: defaults to 'price'
- groupby: defaults to 'model'
- aggregation: defaults to 'mean'

Only respond with valid JSON, no other text."""
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        # Parse the response
        response_text = response.text.strip()
        
        # Try to extract JSON from response
        try:
            if '```json' in response_text:
                json_str = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                json_str = response_text.split('```')[1].split('```')[0].strip()
            else:
                json_str = response_text
            
            parsed = json.loads(json_str)
            metric = parsed.get('metric', 'price')
            groupby = parsed.get('groupby', 'model')
            aggregation = parsed.get('aggregation', 'mean')
        except (json.JSONDecodeError, IndexError, KeyError, ValueError):
            # Fallback to local parser if JSON parsing fails
            return parse_query(query_text)
        
        # Validate columns exist
        if metric not in df.columns:
            metric = 'price'
        if groupby not in df.columns:
            groupby = 'model'
        
        # Validate aggregation type
        valid_aggs = ['mean', 'sum', 'count', 'min', 'max', 'median', 'std']
        if aggregation not in valid_aggs:
            aggregation = 'mean'
        
        # Validate metric is numeric
        if df[metric].dtype not in ['float64', 'float32', 'int64', 'int32']:
            metric = 'price'
        
        return metric, groupby, aggregation
    
    except Exception as e:
        print(f"Gemini API error: {e}. Falling back to local parser.")
        return parse_query(query_text)

@app.post("/query")
def process_query(q: Query):
    try:
        query_text = q.user_query.strip()
        
        if not query_text:
            return {"error": "Query text cannot be empty"}
        
        # Parse the user query intelligently (uses Gemini if available, else local parser)
        metric, groupby, aggregation = parse_query_with_gemini(query_text)
        
        try:
            # Perform the appropriate aggregation
            if aggregation == "count":
                result = df.groupby(groupby).size().reset_index(name=metric)
            elif aggregation == "mean":
                result = df.groupby(groupby)[metric].mean().reset_index()
            elif aggregation == "sum":
                result = df.groupby(groupby)[metric].sum().reset_index()
            elif aggregation == "min":
                result = df.groupby(groupby)[metric].min().reset_index()
            elif aggregation == "max":
                result = df.groupby(groupby)[metric].max().reset_index()
            elif aggregation == "median":
                result = df.groupby(groupby)[metric].median().reset_index()
            elif aggregation == "std":
                result = df.groupby(groupby)[metric].std().reset_index()
            else:
                result = df.groupby(groupby)[metric].mean().reset_index()
            
            # Remove NaN values
            result = result.dropna()
            
            # Round numeric results to 2 decimal places
            if result[metric].dtype in ['float64', 'float32', 'int64', 'int32']:
                result[metric] = result[metric].round(2)
            
            # Rename columns for consistency in response
            result.columns = [groupby, metric]
            
            return {
                "data": result.to_dict(orient="records"),
                "meta": {
                    "chart_type": "bar",
                    "x": groupby,
                    "y": metric,
                    "aggregation": aggregation,
                    "query_parsed": f"{aggregation}({metric}) grouped by {groupby}",
                    "record_count": len(result)
                }
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
    port = int(os.getenv("BACKEND_PORT", "8080"))
    reload = os.getenv("DEBUG_MODE", "false").lower() in ["1", "true", "yes"]

    uvicorn.run(app, host=host, port=port, log_level="info", reload=reload)