# Простой рабочий Dockerfile без многоэтапной сборки
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    procps \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Установка Poetry
RUN pip install --no-cache-dir poetry==1.6.1

# Настройка Poetry
ENV POETRY_VENV_IN_PROJECT=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR=/opt/poetry_cache

# Создание пользователя
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Рабочая директория
WORKDIR /app

# Копирование файлов проекта
COPY pyproject.toml poetry.lock* ./
COPY README.md ./
COPY src/ ./src/
COPY main.py ./
COPY run.py ./

# Установка зависимостей
RUN poetry install --only=main && rm -rf $POETRY_CACHE_DIR

# Создание директорий
RUN mkdir -p data output logs && \
    chown -R appuser:appuser /app

# Переключение на пользователя
USER appuser

# Переменные окружения
ENV PYTHONPATH="/app" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Метаданные образа
LABEL maintainer="Amir B." \
      version="1.0.0" \
      description="Система мониторинга уборочных машин"

# Проверка здоровья
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Команда по умолчанию
CMD ["python", "main.py", "--help"]