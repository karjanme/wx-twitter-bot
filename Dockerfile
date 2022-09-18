# syntax=docker/dockerfile:1

FROM python:3.10-slim

VOLUME ["/app"]

RUN mkdir /wxtwitterbot
WORKDIR /wxtwitterbot
COPY . .

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "src/main.py"]