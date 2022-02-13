# syntax=docker/dockerfile:1

FROM python:3.8-slim

RUN useradd --create-home --shell /bin/bash wxtwitterbot

VOLUME ["/app"]

RUN python -m pip install --upgrade pip
RUN pip install wxtwitterbot==1.0.3a0

WORKDIR /home/wxtwitterbot
COPY start-app start-app

WORKDIR /app
USER wxtwitterbot
CMD /home/wxtwitterbot/start-app
