# Use an official Python runtime as a base image
FROM python:3.9-slim

# Create and set the working directory
RUN mkdir -p /var/app
WORKDIR /var/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    cmake \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Set environment variables for Poetry
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    PIP_NO_CACHE_DIR=false \
    PATH="${PATH}:/root/.local/bin:/var/app/libs:/root/.local/bin" \
    PYTHONPATH="${PYTHONPATH}:/var/app/libs:/var/app"

# Install Poetry
RUN pip install poetry

# Install dependencies (including dlib)
RUN poetry install --no-root

# Copy the application code
COPY ./libs ./libs

# Expose port 8000
EXPOSE 8000

# Run the application
CMD ["uvicorn", "libs.services.main:app", "--host", "0.0.0.0", "--port", "8000"]