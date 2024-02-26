FROM python:3.9.6-alpine

WORKDIR /app

COPY ./requirements.txt .
RUN mkdir -p media

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .