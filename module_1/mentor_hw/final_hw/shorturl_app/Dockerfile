FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app

# Включить компиляцию байт-кода
ENV UV_COMPILE_BYTECODE=1

# Копировать из кэша вместо создания символических ссылок (учёт монтируемого тома)
ENV UV_LINK_MODE=copy

# Установить зависимости
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Скопировать проект в поддиректорию, чтобы получить пакет python
COPY . ./shorturl_app

# Установить сам проект в окружение
RUN uv sync --frozen --no-dev

# Добавить исполняемые файлы окружения в начало PATH
ENV PATH="/app/.venv/bin:$PATH"

# Сбросить entrypoint: не запускать `uv` как точку входа
ENTRYPOINT []

# Запустить приложение
CMD ["uvicorn", "shorturl_app.main:app", "--host", "0.0.0.0", "--port", "8001"]
