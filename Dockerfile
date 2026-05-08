FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements/base.txt ./requirements.txt
RUN apt-get update && apt-get install -y build-essential gcc libpq-dev --no-install-recommends \
    && pip install --upgrade pip && pip install -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential gcc \
    && rm -rf /var/lib/apt/lists/*
COPY . /app
CMD ["./manage.py", "runserver", "0.0.0.0:8000"]
