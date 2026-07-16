FROM python:3.14-slim

WORKDIR /app

# Зависимости отдельным слоем — кэшируется, пока не меняется requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini .
COPY app ./app

# Каталог для SQLite-базы (в compose сюда монтируется том)
RUN mkdir -p /data

EXPOSE 8000

# Сначала накатываем миграции, затем запускаем сервер
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
