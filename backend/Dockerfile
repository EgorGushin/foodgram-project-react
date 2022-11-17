FROM python:3.7-slim

WORKDIR /app
RUN apt-get update
RUN apt-get install libpq-dev gcc -y
COPY requirements.txt .
RUN pip3 install -r ./requirements.txt --no-cache-dir
COPY . .
CMD gunicorn backend.wsgi:application --bind 0.0.0.0:8000