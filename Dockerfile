FROM python:3.11-slim

RUN apt-get update && apt-get install -y libpq5 curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir "pip>=24" && pip install --no-cache-dir .

COPY . .
RUN playwright install --with-deps firefox

EXPOSE 8000
CMD ["gunicorn", "-k", "gevent", "-b", "0.0.0.0:8000", "fb_scraper.web:create_app()"]
