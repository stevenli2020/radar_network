# syntax=docker/dockerfile:1
FROM python:3.9-alpine as base

# Set the working directory inside the container
WORKDIR /code

# Install necessary build tools and dependencies
RUN apk add --no-cache --update \
    python3 python3-dev gcc gfortran musl-dev linux-headers g++

# Set Flask environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_DEBUG=1

# Copy the requirements.txt and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for Flask
EXPOSE 5000

# Copy the rest of the application code
COPY . .

# Define the command to run the Flask application
CMD ["flask", "run"]
