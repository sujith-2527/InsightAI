# Dockerfile for Conversational Dashboard backend
# Builds a Python image that runs the FastAPI app

FROM python:3.14-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY . .

# Default environment variables
ENV BACKEND_HOST=0.0.0.0
ENV BACKEND_PORT=8080

EXPOSE 8080

CMD ["python", "app.py"]
