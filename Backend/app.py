from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import os
import uvicorn
import socket

app = FastAPI()

# Use absolute path to CSV file
csv_path = os.path.join(os.path.dirname(__file__), "cars.csv")
df = pd.read_csv(csv_path)

# clean column names
df.columns = df.columns.str.strip().str.lower()

print("Columns:", df.columns)

class Query(BaseModel):
    user_query: str

@app.get("/")
def home():
    return {"message": "Server running 🚀"}

@app.get("/columns")
def get_columns():
    return {"columns": list(df.columns)}

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

@app.post("/query")
def process_query(q: Query):
    try:
        query_text = q.user_query.strip()
        
        if not query_text:
            return {"error": "Query text cannot be empty"}
        
        # Parse the user query intelligently
        metric, groupby, aggregation = parse_query(query_text)
        
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
    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="info")