# syntax=docker/dockerfile:1
FROM python:3.9-alpine as base
WORKDIR /app
RUN apk add --no-cache --update \
    python3 python3-dev gcc \
    gfortran musl-dev
RUN apk --no-cache add musl-dev linux-headers g++
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . /app
CMD ["python3","run.py"]
