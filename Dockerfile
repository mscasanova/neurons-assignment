FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Avoid interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip separately to avoid old wheels
RUN pip install --upgrade pip

# Copy requirements first for better caching
COPY requirements.txt ./

# Install dependencies (using --no-cache-dir to reduce size)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose FastAPI and Gradio ports
EXPOSE 8000
EXPOSE 8501

# Start API and UI
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & python3 app/frontend/frontend.py"]

