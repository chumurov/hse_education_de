---
description: "Task list for FastAPI Microservices (TODO & ShortURL)"
---

# Tasks: Разработка микросервисов TODO и ShortURL

**Input**: Design documents from `/specs/001-fastapi-microservices/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/

**Tests**: Unit and Integration tests are **REQUIRED** for P1 stories (Constitution: Test-First).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel
- **[Story]**: [US1] (TODO), [US2] (ShortURL), [US3] (Docker)

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize project structure and dependencies using `uv`.

- [ ] T001 Create project directories (`todo_app`, `shorturl_app`, `tests`)
- [ ] T002 Initialize `todo_app` with `uv init` and add dependencies (`fastapi`, `uvicorn`, `jinja2`, `aiosqlite`, `pydantic`)
- [ ] T003 Initialize `shorturl_app` with `uv init` and add dependencies (`fastapi`, `uvicorn`, `jinja2`, `aiosqlite`, `pydantic`, `nanoid`)
- [ ] T004 Create root `.gitignore` (python, docker, coverage, uv)
- [ ] T005 [P] Configure `pytest` in `pyproject.toml` (or root config) for both services

---

## Phase 2: Foundational (Shared Logic & DB)

**Purpose**: Setup database connection logic for both services.

- [ ] T006 [P] [US1] Implement database connection manager (aiosqlite) in `todo_app/database.py`
- [ ] T007 [P] [US2] Implement database connection manager (aiosqlite) in `shorturl_app/database.py`

---

## Phase 3: User Story 1 - TODO Service (Priority: P1)

**Goal**: Create a task management service with API and UI.
**Test Requirement**: TDD - Write tests before implementation.

### Tests (TDD)
- [ ] T008 [US1] Create unit tests for Task CRUD logic in `tests/todo/unit/test_logic.py` (Expect Fail)
- [ ] T009 [US1] Create integration tests for TODO API endpoints in `tests/todo/integration/test_api.py` (Expect Fail)

### Implementation
- [ ] T010 [US1] Implement Task Pydantic models and DB schema in `todo_app/models.py`
- [ ] T011 [US1] Implement CRUD endpoints (GET, POST, PUT, DELETE) in `todo_app/main.py`
- [ ] T012 [US1] Implement simple HTML interface in `todo_app/templates/index.html`
- [ ] T013 [US1] Mount static/templates and connect UI in `todo_app/main.py`
- [ ] T014 [US1] Verify all tests pass

---

## Phase 4: User Story 2 - ShortURL Service (Priority: P1)

**Goal**: Create a URL shortening service with API and UI.
**Test Requirement**: TDD - Write tests before implementation.

### Tests (TDD)
- [ ] T015 [US2] Create unit tests for ShortID generation and DB logic in `tests/shorturl/unit/test_logic.py` (Expect Fail)
- [ ] T016 [US2] Create integration tests for Shorten/Redirect API in `tests/shorturl/integration/test_api.py` (Expect Fail)

### Implementation
- [ ] T017 [US2] Implement URLMapping Pydantic models and DB schema in `shorturl_app/models.py`
- [ ] T018 [US2] Implement Shorten, Redirect, and Stats endpoints in `shorturl_app/main.py`
- [ ] T019 [US2] Implement simple HTML interface in `shorturl_app/templates/index.html`
- [ ] T020 [US2] Mount static/templates and connect UI in `shorturl_app/main.py`
- [ ] T021 [US2] Verify all tests pass

---

## Phase 5: User Story 3 - Docker & Deployment (Priority: P1)

**Goal**: Containerize both services.

- [ ] T022 [P] [US3] Create `todo_app/Dockerfile` (multi-stage or slim, using uv)
- [ ] T023 [P] [US3] Create `shorturl_app/Dockerfile` (multi-stage or slim, using uv)
- [ ] T024 [US3] Create `README.md` with `docker run` instructions (including volume creation)
- [ ] T025 [US3] Manual verification: Build and run containers, check persistence

---

## Phase 6: Polish

- [ ] T026 Run linters (ruff/flake8) and formatters (black/ruff) on all code
- [ ] T027 Final review of `README.md` against requirements

## Dependencies & Execution Order

1. **Setup** (Phase 1) must be done first.
2. **Foundational** (Phase 2) can be done in parallel for each app.
3. **US1** and **US2** are independent and can be developed in parallel.
4. **US3** (Docker) depends on the respective app being runnable (at least `main.py` and `pyproject.toml` exist), but can be drafted early.

## Implementation Strategy

1. Initialize both projects with `uv`.
2. Implement TODO Service (TDD -> Code -> UI).
3. Implement ShortURL Service (TDD -> Code -> UI).
4. Add Dockerfiles.
5. Verify.
