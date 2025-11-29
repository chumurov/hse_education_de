# Локальная MongoDB (локальное развёртывание через Docker)

Это минимальная конфигурация для запуска MongoDB локально в контейнере Docker и примеры подключения.

## Что добавлено

- `docker-compose.yml` — служба `mongodb` с монтированными томами и healthcheck.
- `mongo-init/init.js` — скрипт инициализации, создаёт пользователя приложения и опционально добавляет тестовые данные.
- `scripts/` — удобные скрипты:
  - `start.sh` — поднять контейнер (создаёт `.env`, если его нет)
  - `stop.sh` — остановить контейнер
  - `reset.sh` — сброс данных (удаляет `./data` и запускает контейнер заново)
  - `connect.sh` — подключиться к MongoDB внутри контейнера с `mongosh`

## Быстрый запуск

1) Убедитесь, что у вас установлен Docker (и docker compose в v2):

```bash
docker --version
docker compose version
```

2) Запустите MongoDB:

```bash
cd module_1/nosql
./scripts/start.sh
```

3) Подключение:

- Через `mongosh` внутри контейнера (подходит если у вас нет mongosh локально):

```bash
./scripts/connect.sh
```

- Локальный `mongosh` (если он у вас установлен):

```bash
# подключение к контейнеру через порт
mongosh "mongodb://root:example@localhost:27017/admin"
# подключение как app user к базе appdb:
mongosh "mongodb://appuser:apppassword@localhost:27017/appdb"
```

4) Остановить контейнер:

```bash
./scripts/stop.sh
```

5) Сброс данных (удалит ./data):

```bash
./scripts/reset.sh
```

## Заполнение тестовыми данными

Если вы хотите заполнить базу дополнительными тестовыми данными (несколько студентов, курсов и оценок), используйте seeder:

```bash
# Запустить только если MongoDB уже поднят:
./scripts/seed.sh

# Если хотите принудительно пересоздать данные (удалит и заново создаст коллекции):
FORCE_SEED=true ./scripts/seed.sh
```

Скрипт `mongo-init/02_seed.js` вставит набор преподавателей, курсов, студентов и оценок и выведет итоговые счёты.

---

## Типовые запросы и примеры вывода

Ниже приведены 10 типовых запросов для работы с этой схемой, короткое описание и пример вывода (до 5 строк). Используйте `mongosh` для запуска запросов или выполняйте через `docker exec nosql_mongo mongosh ...`.

1) Посмотреть все оценки студента с названиями курсов

Запрос:
```javascript
// заменить STUDENT_OBJECT_ID на ObjectId студента
const sid = ObjectId('692ad9e9518463d588ce5f54');
db.getSiblingDB('appdb').grades.aggregate([
  { $match: { studentId: sid } },
  { $lookup: { from: 'courses', localField: 'courseId', foreignField: '_id', as: 'course' } },
  { $unwind: '$course' },
  { $project: { courseName: '$course.courseName', grade: 1, gradeType: 1, gradeDate: 1 } },
  { $sort: { gradeDate: -1 } },
  { $limit: 5 }
])
```

Пример вывода (5 строк):
```
{ _id: ObjectId('...'), grade: 1.3, gradeType: 'контрольная', gradeDate: ISODate('...'), courseName: 'Курс 8 (COURSE-2025-008)' }
{ _id: ObjectId('...'), grade: 4.4, gradeType: 'экзамен', gradeDate: ISODate('...'), courseName: 'Курс 4 (COURSE-2025-004)' }
{ _id: ObjectId('...'), grade: 4.6, gradeType: 'экзамен', gradeDate: ISODate('...'), courseName: 'Курс 2 (COURSE-2025-002)' }
{ _id: ObjectId('...'), grade: 3.3, gradeType: 'зачёт', gradeDate: ISODate('...'), courseName: 'Курс 3 (COURSE-2025-003)' }
```

2) Средняя оценка студента (финальные оценки)

Запрос:
```javascript
const sid = ObjectId('692ad9e9518463d588ce5f54');
db.getSiblingDB('appdb').grades.aggregate([
  { $match: { studentId: sid, status: 'final' } },
  { $group: { _id: '$studentId', avgGrade: { $avg: '$grade' }, courses: { $sum: 1 } } }
])
```

Пример вывода:
```
{ _id: ObjectId('...'), avgGrade: 3.0666666666666664, courses: 3 }
```

3) Все студенты по курсу преподавателя с их оценками (для преподавателя)

Запрос:
```javascript
const tid = ObjectId('692ad9e9518463d588ce5f47');
db.getSiblingDB('appdb').courses.aggregate([
  { $match: { teacherId: tid } },
  { $lookup: { from: 'grades', localField: '_id', foreignField: 'courseId', as: 'grades' } },
  { $unwind: { path: '$grades', preserveNullAndEmptyArrays: true } },
  { $lookup: { from: 'students', localField: 'grades.studentId', foreignField: '_id', as: 'student' } },
  { $unwind: { path: '$student', preserveNullAndEmptyArrays: true } },
  { $project: { courseCode: 1, courseName: 1, 'student.studentId': 1, 'student.fullName': 1, 'grades.grade': 1 } },
  { $limit: 5 }
])
```

Пример вывода:
```
{ _id: ObjectId('...'), courseCode: 'COURSE-2025-001', courseName: 'Курс 1 (COURSE-2025-001)', grades: { grade: 4.2 }, student: { studentId: 'STU-2024-002', fullName: 'Петров Иван Андреевич' } }
{ _id: ObjectId('...'), courseCode: 'COURSE-2025-001', courseName: 'Курс 1 (COURSE-2025-001)', grades: { grade: 1.5 }, student: { studentId: 'STU-2024-009', fullName: 'Новикова Наталья Петрович' } }
{ _id: ObjectId('...'), courseCode: 'COURSE-2025-001', courseName: 'Курс 1 (COURSE-2025-001)', grades: { grade: 2.4 }, student: { studentId: 'STU-2024-010', fullName: 'Смирнов Елена Ивановна' } }
{ _id: ObjectId('...'), courseCode: 'COURSE-2025-001', courseName: 'Курс 1 (COURSE-2025-001)', grades: { grade: 1.9 }, student: { studentId: 'STU-2024-011', fullName: 'Леонова Андрей Андреевич' } }
{ _id: ObjectId('...'), courseCode: 'COURSE-2025-001', courseName: 'Курс 1 (COURSE-2025-001)', grades: { grade: 4.7 }, student: { studentId: 'STU-2024-013', fullName: 'Новикова Сергей Петрович' } }
```

4) Рейтинг (топ) студентов по курсу

Запрос:
```javascript
const cid = ObjectId('692ad9e9518463d588ce5f4c');
db.getSiblingDB('appdb').grades.aggregate([
  { $match: { courseId: cid, status: 'final' } },
  { $group: { _id: '$studentId', avgGrade: { $avg: '$grade' } } },
  { $lookup: { from: 'students', localField: '_id', foreignField: '_id', as: 'student' } },
  { $unwind: '$student' },
  { $project: { studentId: '$student.studentId', studentName: '$student.fullName', avgGrade: 1 } },
  { $sort: { avgGrade: -1 } },
  { $limit: 5 }
])
```

Пример вывода:
```
{ _id: ObjectId('...'), avgGrade: 4.8, studentId: 'STU-2024-049', studentName: 'Кузнецов Наталья Иванович' }
{ _id: ObjectId('...'), avgGrade: 4.7, studentId: 'STU-2024-034', studentName: 'Кузнецов Иван Петровна' }
{ _id: ObjectId('...'), avgGrade: 4.7, studentId: 'STU-2024-013', studentName: 'Новикова Сергей Петрович' }
{ _id: ObjectId('...'), avgGrade: 4.4, studentId: 'STU-2024-027', studentName: 'Попова Мария Андреевич' }
{ _id: ObjectId('...'), avgGrade: 4.2, studentId: 'STU-2024-002', studentName: 'Петров Иван Андреевич' }
```

5) Топ студентов по средней оценке по всем курсам

Запрос:
```javascript
db.getSiblingDB('appdb').grades.aggregate([
  { $match: { status: 'final' } },
  { $group: { _id: '$studentId', avgGrade: { $avg: '$grade' } } },
  { $lookup: { from: 'students', localField: '_id', foreignField: '_id', as: 'student' } },
  { $unwind: '$student' },
  { $project: { studentId: '$student.studentId', studentName: '$student.fullName', avgGrade: 1 } },
  { $sort: { avgGrade: -1 } },
  { $limit: 5 }
])
```

Пример вывода:
```
{ _id: ObjectId('...'), avgGrade: 4.8, studentId: 'STU-2024-015', studentName: 'Новикова Иван Алексеевич' }
{ _id: ObjectId('...'), avgGrade: 4.6, studentId: 'STU-2024-036', studentName: 'Кузнецов Ольга Сергеевич' }
{ _id: ObjectId('...'), avgGrade: 4.5, studentId: 'STU-2024-049', studentName: 'Кузнецов Наталья Иванович' }
{ _id: ObjectId('...'), avgGrade: 4.35, studentId: 'STU-2024-016', studentName: 'Петров Мария Петрович' }
{ _id: ObjectId('...'), avgGrade: 4.35, studentId: 'STU-2024-022', studentName: 'Петров Елена Алексеевич' }
```

6) Студенты с низкой средней (на пересдачи / в академическом риске)

Запрос:
```javascript
db.getSiblingDB('appdb').grades.aggregate([
  { $match: { status: 'final' } },
  { $group: { _id: '$studentId', avgGrade: { $avg: '$grade' } } },
  { $match: { avgGrade: { $lt: 2.5 } } },
  { $lookup: { from: 'students', localField: '_id', foreignField: '_id', as: 'student' } },
  { $unwind: '$student' },
  { $project: { studentId: '$student.studentId', studentName: '$student.fullName', avgGrade: 1 } },
  { $limit: 5 }
])
```

Пример вывода:
```
{ _id: ObjectId('...'), avgGrade: 2.1, studentId: 'STU-2024-023', studentName: 'Волкова Петр Петровна' }
{ _id: ObjectId('...'), avgGrade: 2, studentId: 'STU-2024-042', studentName: 'Кузнецов Ольга Алексеевич' }
{ _id: ObjectId('...'), avgGrade: 2.4667, studentId: 'STU-2024-009', studentName: 'Новикова Наталья Петрович' }
{ _id: ObjectId('...'), avgGrade: 1.2, studentId: 'STU-2024-005', studentName: 'Сидоров Алексей Сергеевич' }
{ _id: ObjectId('...'), avgGrade: 2.4, studentId: 'STU-2024-038', studentName: 'Кузнецов Ольга Андреевич' }
```

7) Распределение оценок по курсу (bucket по целой части оценки)

Запрос:
```javascript
const cid = ObjectId('692ad9e9518463d588ce5f4c');
db.getSiblingDB('appdb').grades.aggregate([
  { $match: { courseId: cid, status: 'final' } },
  { $project: { grade: 1, bucket: { $floor: '$grade' } } },
  { $group: { _id: '$bucket', count: { $sum: 1 } } },
  { $sort: { _id: -1 } }
])
```

Пример вывода:
```
{ _id: 4, count: 5 }
{ _id: 3, count: 5 }
{ _id: 2, count: 7 }
{ _id: 1, count: 3 }
```

8) Курсы преподавателя и число зачисленных студентов

Запрос:
```javascript
const tid = ObjectId('692ad9e9518463d588ce5f47');
db.getSiblingDB('appdb').courses.aggregate([
  { $match: { teacherId: tid } },
  { $lookup: { from: 'grades', localField: '_id', foreignField: 'courseId', as: 'grades' } },
  { $project: { courseCode: 1, courseName: 1, enrolled: { $size: { $ifNull: [ { $setUnion: [ { $map: { input: '$grades', as: 'g', in: '$$g.studentId' } } , [] ] } , [] ] } } } },
  { $limit: 5 }
])
```

Пример вывода:
```
{ _id: ObjectId('...'), courseCode: 'COURSE-2025-001', courseName: 'Курс 1 (COURSE-2025-001)', enrolled: 1 }
{ _id: ObjectId('...'), courseCode: 'COURSE-2025-006', courseName: 'Курс 6 (COURSE-2025-006)', enrolled: 1 }
```

9) Число активных студентов по группам

Запрос:
```javascript
db.getSiblingDB('appdb').students.aggregate([
  { $match: { status: 'active' } },
  { $group: { _id: '$group', count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 5 }
])
```

Пример вывода:
```
{ _id: 'БО-2-2', count: 10 }
{ _id: 'БО-1-2', count: 10 }
{ _id: 'БО-3-1', count: 10 }
{ _id: 'БО-1-1', count: 10 }
{ _id: 'БО-2-1', count: 10 }
```

10) Новые оценки за последние 7 дней (мониторинг)

Запрос:
```javascript
const since = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
db.getSiblingDB('appdb').grades.aggregate([
  { $match: { gradeDate: { $gte: since } } },
  { $lookup: { from: 'students', localField: 'studentId', foreignField: '_id', as: 'student' } },
  { $unwind: '$student' },
  { $lookup: { from: 'courses', localField: 'courseId', foreignField: '_id', as: 'course' } },
  { $unwind: '$course' },
  { $project: { studentId: '$student.studentId', studentName: '$student.fullName', courseName: '$course.courseName', grade: 1, gradeDate: 1 } },
  { $sort: { gradeDate: -1 } },
  { $limit: 5 }
])
```

Пример вывода:
```
{ _id: ObjectId('...'), grade: 3, gradeType: 'экзамен', gradeDate: ISODate('...'), studentId: 'STU-2024-050', studentName: 'Леонова Иван Сергеевич', courseName: 'Курс 6 (COURSE-2025-006)' }
{ _id: ObjectId('...'), grade: 3, gradeType: 'зачёт', gradeDate: ISODate('...'), studentId: 'STU-2024-050', studentName: 'Леонова Иван Сергеевич', courseName: 'Курс 7 (COURSE-2025-007)' }
{ _id: ObjectId('...'), grade: 3.8, gradeType: 'экзамен', gradeDate: ISODate('...'), studentId: 'STU-2024-050', studentName: 'Леонова Иван Сергеевич', courseName: 'Курс 4 (COURSE-2025-004)' }
{ _id: ObjectId('...'), grade: 4.8, gradeType: 'контрольная', gradeDate: ISODate('...'), studentId: 'STU-2024-049', studentName: 'Кузнецов Наталья Иванович', courseName: 'Курс 1 (COURSE-2025-001)' }
{ _id: ObjectId('...'), grade: 4.2, gradeType: 'экзамен', gradeDate: ISODate('...'), studentId: 'STU-2024-049', studentName: 'Кузнецов Наталья Иванович', courseName: 'Курс 7 (COURSE-2025-007)' }
```

---

Эти примеры можно адаптировать под ваши реальные Id/поля, добавить фильтры по семестру, кафедре или типу оценки и т.д. Если хотите, могу добавить версии запроса в виде коротких shell-команд для запуска в `mongosh` или через `docker exec`.


## Примечания безопасности

- Данные в `.env` хранятся в корне репозитория для удобства разработки — **не храните** реальные пароли в этом файле при публикации в Git.
- Для production используйте секреты Docker или внешние менеджеры секретов.

## Дополнительно

- Для создания дополнительного набора данных можно расширить `mongo-init/init.js`.
- Если вы используете MongoDB в приложении, добавьте строку подключения в переменные среды вашего приложения, например `MONGO_URI=mongodb://appuser:apppassword@localhost:27017/appdb`.
