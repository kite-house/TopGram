FROM python:3.11-alpine
WORKDIR /usr/src/app
COPY requirements.txt .
RUN apk add --no-cache --virtual build-deps gcc musl-dev libffi-dev2 pkgconf mariadb-dev && \
    apk add --no-cache mariadb-connector-c-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del build-deps
COPY . .