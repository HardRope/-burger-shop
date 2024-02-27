FROM node:16.17.0-bullseye-slim

WORKDIR /app

COPY ./bundles-src/ ./bundles-src/
COPY package*.json ./

RUN npm ci --dev