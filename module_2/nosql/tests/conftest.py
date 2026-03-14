from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime

import pytest
from bson import ObjectId
from pymongo import MongoClient


@pytest.fixture()
def test_database(monkeypatch: pytest.MonkeyPatch):
    mongo_uri = os.getenv("APP_MONGO_URI", "mongodb://localhost:27018/appdb")
    database_name = f"nosql_test_{uuid.uuid4().hex}"
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)

    try:
        client.admin.command("ping")
    except Exception as error:  # noqa: BLE001
        client.close()
        pytest.skip(f"MongoDB is not available for integration tests: {error}")

    monkeypatch.setenv("APP_MONGO_URI", mongo_uri)
    monkeypatch.setenv("APP_MONGO_DB", database_name)

    database = client[database_name]
    teacher_id = ObjectId()
    course_id = ObjectId()
    student_id = ObjectId()

    database.teachers.insert_one(
        {
            "_id": teacher_id,
            "teacherId": "PR-TEST-001",
            "fullName": "Петров Петр Петрович",
            "email": "teacher@test.local",
            "department": "Информатика",
            "position": "Доцент",
        }
    )
    database.students.insert_one(
        {
            "_id": student_id,
            "studentId": "STU-TEST-001",
            "fullName": "Иванов Иван Иванович",
            "email": "student@test.local",
            "program": "Информатика",
            "course": 2,
            "enrollmentDate": datetime.now(UTC),
            "status": "active",
            "group": "БО-2-1",
        }
    )
    database.courses.insert_one(
        {
            "_id": course_id,
            "courseCode": "COURSE-TEST-001",
            "courseName": "Тестовая база данных",
            "department": "Информатика",
            "credits": 3,
            "semester": 4,
            "hours": 48,
            "teacherId": teacher_id,
            "startDate": datetime.now(UTC),
            "endDate": datetime.now(UTC),
            "maxStudents": 30,
        }
    )
    database.grades.insert_one(
        {
            "studentId": student_id,
            "courseId": course_id,
            "grade": 4.5,
            "gradeType": "экзамен",
            "gradeDate": datetime.now(UTC),
            "status": "final",
            "teacher": teacher_id,
        }
    )

    yield database

    client.drop_database(database_name)
    client.close()

