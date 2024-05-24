# syntax=docker/dockerfile:1
FROM python:3.9-alpine as base

RUN apk update && \
    apk add --no-cache mysql-client

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files into the container
COPY . .

# Specify the command to run the Python script
CMD ["python", "run.py"]
