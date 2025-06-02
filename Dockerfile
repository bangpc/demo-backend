FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
COPY requirements-test.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port (default FastAPI port)
EXPOSE 8000

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
