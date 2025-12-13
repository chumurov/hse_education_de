<!--
Sync Impact Report
- Version change: TEMPLATE -> 1.0.0
- Modified principles:
	- [PRINCIPLE_1_NAME] -> I. Библиотечно-ориентированный дизайн (Library-first)
	- [PRINCIPLE_2_NAME] -> II. Интерфейс командной строки и тестируемые контракты (CLI / API)
	- [PRINCIPLE_3_NAME] -> III. Тестирование в первую очередь (TDD) — НЕПРЕКРАЩАЕМОЕ
	- [PRINCIPLE_4_NAME] -> IV. Интеграция и контрактное тестирование
	- [PRINCIPLE_5_NAME] -> V. Наблюдаемость, версияция и простота
- Added sections:
	- Ограничения и требования
	- Процесс разработки и контроль качества
- Removed sections: none
- Templates requiring updates:
	- .specify/templates/plan-template.md ✅ updated
	- .specify/templates/spec-template.md ✅ updated
	- .specify/templates/tasks-template.md ✅ updated
	- .specify/templates/agent-file-template.md ⚠ pending review
	- .github/agents/*.md ⚠ review for references/agent names
- Follow-up TODOs:
	- Verify whether `RATIFICATION_DATE` should be earlier than 2025-12-13 or kept as ratified today.
	- Confirm whether project name should be changed from the repository name to a canonical identity.
	- Review agent scripts (CLAUDE references) for any required name canonicalization.
-->

# HSE Education (DE) — Final HW Constitution
<!-- Это внутренняя конституция проекта - набор правил и руководств для разработки, релизов и управления изменениями. -->

## Core Principles

### I. Библиотечно-ориентированный дизайн (Library-first)
Все новые функции должны начинаться как автономная библиотека/модуль с чётко определённым интерфейсом. Библиотеки
должны быть самодостаточными, документированными и иметь набор юнит-тестов. Любая функциональность, нужная для
других компонентов, должна быть вынесена в библиотеку, а не размещаться в приложении напрямую.
<!-- Example: Every feature starts as a standalone library; Libraries must be self-contained, independently testable, documented; Clear purpose required - no organizational-only libraries -->

### II. Интерфейс командной строки и тестируемые контракты (CLI / API)
Библиотеки и сервисы, которые взаимодействуют с пользователем или другими системами, должны предоставлять
однозначно тестируемый интерфейс. Предпочтение отдаётся простым текстовым интерфейсам (stdin/args → stdout),
а также JSON-совместимым форматам для машинной потребности. Любые API/CLI должны иметь понятную спецификацию
и примеры использования.
<!-- Example: Every library exposes functionality via CLI; Text in/out protocol: stdin/args → stdout, errors → stderr; Support JSON + human-readable formats -->

### III. Тестирование в первую очередь (TDD) — НЕПРЕКРАЩАЕМОЕ
Тестирование — обязательный базовый уровень качества. Для новой функциональности сначала пишутся тесты, затем
реализация; цикл Red-Green-Refactor должен соблюдаться. Тесты должны быть независимы, воспроизводимы и без
жёстких внешних зависимостей (использовать моки, фикстуры, e2e/интеграционные тесты там, где необходимо).
<!-- Example: TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced -->

### IV. Интеграция и контрактное тестирование
Интеграционные тесты обязаны покрывать изменения контрактов между сервисами и библиотеками. Любая модификация
международной логики, API или контрактных форматов требует набора контрактных тестов, чтобы предотвратить
бестолковые регресии при интеграции.
<!-- Example: Focus areas requiring integration tests: New library contract tests, Contract changes, Inter-service communication, Shared schemas -->

### V. Наблюдаемость, версияция и простота
Логирование должно быть структурированным (JSON) и полезным для отладки; ошибки — информативными; телеметрия —
доступной через стандартные средства мониторинга. Версияция — по семантическому формату MAJOR.MINOR.PATCH.
Разрывающие изменения требуют MAJOR-бамп и миграционных инструкций. Проект стремится к простоте: YAGNI и KISS.
<!-- Example: Text I/O ensures debuggability; Structured logging required; Or: MAJOR.MINOR.BUILD format; Or: Start simple, YAGNI principles -->

## Ограничения и требования (Constraints & Requirements)

Технологический стек и требования к доставке должны быть минимально необходимыми и обоснованы в плане. Рекомендуемые
практики:
- Поддержка современного, поддерживаемого языка (например, Python >= 3.11, Node.js >= 18, Rust 1.70+ — по потребности);
- Строгие тесты: unit + integration для ключевых контрактов;
- CI: линтеры, форматтеры, тесты и статическая проверка на каждом PR;
- Безопасность: чувствительные данные не должны попадать в репозиторий; секреты через CI/Secrets.
<!-- Example: Technology stack requirements, compliance standards, deployment policies, etc. -->

## Процесс разработки и контроль качества (Development Workflow)

Процесс:
- Все изменения — через Pull Request (PR).
- Минимальные требования для PR: описание проблемы, изменения, тесты и `CHANGELOG`/заметка о версии если затронута публичная API.
- Code review: минимум 1 отзывчик (2 для крупных изменений). Все CI-проверки должны быть зелёными перед слиянием.
- Quality gates: линтинг, статическая проверка, unit-тесты и интеграционные тесты (если релевантно).

Требования к релизам:
- Публикация тега в формате `vMAJOR.MINOR.PATCH`.
- Для breaking change — MAJOR; для добавлений/улучшений — MINOR; для исправлений — PATCH.
<!-- Example: Code review requirements, testing gates, deployment approval process, etc. -->

## Руководство по управлению и внесению изменений (Governance)

Эта Конституция — основной набор правил для проекта. Изменения в Конституции должны выполняться через явно
задокументированный процесс:

1. Предложение изменений через PR в `.specify/memory/constitution.md` с пояснением причин.
2. В PR должно быть указано влияние на существующие спецификации, планы и задачи; если принцип меняется —
	требуется миграционный план и шаги по приведению в соответствие всех существующих артефактов.
3. Стандарт одобрения: минимум 2 рецензента (или maintainers) для несущественных изменений; существенные
	изменения (удаление принципа, изменение сути принципа) требуют консенсуса большинства коммитеров/maintainers.
4. При внесении изменений — указывайте тип bump версии Конституции: MAJOR/MINOR/PATCH согласно правилам ниже.

Политика версий Конституции
- MAJOR: удаление или фундаментальное изменение принципа, несовместимое с предыдущим поведением.
- MINOR: добавление новой принципы или значительное расширение существующих указаний.
- PATCH: формулировки, опечатки, незначительные уточнения, которые не меняют суть правил.

Все изменения в Конституции должны обновлять метаданные (строку Version/Last Amended) и Sync Impact Report.
<!-- Example: All PRs/reviews must verify compliance; Complexity must be justified; Use `.specify/templates/agent-file-template.md` for runtime development guidance -->

**Version**: 1.0.0 | **Ratified**: 2025-12-13 | **Last Amended**: 2025-12-13
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->
