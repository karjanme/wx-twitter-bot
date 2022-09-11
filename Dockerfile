# syntax=docker/dockerfile:1

FROM python:3.10-slim

RUN useradd --create-home --shell /bin/bash wxtwitterbot

VOLUME ["/app"]

WORKDIR /home/wxtwitterbot
COPY . .

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

USER wxtwitterbot
CMD ["python", "src/main.py"]