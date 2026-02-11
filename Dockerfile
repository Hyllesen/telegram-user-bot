# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies needed for OpenCV and other packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgomp1 \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libopenblas-dev \
        liblapack-dev \
        gfortran \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create the group_images directory
RUN mkdir -p group_images

# Expose any necessary ports (though this app doesn't serve HTTP)
EXPOSE 80

# Default command to run the application
CMD ["python", "main.py"]