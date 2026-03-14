import json

from typer.testing import CliRunner

from nosql_app.cli import app


runner = CliRunner()


def test_students_list_command_outputs_json(test_database):
    result = runner.invoke(app, ["students", "list", "--limit", "5"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload[0]["studentId"] == "STU-TEST-001"


def test_reports_student_average_command_outputs_json(test_database):
    result = runner.invoke(app, ["reports", "student-average", "--student-id", "STU-TEST-001"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["avgGrade"] == 4.5


def test_grades_add_command_inserts_grade(test_database):
    test_database.courses.insert_one(
        {
            "courseCode": "COURSE-TEST-003",
            "courseName": "Третья дисциплина",
            "department": "Информатика",
            "credits": 3,
            "semester": 5,
            "hours": 32,
            "teacherId": test_database.teachers.find_one({})["_id"],
            "startDate": test_database.courses.find_one({})["startDate"],
            "endDate": test_database.courses.find_one({})["endDate"],
            "maxStudents": 20,
        }
    )

    result = runner.invoke(
        app,
        [
            "grades",
            "add",
            "--student-id",
            "STU-TEST-001",
            "--course-id",
            "COURSE-TEST-003",
            "--grade",
            "5",
            "--grade-type",
            "экзамен",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["grade"] == 5.0
