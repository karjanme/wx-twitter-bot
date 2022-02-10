# syntax=docker/dockerfile:1

FROM python:3.8-slim

RUN useradd --create-home --shell /bin/bash wxtwitterbot

VOLUME ["/app"]

WORKDIR /home/wxtwitterbot
COPY dist/ dist/

RUN python -m pip install --upgrade pip
RUN pip install dist/wxtwitterbot-0.2.2-py3-none-any.whl

#RUN pip install wxtwitterbot

COPY start-app start-app

WORKDIR /app

USER wxtwitterbot
CMD /home/wxtwitterbot/start-app
