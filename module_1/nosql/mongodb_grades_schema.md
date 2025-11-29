# MongoDB Схема для учёта оценок студентов

## Обзор системы

Система управления оценками включает 4 основные коллекции для работы студентов, преподавателей и деканата.

---

## Коллекции и структура данных

### 1. Students (Студенты)

```json
{
  "_id": ObjectId,
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

**Описание полей:**
- `studentId` — уникальный номер студента
- `fullName` — ФИО студента
- `email` — электронная почта
- `phone` — номер телефона
- `program` — направление обучения
- `course` — курс обучения (1-6)
- `enrollmentDate` — дата поступления
- `status` — статус (active, inactive, graduated, expelled)
- `group` — номер учебной группы

---

### 2. Teachers (Преподаватели)

```json
{
  "_id": ObjectId,
  "teacherId": "ПРЕ-2024-001",
  "fullName": "Петров Петр Петрович",
  "email": "petrov@university.ru",
  "department": "Информатика",
  "position": "Доцент",
  "phone": "+7-999-987-6543",
  "specialization": ["Базы данных", "Программирование"]
}
```

**Описание полей:**
- `teacherId` — уникальный номер преподавателя
- `fullName` — ФИО преподавателя
- `email` — электронная почта
- `department` — кафедра
- `position` — должность (Профессор, Доцент, Ассистент)
- `phone` — номер телефона
- `specialization` — список специализаций

---

### 3. Courses (Курсы)

```json
{
  "_id": ObjectId,
  "courseCode": "BD-2024-001",
  "courseName": "Базы данных",
  "description": "Введение в системы управления базами данных",
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

**Описание полей:**
- `courseCode` — код дисциплины
- `courseName` — название курса
- `description` — описание курса
- `department` — кафедра, ведущая курс
- `credits` — количество кредитов (ECTS)
- `semester` — семестр
- `hours` — общее количество часов
- `teacherId` — ID преподавателя
- `startDate` — дата начала
- `endDate` — дата окончания
- `maxStudents` — максимальное количество студентов

---

### 4. Grades (Оценки)

```json
{
  "_id": ObjectId,
  "studentId": ObjectId("..."),
  "courseId": ObjectId("..."),
  "grade": 4.5,
  "gradeType": "экзамен",
  "gradeDate": ISODate("2024-12-15"),
  "notes": "Хорошо решена практическая часть",
  "status": "final",
  "teacher": ObjectId("...")
}
```

**Описание полей:**
- `studentId` — ID студента
- `courseId` — ID курса
- `grade` — оценка (1-5 или по 100-балльной шкале)
- `gradeType` — тип оценки (экзамен, зачёт, контрольная, практика)
- `gradeDate` — дата выставления оценки
- `notes` — комментарии преподавателя
- `status` — статус (draft, interim, final)
- `teacher` — ID преподавателя, выставившего оценку

---

## Индексы для оптимизации

```javascript
// Students
db.students.createIndex({ "studentId": 1 })
db.students.createIndex({ "email": 1 })
db.students.createIndex({ "group": 1 })

// Teachers
db.teachers.createIndex({ "teacherId": 1 })
db.teachers.createIndex({ "email": 1 })

// Courses
db.courses.createIndex({ "courseCode": 1 })
db.courses.createIndex({ "semester": 1 })
db.courses.createIndex({ "teacherId": 1 })

// Grades
db.grades.createIndex({ "studentId": 1 })
db.grades.createIndex({ "courseId": 1 })
db.grades.createIndex({ "studentId": 1, "courseId": 1 })
db.grades.createIndex({ "gradeDate": 1 })
```

---

## Примеры запросов для разных ролей

### Студент: Посмотреть свои оценки

```javascript
db.grades.aggregate([
  {
    $match: {
      studentId: ObjectId("студент_id")
    }
  },
  {
    $lookup: {
      from: "courses",
      localField: "courseId",
      foreignField: "_id",
      as: "course"
    }
  },
  {
    $unwind: "$course"
  },
  {
    $project: {
      courseName: "$course.courseName",
      grade: 1,
      gradeType: 1,
      gradeDate: 1
    }
  }
])
```

### Преподаватель: Выставить оценку студентам

```javascript
db.grades.insertOne({
  studentId: ObjectId("студент_id"),
  courseId: ObjectId("курс_id"),
  grade: 4,
  gradeType: "экзамен",
  gradeDate: new Date(),
  notes: "Хорошее решение",
  status: "final",
  teacher: ObjectId("преподаватель_id")
})
```

### Деканат: Посмотреть рейтинг студентов по курсу

```javascript
db.grades.aggregate([
  {
    $match: {
      courseId: ObjectId("курс_id"),
      status: "final"
    }
  },
  {
    $lookup: {
      from: "students",
      localField: "studentId",
      foreignField: "_id",
      as: "student"
    }
  },
  {
    $unwind: "$student"
  },
  {
    $sort: { grade: -1 }
  },
  {
    $project: {
      studentName: "$student.fullName",
      grade: 1
    }
  }
])
```

### Деканат: Средняя оценка студента

```javascript
db.grades.aggregate([
  {
    $match: {
      studentId: ObjectId("студент_id"),
      status: "final"
    }
  },
  {
    $group: {
      _id: "$studentId",
      avgGrade: { $avg: "$grade" },
      courseCount: { $sum: 1 }
    }
  }
])
```

---

## Рекомендации

- **Безопасность**: используйте роли MongoDB для разделения доступа (студенты видят только свои оценки, преподаватели — оценки своих курсов)
- **Валидация**: добавьте JSON Schema для проверки типов данных
- **Архивирование**: периодически архивируйте старые оценки
- **Резервные копии**: регулярно делайте резервные копии БД
