# Базовый образ Python
FROM python:3.10-slim

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev && \
    apt-get clean

# Установка рабочей директории
WORKDIR /app

# Копируем файлы проекта
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запуск сервиса
CMD ["python", "telegram_bot.py"]
