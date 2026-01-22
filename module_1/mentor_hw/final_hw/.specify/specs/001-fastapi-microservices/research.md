# Research: Разработка микросервисов TODO и ShortURL

**Feature**: `001-fastapi-microservices`
**Status**: Completed

## Unknowns & Decisions

### 1. Python Version for Docker
- **Question**: Is Python 3.14 available as a stable Docker image?
- **Research**: Python 3.14 is likely in alpha/beta or not released yet (current stable is 3.12/3.13).
- **Decision**: Use `python:3.14-rc-slim` if available, otherwise fallback to `python:3.13-slim` or `python:3.14.0aX-slim` if explicitly required by user. Given the prompt asks for 3.14, we will try to use a preview version or the latest available.
- **Rationale**: Strict adherence to user requirement, but with a fallback for stability.

### 2. Database Library
- **Question**: Should we use `sqlite3` (standard lib) or `aiosqlite` (async)?
- **Research**: FastAPI is async. Using blocking `sqlite3` calls in async path can block the event loop. `aiosqlite` provides async bindings.
- **Decision**: Use `aiosqlite` for database interactions.
- **Rationale**: Performance and best practices for FastAPI (async framework).

### 3. Frontend Implementation
- **Question**: How to implement "simple frontend"?
- **Research**: FastAPI has built-in support for Jinja2 templates.
- **Decision**: Use `Jinja2Templates` to render simple HTML pages served directly by FastAPI.
- **Rationale**: Keeps the service self-contained, no need for separate build step (React/Vue), meets "simple" requirement.

### 4. Short ID Generation Strategy
- **Question**: How to generate short IDs?
- **Research**: 
  - Random string (collision risk).
  - Database ID encoding (Base62).
- **Decision**: Use `nanoid` or random string of length 6-8 with retry on collision, OR Base62 encoding of auto-incrementing DB ID.
- **Rationale**: Random string is simpler for MVP and doesn't expose sequential IDs.

### 5. Docker Volume Permissions
- **Question**: How to handle SQLite file permissions in Docker volume?
- **Research**: SQLite creates journal files. The directory must be writable.
- **Decision**: Ensure the container runs as a user that has write access to `/app/data`, or run as root (simplest for MVP, though not best practice for prod). For this homework, running as default (root) in container is acceptable unless specified otherwise.
- **Rationale**: Simplicity for homework assignment.

## Best Practices Adopted

- **FastAPI**: Use `Pydantic` models for validation.
- **Package Management**: Use `uv` for faster dependency resolution and installation instead of `pip`.
- **Docker**: Use `uv` in Dockerfile for efficient layer caching and fast builds. Use `.dockerignore`.
- **Testing**: `pytest` + `httpx` `AsyncClient` for testing FastAPI endpoints.
- **Structure**: Flat structure for each microservice as requested (`main.py` at root of app folder).

## Alternatives Considered

- **SQLAlchemy**: Rejected for simplicity. Raw SQL or simple query builder with `aiosqlite` is sufficient for this scale.
- **Separate Frontend Container**: Rejected. Requirement implies "simple frontend" which usually means server-side rendering or static files served by the same app for microservices homeworks.
- **pip + requirements.txt**: Rejected in favor of `uv` for faster dependency management and modern Python tooling.

