# Используем официальный Python образ
FROM python:3.11

ENV PYTHONUNBUFFERED=1

# Устанавливаем и запускаем CRON
RUN apt-get update && apt-get install -y cron

# Устанавливаем Poetry
RUN pip install --upgrade pip "poetry==1.8.3"
RUN poetry config virtualenvs.create false

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем pyproject.toml и poetry.lock и устанавливаем зависимости
COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

# Устанавливаем зависимости проекта
RUN poetry install --no-root

# Копируем исходный код
COPY . /app/

# Выполняем миграции, добавляем CRON задачи и запускаем приложение
CMD ["bash", "-c", "python manage.py migrate && cron && python manage.py crontab add && python manage.py runserver 0.0.0.0:8877"]
