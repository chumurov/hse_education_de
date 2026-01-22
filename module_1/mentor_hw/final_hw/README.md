# Домашнее задание: Микросервисы на FastAPI

Проект содержит два микросервиса:
1. **TODO App** — сервис управления задачами.
2. **ShortURL App** — сервис сокращения ссылок.

## Стек технологий
- Python 3.14
- FastAPI
- SQLite (асинхронная работа)
- Docker и Docker Compose
- uv (пакетный менеджер)

## Запуск через Docker

```bash
docker compose up --build
```

- TODO App: http://localhost:8000/docs
- ShortURL App: http://localhost:8001/docs

## Локальный запуск

### Требования
- Установлен `uv`: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Python 3.14

### TODO App
```bash
cd todo_app
uv sync
uv run uvicorn todo_app.main:app --reload --port 8000
```

### ShortURL App
```bash
cd shorturl_app
uv sync
uv run uvicorn shorturl_app.main:app --reload --port 8001
```

## Запуск тестов

```bash
# TODO App
uv run --project todo_app pytest tests/todo

# ShortURL App
uv run --project shorturl_app pytest tests/shorturl
```

## Ручное тестирование (curl)

### TODO App

**1. Создать задачу**
```bash
curl -X POST "http://localhost:8000/tasks/" \
     -H "Content-Type: application/json" \
     -d '{"title": "Buy groceries", "description": "Milk, Eggs, Bread"}'
```
*Ответ:*
```json
{"title":"Buy groceries","description":"Milk, Eggs, Bread","completed":false,"id":1}
```

**2. Список задач**
```bash
curl -X GET "http://localhost:8000/tasks/"
```
*Ответ:*
```json
[{"title":"Buy groceries","description":"Milk, Eggs, Bread","completed":false,"id":1}]
```

**3. Обновить задачу**
```bash
curl -X PUT "http://localhost:8000/tasks/1" \
     -H "Content-Type: application/json" \
     -d '{"title": "Buy groceries", "description": "Milk, Eggs, Bread, Cheese", "completed": true}'
```
*Ответ:*
```json
{"title":"Buy groceries","description":"Milk, Eggs, Bread, Cheese","completed":true,"id":1}
```

**4. Удалить задачу**
```bash
curl -X DELETE "http://localhost:8000/tasks/1"
```

### ShortURL App

**1. Создать короткую ссылку**
```bash
curl -X POST "http://localhost:8001/urls/" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.google.com"}'
```
*Ответ:*
```json
{"url":"https://www.google.com/","id":"LzSCnTcI"}
```

**2. Проверка редиректа**
```bash
curl -v http://localhost:8001/LzSCnTcI
```
*Ответ (заголовки):*
```http
< HTTP/1.1 307 Temporary Redirect
< location: https://www.google.com/
```
