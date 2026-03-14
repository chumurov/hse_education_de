# Итоговое задание модуль 3: MongoDB шардинг, Python CLI и нагрузочное тестирование

## 1. Описание проекта

Проект моделирует систему учёта успеваемости студентов университета на MongoDB. Система хранит информацию о студентах, преподавателях, учебных курсах и выставленных оценках.

В рамках доработки под модуль 3 были реализованы:

- sharded cluster MongoDB для горизонтального масштабирования;
- консольный интерфейс на Python;
- нагрузочное тестирование standalone и sharded конфигураций;
- запуск и управление Python-частью через `uv`.

## 2. Схема базы данных

В базе используются 4 основные коллекции: `students`, `teachers`, `courses`, `grades`.

### 2.1. Коллекция `students`

Коллекция хранит профиль студента и используется как справочник для агрегаций по оценкам.

Основные поля:

- `studentId`: человекочитаемый идентификатор студента;
- `fullName`: ФИО;
- `email`, `phone`: контакты;
- `program`: образовательная программа;
- `course`: текущий курс обучения;
- `enrollmentDate`: дата поступления;
- `status`: статус обучения;
- `group`: учебная группа.

Индексы:

- уникальный индекс по `studentId`;
- индекс по `email`;
- индекс по `group`.

### 2.2. Коллекция `teachers`

Коллекция описывает преподавателей и связывается с курсами и выставленными оценками.

Основные поля:

- `teacherId`: человекочитаемый идентификатор преподавателя;
- `fullName`: ФИО;
- `email`, `phone`: контакты;
- `department`: кафедра;
- `position`: должность;
- `specialization`: список предметных специализаций.

Индексы:

- уникальный индекс по `teacherId`;
- индекс по `email`.

### 2.3. Коллекция `courses`

Коллекция хранит учебные дисциплины и привязку к преподавателю.

Основные поля:

- `courseCode`: код курса;
- `courseName`: название;
- `description`: описание курса;
- `department`: кафедра;
- `credits`: число кредитов;
- `semester`: семестр;
- `hours`: количество часов;
- `teacherId`: ссылка на преподавателя;
- `startDate`, `endDate`: даты проведения;
- `maxStudents`: ограничение по количеству студентов.

Индексы:

- уникальный индекс по `courseCode`;
- индекс по `semester`;
- индекс по `teacherId`.

### 2.4. Коллекция `grades`

Это основная фактовая коллекция, которая растёт быстрее остальных и поэтому выбрана для шардирования.

Основные поля:

- `studentId`: ссылка на студента;
- `courseId`: ссылка на курс;
- `grade`: числовая оценка;
- `gradeType`: тип оценки;
- `gradeDate`: дата выставления;
- `notes`: комментарий преподавателя;
- `status`: статус оценки;
- `teacher`: преподаватель, который поставил оценку.

Индексы:

- индекс по `studentId`;
- индекс по `courseId`;
- уникальный составной индекс по `studentId + courseId`;
- индекс по `gradeDate`.

### 2.5. Почему схема разбита именно так

Справочники `students`, `teachers` и `courses` хранят относительно стабильные сущности, а `grades` хранит событийные записи и участвует почти во всех пользовательских сценариях:

- просмотр оценок студента;
- вычисление средней оценки;
- рейтинг студентов по курсу;
- нагрузочные read/write сценарии.

Именно поэтому `grades` отделена от справочников и шардируется отдельно.

## 3. Реализация шардинга

Добавлен отдельный локальный sharded cluster в Docker Compose:

- `cfgRS`: три config server узла;
- `shard1RS`: первый shard;
- `shard2RS`: второй shard;
- `mongos`: router для клиентских подключений.

Коллекция `grades` шардируется по ключу:

```javascript
{ studentId: 1 }
```

Почему выбран именно этот shard key:

- большая часть прикладных запросов фильтрует оценки по студенту;
- текущий уникальный индекс `{ studentId: 1, courseId: 1 }` остаётся совместимым;
- справочники `students`, `teachers`, `courses` можно не шардировать в первой версии.

После сидирования выполняется split и move chunk, чтобы даже на небольшом учебном наборе данных `grades` реально распределялась между двумя shard’ами.

### Запуск шардированного стенда

```bash
./scripts/sharded_start.sh
./scripts/sharded_status.sh
```

URI для приложений:

```text
mongodb://localhost:27018/appdb
```

### Вывод выполненной команды `./scripts/sharded_status.sh`

Фрагмент реального вывода после запуска:

```text
shards
[
  { _id: 'shard1RS', host: 'shard1RS/shard1:27018', state: 1 },
  { _id: 'shard2RS', host: 'shard2RS/shard2:27018', state: 1 }
]
...
'appdb.grades': {
  shardKey: { studentId: 1 },
  chunkMetadata: [
    { shard: 'shard1RS', nChunks: 1 },
    { shard: 'shard2RS', nChunks: 1 }
  ]
}
```

Этот вывод подтверждает, что кластер содержит 2 shard’а, а `appdb.grades` действительно шардирована и распределена по двум chunk’ам.

## 4. Python-интерфейс

Python-приложение реализовано как CLI на `Typer`, зависимости и запуск выполняются через `uv`.

Установка зависимостей:

```bash
uv sync
```

Основные команды:

```bash
uv run nosql-cli healthcheck
uv run nosql-cli students list --limit 5
uv run nosql-cli students grades --student-id STU-2024-001
uv run nosql-cli teachers courses --teacher-id PR-2025-001
uv run nosql-cli grades add --student-id STU-2024-001 --course-id COURSE-2025-001 --grade 4.7 --grade-type экзамен
uv run nosql-cli reports top-students --course-id COURSE-2025-001
uv run nosql-cli reports student-average --student-id STU-2024-001
```

CLI по умолчанию подключается к `mongos`. Подключение можно переопределить через:

- `APP_MONGO_URI`
- `APP_MONGO_DB`

### Вывод выполненной команды `uv run nosql-cli healthcheck`

```json
{
  "$clusterTime": {
    "clusterTime": {
      "inc": 1,
      "time": 1773458571
    },
    "signature": {
      "hash": "0000000000000000000000000000000000000000",
      "keyId": 0
    }
  },
  "ok": 1.0,
  "operationTime": {
    "inc": 1,
    "time": 1773458571
  }
}
```

Этот вывод показывает, что CLI успешно подключается к `mongos` и получает ответ от MongoDB.

## 5. Standalone baseline

Для сравнения с шардированным кластером сохранён standalone стенд:

```bash
./scripts/start.sh
./scripts/apply_schema.sh
./scripts/seed.sh
```

URI для baseline:

```text
mongodb://root:example@localhost:27017/appdb?authSource=admin
```

## 6. Нагрузочное тестирование

Добавлен benchmark-скрипт на Python, запускаемый через `uv`.

Поддерживаемые сценарии:

- `student_grades`
- `student_average`
- `top_students`
- `insert_grade`

Поддерживаемые профили:

- `read-heavy`
- `mixed`
- `write-heavy`

Примеры запуска:

```bash
uv run nosql-benchmark --target-uri mongodb://localhost:27018/appdb --db-name appdb --label sharded --duration-seconds 30 --workers 8 --profile mixed
uv run nosql-benchmark --target-uri 'mongodb://root:example@localhost:27017/appdb?authSource=admin' --db-name appdb --label standalone --duration-seconds 30 --workers 8 --profile mixed
```

Для smoke-проверки были выполнены короткие двухсекундные прогоны с двумя worker’ами. Ниже приведён реальный вывод команд.

### Вывод benchmark для sharded стенда

```json
{
  "summary": {
    "insert_grade": {
      "operations": 457,
      "success_rate": 1.0,
      "avg_latency_ms": 1.562,
      "p50_ms": 1.423,
      "p95_ms": 2.464,
      "throughput_ops_sec": 228.5
    },
    "student_average": {
      "operations": 359,
      "success_rate": 1.0,
      "avg_latency_ms": 1.711,
      "p50_ms": 1.621,
      "p95_ms": 2.434,
      "throughput_ops_sec": 179.5
    },
    "student_grades": {
      "operations": 614,
      "success_rate": 1.0,
      "avg_latency_ms": 2.348,
      "p50_ms": 2.321,
      "p95_ms": 3.302,
      "throughput_ops_sec": 307.0
    },
    "top_students": {
      "operations": 374,
      "success_rate": 1.0,
      "avg_latency_ms": 3.241,
      "p50_ms": 3.083,
      "p95_ms": 4.298,
      "throughput_ops_sec": 187.0
    }
  }
}
```

### Вывод benchmark для standalone стенда

```json
{
  "summary": {
    "insert_grade": {
      "operations": 930,
      "success_rate": 1.0,
      "avg_latency_ms": 0.496,
      "p50_ms": 0.468,
      "p95_ms": 0.744,
      "throughput_ops_sec": 465.0
    },
    "student_average": {
      "operations": 779,
      "success_rate": 1.0,
      "avg_latency_ms": 1.075,
      "p50_ms": 1.037,
      "p95_ms": 1.43,
      "throughput_ops_sec": 389.5
    },
    "student_grades": {
      "operations": 1297,
      "success_rate": 1.0,
      "avg_latency_ms": 1.248,
      "p50_ms": 1.19,
      "p95_ms": 1.655,
      "throughput_ops_sec": 648.5
    },
    "top_students": {
      "operations": 715,
      "success_rate": 1.0,
      "avg_latency_ms": 1.456,
      "p50_ms": 1.395,
      "p95_ms": 1.953,
      "throughput_ops_sec": 357.5
    }
  }
}
```

### Скриншоты нагрузочного тестирования

#### Sharded cluster: latency

![Sharded latency](benchmark_results/sharded_smoke_mixed_20260314T032342Z_latency.png)

#### Sharded cluster: throughput

![Sharded throughput](benchmark_results/sharded_smoke_mixed_20260314T032342Z_throughput.png)

#### Standalone: latency

![Standalone latency](benchmark_results/standalone_smoke_mixed_20260314T032342Z_latency.png)

#### Standalone: throughput

![Standalone throughput](benchmark_results/standalone_smoke_mixed_20260314T032342Z_throughput.png)

### Выводы по нагрузочному тестированию

- в коротком smoke-тесте standalone ожидаемо быстрее, потому что нет сетевого и маршрутизирующего overhead sharded cluster;
- при этом sharded конфигурация работает корректно: все сценарии выполнились без ошибок, `success_rate = 1.0`;
- кластер действительно распределяет данные между двумя shard’ами, то есть горизонтальное масштабирование реализовано не только формально;
- для учебной задачи это подтверждает корректность архитектуры и готовность проекта к дальнейшему увеличению объёма данных.

Результаты сохраняются в `benchmark_results/`:

- `*.csv` с сырыми измерениями;
- `*.json` со сводкой;
- `*_latency.png`;
- `*_throughput.png`.

## 7. Проверка реализации

Проверка Python-кода:

```bash
APP_MONGO_URI=mongodb://localhost:27018/appdb uv run pytest
```

Реальный вывод команды:

```text
============================= test session starts ==============================
platform linux -- Python 3.13.7, pytest-9.0.2, pluggy-1.6.0
rootdir: /home/nikita/hse_education_de/module_2/nosql
configfile: pyproject.toml
testpaths: tests
collected 8 items

tests/test_cli.py ...                                                    [ 37%]
tests/test_queries.py .....                                              [100%]

============================== 8 passed in 1.70s ===============================
```

## 8. Итог

Во время локальной проверки подтверждено:

- кластер поднимается и конфигурируется автоматически;
- `appdb.grades` шардирована по `{ studentId: 1 }`;
- данные реально распределяются между двумя shard’ами;
- CLI работает через `mongos`;
- `uv run pytest` проходит успешно;
- benchmark отрабатывает и для standalone, и для sharded режима.
