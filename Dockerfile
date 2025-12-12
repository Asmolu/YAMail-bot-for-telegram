FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure the data directory exists for the SQLite database
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["python", "-m", "bot.main"]