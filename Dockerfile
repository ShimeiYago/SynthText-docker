# Use Python 3.6 + old pip + manylinux1/2010 wheels
# Build for x86_64 (linux/amd64)
FROM python:3.6.15-slim

# Explicitly specify platform
ARG TARGETPLATFORM=linux/amd64

# Install required system packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    gfortran \
    liblapack-dev \
    libblas-dev \
    libhdf5-dev \
    pkg-config \
    libfreetype6-dev \
    libpng-dev \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    libssl-dev \
    wget \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Downgrade pip to 20.3.4 (compatible with old manylinux1/2010 wheels)
RUN pip install --no-cache-dir pip==20.3.4

WORKDIR /app

COPY requirements.txt .

# Install packages with old pip
# Use --prefer-binary to prefer binary wheels when possible
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

COPY . .

# Set environment variables (configure Matplotlib backend)
ENV MPLBACKEND=Agg
