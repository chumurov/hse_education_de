from __future__ import annotations

from datetime import UTC, datetime

from bson import ObjectId
from pymongo.database import Database


class EntityNotFoundError(ValueError):
    pass


def _maybe_object_id(value: str) -> ObjectId | None:
    if ObjectId.is_valid(value):
        return ObjectId(value)
    return None


def _resolve_entity(database: Database, collection_name: str, natural_key: str, identifier: str) -> dict:
    collection = database[collection_name]
    entity = collection.find_one({natural_key: identifier})
    if entity:
        return entity

    object_id = _maybe_object_id(identifier)
    if object_id:
        entity = collection.find_one({"_id": object_id})
        if entity:
            return entity

    raise EntityNotFoundError(f"{collection_name.rstrip('s').title()} '{identifier}' was not found")


def resolve_student(database: Database, identifier: str) -> dict:
    return _resolve_entity(database, "students", "studentId", identifier)


def resolve_teacher(database: Database, identifier: str) -> dict:
    return _resolve_entity(database, "teachers", "teacherId", identifier)


def resolve_course(database: Database, identifier: str) -> dict:
    return _resolve_entity(database, "courses", "courseCode", identifier)


def list_students(database: Database, limit: int = 20) -> list[dict]:
    cursor = database.students.find(
        {},
        {
            "studentId": 1,
            "fullName": 1,
            "group": 1,
            "program": 1,
            "course": 1,
            "status": 1,
        },
    ).sort("studentId", 1).limit(limit)
    return list(cursor)


def list_courses(database: Database, limit: int = 20) -> list[dict]:
    cursor = database.courses.find(
        {},
        {
            "courseCode": 1,
            "courseName": 1,
            "semester": 1,
            "department": 1,
            "teacherId": 1,
        },
    ).sort("courseCode", 1).limit(limit)
    return list(cursor)


def student_grades(database: Database, student_identifier: str, limit: int = 20) -> list[dict]:
    student = resolve_student(database, student_identifier)
    pipeline = [
        {"$match": {"studentId": student["_id"]}},
        {"$lookup": {"from": "courses", "localField": "courseId", "foreignField": "_id", "as": "course"}},
        {"$unwind": "$course"},
        {
            "$project": {
                "_id": 1,
                "grade": 1,
                "gradeType": 1,
                "gradeDate": 1,
                "status": 1,
                "notes": 1,
                "courseCode": "$course.courseCode",
                "courseName": "$course.courseName",
                "studentId": student["studentId"],
                "studentName": student["fullName"],
            }
        },
        {"$sort": {"gradeDate": -1}},
        {"$limit": limit},
    ]
    return list(database.grades.aggregate(pipeline))


def teacher_courses(database: Database, teacher_identifier: str, limit: int = 20) -> list[dict]:
    teacher = resolve_teacher(database, teacher_identifier)
    cursor = database.courses.find({"teacherId": teacher["_id"]}).sort("courseCode", 1).limit(limit)
    return list(cursor)


def add_grade(
    database: Database,
    student_identifier: str,
    course_identifier: str,
    grade: float,
    grade_type: str,
    status: str = "final",
    notes: str | None = None,
) -> dict:
    student = resolve_student(database, student_identifier)
    course = resolve_course(database, course_identifier)

    grade_document = {
        "studentId": student["_id"],
        "courseId": course["_id"],
        "grade": float(grade),
        "gradeType": grade_type,
        "gradeDate": datetime.now(UTC),
        "status": status,
        "teacher": course["teacherId"],
    }
    if notes:
        grade_document["notes"] = notes

    result = database.grades.insert_one(grade_document)
    return database.grades.find_one({"_id": result.inserted_id})


def top_students(database: Database, course_identifier: str, limit: int = 10) -> list[dict]:
    course = resolve_course(database, course_identifier)
    pipeline = [
        {"$match": {"courseId": course["_id"], "status": "final"}},
        {"$group": {"_id": "$studentId", "avgGrade": {"$avg": "$grade"}, "attempts": {"$sum": 1}}},
        {"$lookup": {"from": "students", "localField": "_id", "foreignField": "_id", "as": "student"}},
        {"$unwind": "$student"},
        {
            "$project": {
                "_id": 0,
                "studentId": "$student.studentId",
                "studentName": "$student.fullName",
                "avgGrade": {"$round": ["$avgGrade", 2]},
                "attempts": 1,
                "courseCode": course["courseCode"],
                "courseName": course["courseName"],
            }
        },
        {"$sort": {"avgGrade": -1, "studentName": 1}},
        {"$limit": limit},
    ]
    return list(database.grades.aggregate(pipeline))


def student_average(database: Database, student_identifier: str) -> dict:
    student = resolve_student(database, student_identifier)
    pipeline = [
        {"$match": {"studentId": student["_id"], "status": "final"}},
        {"$group": {"_id": "$studentId", "avgGrade": {"$avg": "$grade"}, "courseCount": {"$sum": 1}}},
    ]
    result = next(iter(database.grades.aggregate(pipeline)), None)
    if not result:
        return {
            "studentId": student["studentId"],
            "studentName": student["fullName"],
            "avgGrade": None,
            "courseCount": 0,
        }

    return {
        "studentId": student["studentId"],
        "studentName": student["fullName"],
        "avgGrade": round(result["avgGrade"], 2),
        "courseCount": result["courseCount"],
    }

