# Quickstart: Разработка микросервисов TODO и ShortURL

## Prerequisites

- Docker
- uv (для локальной разработки без Docker)
- Python 3.14 (optional, для локальной разработки)

## Running with Docker (Recommended)

1. **Build Images**:
   ```bash
   docker build -t todo-app ./todo_app
   docker build -t shorturl-app ./shorturl_app
   ```

2. **Create Data Volume**:
   ```bash
   docker volume create todo_data
   docker volume create shorturl_data
   ```

3. **Run TODO Service**:
   ```bash
   docker run -d -p 8001:80 -v todo_data:/app/data --name todo-service todo-app
   ```
   Access at: http://localhost:8001

4. **Run ShortURL Service**:
   ```bash
   docker run -d -p 8002:80 -v shorturl_data:/app/data --name shorturl-service shorturl-app
   ```
   Access at: http://localhost:8002

## Local Development (No Docker)

Для локальной разработки требуется установленный `uv`:

```bash
# Установка uv (если еще не установлен)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

1. **TODO Service**:
   ```bash
   cd todo_app
   uv sync
   uv run uvicorn main:app --reload --port 8001
   ```

2. **ShortURL Service**:
   ```bash
   cd shorturl_app
   uv sync
   uv run uvicorn main:app --reload --port 8002
   ```

## Testing

```bash
# Run all tests
pytest tests/
```
