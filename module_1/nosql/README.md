# Отчет по проектированию базы данных MongoDB для системы учета оценок

## 1. Введение

Данный отчет описывает структуру и реализацию базы данных MongoDB для системы управления успеваемостью студентов. Система предназначена для хранения информации о студентах, преподавателях, учебных курсах и оценках.

## 2. Схема и структура данных

База данных состоит из четырех основных коллекций: `students`, `teachers`, `courses` и `grades`. Ниже приведено подробное описание каждой коллекции.

### 2.1. Коллекция Students (Студенты)

Хранит информацию о студентах университета.

**Пример документа:**
```json
{
  "_id": ObjectId("..."),
  "studentId": "БО-2024-001",
  "fullName": "Иванов Иван Иванович",
  "email": "ivan@university.ru",
  "phone": "+7-999-123-4567",
  "program": "Информатика",
  "course": 2,
  "enrollmentDate": ISODate("2023-09-01"),
  "status": "active",
  "group": "БО-2-1"
}
```

**Поля:**
- `studentId` (string): Уникальный идентификатор студента.
- `fullName` (string): ФИО студента.
- `email` (string): Контактный email.
- `phone` (string): Контактный телефон.
- `program` (string): Образовательная программа.
- `course` (int): Текущий курс обучения (1-6).
- `enrollmentDate` (date): Дата зачисления.
- `status` (string): Статус обучения (active, inactive, graduated, expelled).
- `group` (string): Учебная группа.

**Индексы:**
- `{ "studentId": 1 }` (Unique)
- `{ "email": 1 }`
- `{ "group": 1 }`

---

### 2.2. Коллекция Teachers (Преподаватели)

Хранит профили преподавательского состава.

**Пример документа:**
```json
{
  "_id": ObjectId("..."),
  "teacherId": "ПРЕ-2024-001",
  "fullName": "Петров Петр Петрович",
  "email": "petrov@university.ru",
  "department": "Информатика",
  "position": "Доцент",
  "phone": "+7-999-987-6543",
  "specialization": ["Базы данных", "Программирование"]
}
```

**Поля:**
- `teacherId` (string): Уникальный идентификатор преподавателя.
- `fullName` (string): ФИО.
- `email` (string): Email.
- `department` (string): Кафедра.
- `position` (string): Должность.
- `phone` (string): Телефон.
- `specialization` (array of strings): Список специализаций.

**Индексы:**
- `{ "teacherId": 1 }` (Unique)
- `{ "email": 1 }`

---

### 2.3. Коллекция Courses (Курсы)

Содержит информацию об учебных дисциплинах.

**Пример документа:**
```json
{
  "_id": ObjectId("..."),
  "courseCode": "BD-2024-001",
  "courseName": "Базы данных",
  "description": "Введение в СУБД",
  "department": "Информатика",
  "credits": 3,
  "semester": 4,
  "hours": 48,
  "teacherId": ObjectId("..."),
  "startDate": ISODate("2024-09-01"),
  "endDate": ISODate("2024-12-15"),
  "maxStudents": 30
}
```

**Поля:**
- `courseCode` (string): Код курса.
- `courseName` (string): Название.
- `description` (string): Описание.
- `department` (string): Кафедра.
- `credits` (int): Кредиты ECTS.
- `semester` (int): Семестр.
- `hours` (int): Часы.
- `teacherId` (ObjectId): Ссылка на преподавателя.
- `startDate`, `endDate` (date): Даты проведения.
- `maxStudents` (int): Лимит студентов.

**Индексы:**
- `{ "courseCode": 1 }` (Unique)
- `{ "semester": 1 }`
- `{ "teacherId": 1 }`

---

### 2.4. Коллекция Grades (Оценки)

Журнал успеваемости.

**Пример документа:**
```json
{
  "_id": ObjectId("..."),
  "studentId": ObjectId("..."),
  "courseId": ObjectId("..."),
  "grade": 4.5,
  "gradeType": "экзамен",
  "gradeDate": ISODate("2024-12-15"),
  "notes": "Комментарий",
  "status": "final",
  "teacher": ObjectId("...")
}
```

**Поля:**
- `studentId` (ObjectId): Ссылка на студента.
- `courseId` (ObjectId): Ссылка на курс.
- `grade` (double/int): Оценка.
- `gradeType` (string): Тип (экзамен, зачет и т.д.).
- `gradeDate` (date): Дата.
- `notes` (string): Примечания.
- `status` (string): Статус оценки (draft, final).
- `teacher` (ObjectId): Кто выставил.

**Индексы:**
- `{ "studentId": 1 }`
- `{ "courseId": 1 }`
- `{ "studentId": 1, "courseId": 1 }` (Unique - одна оценка за курс, опционально)
- `{ "gradeDate": 1 }`

---

## 3. Типовые запросы и примеры вывода

Ниже приведены примеры запросов, реализованных для данной схемы, с образцами вывода.

### 1) Посмотреть все оценки студента с названиями курсов

**Запрос:**
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

**Пример вывода:**
```
{ _id: ObjectId('...'), grade: 1.3, gradeType: 'контрольная', gradeDate: ISODate('...'), courseName: 'Курс 8 (COURSE-2025-008)' }
{ _id: ObjectId('...'), grade: 4.4, gradeType: 'экзамен', gradeDate: ISODate('...'), courseName: 'Курс 4 (COURSE-2025-004)' }
{ _id: ObjectId('...'), grade: 4.6, gradeType: 'экзамен', gradeDate: ISODate('...'), courseName: 'Курс 2 (COURSE-2025-002)' }
{ _id: ObjectId('...'), grade: 3.3, gradeType: 'зачёт', gradeDate: ISODate('...'), courseName: 'Курс 3 (COURSE-2025-003)' }
```

### 2) Средняя оценка студента (финальные оценки)

**Запрос:**
```javascript
const sid = ObjectId('692ad9e9518463d588ce5f54');
db.getSiblingDB('appdb').grades.aggregate([
  { $match: { studentId: sid, status: 'final' } },
  { $group: { _id: '$studentId', avgGrade: { $avg: '$grade' }, courses: { $sum: 1 } } }
])
```

**Пример вывода:**
```
{ _id: ObjectId('...'), avgGrade: 3.0666666666666664, courses: 3 }
```

### 3) Все студенты по курсу преподавателя с их оценками

**Запрос:**
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

**Пример вывода:**
```
{ _id: ObjectId('...'), courseCode: 'COURSE-2025-001', courseName: 'Курс 1 (COURSE-2025-001)', grades: { grade: 4.2 }, student: { studentId: 'STU-2024-002', fullName: 'Петров Иван Андреевич' } }
{ _id: ObjectId('...'), courseCode: 'COURSE-2025-001', courseName: 'Курс 1 (COURSE-2025-001)', grades: { grade: 1.5 }, student: { studentId: 'STU-2024-009', fullName: 'Новикова Наталья Петрович' } }
```

### 4) Рейтинг (топ) студентов по курсу

**Запрос:**
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

**Пример вывода:**
```
{ _id: ObjectId('...'), avgGrade: 4.8, studentId: 'STU-2024-049', studentName: 'Кузнецов Наталья Иванович' }
{ _id: ObjectId('...'), avgGrade: 4.7, studentId: 'STU-2024-034', studentName: 'Кузнецов Иван Петровна' }
```

### 5) Топ студентов по средней оценке по всем курсам

**Запрос:**
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

**Пример вывода:**
```
{ _id: ObjectId('...'), avgGrade: 4.8, studentId: 'STU-2024-015', studentName: 'Новикова Иван Алексеевич' }
{ _id: ObjectId('...'), avgGrade: 4.6, studentId: 'STU-2024-036', studentName: 'Кузнецов Ольга Сергеевич' }
```

### 6) Студенты с низкой средней (академический риск)

**Запрос:**
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

**Пример вывода:**
```
{ _id: ObjectId('...'), avgGrade: 2.1, studentId: 'STU-2024-023', studentName: 'Волкова Петр Петровна' }
{ _id: ObjectId('...'), avgGrade: 2, studentId: 'STU-2024-042', studentName: 'Кузнецов Ольга Алексеевич' }
```

### 7) Распределение оценок по курсу

**Запрос:**
```javascript
const cid = ObjectId('692ad9e9518463d588ce5f4c');
db.getSiblingDB('appdb').grades.aggregate([
  { $match: { courseId: cid, status: 'final' } },
  { $project: { grade: 1, bucket: { $floor: '$grade' } } },
  { $group: { _id: '$bucket', count: { $sum: 1 } } },
  { $sort: { _id: -1 } }
])
```

**Пример вывода:**
```
{ _id: 4, count: 5 }
{ _id: 3, count: 5 }
{ _id: 2, count: 7 }
{ _id: 1, count: 3 }
```

### 8) Курсы преподавателя и число зачисленных студентов

**Запрос:**
```javascript
const tid = ObjectId('692ad9e9518463d588ce5f47');
db.getSiblingDB('appdb').courses.aggregate([
  { $match: { teacherId: tid } },
  { $lookup: { from: 'grades', localField: '_id', foreignField: 'courseId', as: 'grades' } },
  { $project: { courseCode: 1, courseName: 1, enrolled: { $size: { $ifNull: [ { $setUnion: [ { $map: { input: '$grades', as: 'g', in: '$$g.studentId' } } , [] ] } , [] ] } } } },
  { $limit: 5 }
])
```

**Пример вывода:**
```
{ _id: ObjectId('...'), courseCode: 'COURSE-2025-001', courseName: 'Курс 1 (COURSE-2025-001)', enrolled: 1 }
{ _id: ObjectId('...'), courseCode: 'COURSE-2025-006', courseName: 'Курс 6 (COURSE-2025-006)', enrolled: 1 }
```

### 9) Число активных студентов по группам

**Запрос:**
```javascript
db.getSiblingDB('appdb').students.aggregate([
  { $match: { status: 'active' } },
  { $group: { _id: '$group', count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 5 }
])
```

**Пример вывода:**
```
{ _id: 'БО-2-2', count: 10 }
{ _id: 'БО-1-2', count: 10 }
{ _id: 'БО-3-1', count: 10 }
{ _id: 'БО-1-1', count: 10 }
{ _id: 'БО-2-1', count: 10 }
```

### 10) Новые оценки за последние 7 дней (мониторинг)

**Запрос:**
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

**Пример вывода:**
```
{ _id: ObjectId('...'), grade: 3, gradeType: 'экзамен', gradeDate: ISODate('...'), studentId: 'STU-2024-050', studentName: 'Леонова Иван Сергеевич', courseName: 'Курс 6 (COURSE-2025-006)' }
{ _id: ObjectId('...'), grade: 3, gradeType: 'зачёт', gradeDate: ISODate('...'), studentId: 'STU-2024-050', studentName: 'Леонова Иван Сергеевич', courseName: 'Курс 7 (COURSE-2025-007)' }
```
