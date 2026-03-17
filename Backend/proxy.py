"""
Simple reverse proxy server that listens on port 8000 and forwards to port 8080
"""
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import uvicorn

BACKEND_URL = "http://127.0.0.1:8080"

proxy_app = FastAPI()

@proxy_app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_request(path: str, request: Request):
    """Proxy all requests to the backend server"""
    # Build the full URL
    url = f"{BACKEND_URL}/{path}"
    if request.url.query:
        url += f"?{request.url.query}"
    
    # Get request body
    body = await request.body()
    
    # Forward the request
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=url,
                headers=dict(request.headers),
                content=body if body else None,
                follow_redirects=True,
            )
            return StreamingResponse(
                iter([response.content]),
                status_code=response.status_code,
                headers=dict(response.headers),
            )
        except Exception as e:
            return {"error": str(e)}, 502

if __name__ == "__main__":
    print(f"Starting reverse proxy on http://127.0.0.1:8000")
    print(f"Forwarding to backend on {BACKEND_URL}")
    uvicorn.run(proxy_app, host="127.0.0.1", port=8000, log_level="info")
