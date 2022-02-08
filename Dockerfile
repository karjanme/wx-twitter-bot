# syntax=docker/dockerfile:1

FROM python:3.8-slim

VOLUME ["/data"]
VOLUME ["/env"]
VOLUME ["/log"]

RUN python -m pip install --upgrade pip

WORKDIR /app

RUN pip install wxtwitterbot

COPY start-app start-app
#CMD start-app
