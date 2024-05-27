FROM python:3.11.6-alpine3.18

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


RUN mkdir -p /files/media /files/static /app/flights/migrations \
    && adduser -D -H my_user \
    && chown -R my_user /app /files/media /files/static /app/flights/migrations \
    && chmod -R 755 /files/media /files/static /app/flights/migrations

USER my_user
