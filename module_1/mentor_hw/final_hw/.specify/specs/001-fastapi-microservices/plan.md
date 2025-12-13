# Implementation Plan: Разработка микросервисов TODO и ShortURL

**Branch**: `001-fastapi-microservices` | **Date**: 2025-12-13 | **Spec**: [.specify/specs/001-fastapi-microservices/spec.md](../spec.md)
**Input**: Feature specification from `/specs/001-fastapi-microservices/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Разработка двух микросервисов (TODO и ShortURL) на базе FastAPI и Python 3.14 с использованием SQLite для хранения данных. Оба сервиса будут контейнеризированы с помощью Docker, данные будут сохраняться в volume. Реализация включает REST API, простой веб-интерфейс и автоматическое создание таблиц БД.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.14 (или 3.13/latest stable, если 3.14 недоступен в slim образе)
**Package Manager**: uv (современный быстрый менеджер пакетов для Python)
**Primary Dependencies**: FastAPI, Uvicorn, Jinja2 (для frontend), aiosqlite (опционально) или sqlite3
**Storage**: SQLite (файлы `todo.db` и `shorturl.db` в `/app/data`)
**Testing**: pytest, httpx (для интеграционных тестов)
**Target Platform**: Docker (Linux containers), порт 80
**Project Type**: Microservices (2 independent services)
**Performance Goals**: Standard REST API performance
**Constraints**: Данные должны сохраняться при перезапуске контейнеров (Volume mapping)
**Scale/Scope**: MVP, 2 сервиса, базовый CRUD и редиректы

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Обязательные проверки, вытекающие из Конституции проекта:

- GATE 1 — Test-First: Каждая ключевая история (P1) должна иметь упавший тест до реализации (unit tests).
- GATE 2 — Library-first: Если реализуемая функциональность имеет повторно используемую логику, её первым артефактом
  должен быть модуль/библиотека с документированным API. (В данном случае сервисы самодостаточны, но общая логика может быть выделена).
- GATE 3 — Interface Contract: Любые изменения публичных интерфейсов/контрактов требуют контрактных/интеграционных тестов.
- GATE 4 — Observability: Все новые сервисы/CLI должны иметь структурированное логирование и хотя бы базовый health
  /metrics endpoint или инструкцию по мониторингу.
- GATE 5 — Versioning: При breaking changes — включить миграционный план и указать bump типа MAJOR; при добавлении
  функциональности — MINOR; при исправлении багов — PATCH.
- GATE 6 — CI/Quality: PR не может быть слит без зелёного status чек-листа (линтеры, форматтеры, тесты).

Проход этих проверок — обязательное условие перед началом разработки и для перехода между фазами плана.

## Project Structure

### Documentation (this feature)

```text
specs/001-fastapi-microservices/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
todo_app/
├── main.py              # Entry point and logic
├── pyproject.toml       # Project metadata and dependencies (uv)
├── uv.lock              # Lockfile for reproducible builds
├── Dockerfile           # Container definition
└── templates/           # HTML templates (optional)

shorturl_app/
├── main.py              # Entry point and logic
├── pyproject.toml       # Project metadata and dependencies (uv)
├── uv.lock              # Lockfile for reproducible builds
├── Dockerfile           # Container definition
└── templates/           # HTML templates (optional)

tests/
├── todo/
│   ├── unit/
│   └── integration/
└── shorturl/
    ├── unit/
    └── integration/

README.md                # Project documentation and run instructions
```

**Structure Decision**: Два независимых каталога `todo_app` и `shorturl_app` в корне репозитория, каждый со своим `Dockerfile` и `pyproject.toml` (управление зависимостями через uv), как запрошено в требованиях. Тесты вынесены в отдельную директорию `tests` или могут быть внутри приложений (решим на этапе research).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | | |
