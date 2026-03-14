from __future__ import annotations

import typer
from pymongo.errors import DuplicateKeyError, PyMongoError

from nosql_app.db import mongo_database, ping
from nosql_app.json_utils import dumps
from nosql_app.queries import (
    EntityNotFoundError,
    add_grade,
    list_courses,
    list_students,
    student_average,
    student_grades,
    teacher_courses,
    top_students,
)


app = typer.Typer(help="CLI for the university grades MongoDB project")
students_app = typer.Typer(help="Student-related commands")
teachers_app = typer.Typer(help="Teacher-related commands")
courses_app = typer.Typer(help="Course-related commands")
grades_app = typer.Typer(help="Grade management commands")
reports_app = typer.Typer(help="Report and aggregation commands")

app.add_typer(students_app, name="students")
app.add_typer(teachers_app, name="teachers")
app.add_typer(courses_app, name="courses")
app.add_typer(grades_app, name="grades")
app.add_typer(reports_app, name="reports")


def _print(data: object) -> None:
    typer.echo(dumps(data))


def _exit_with_error(message: str, exit_code: int = 1) -> None:
    typer.echo(message, err=True)
    raise typer.Exit(code=exit_code)


@app.command()
def healthcheck() -> None:
    try:
        _print(ping())
    except PyMongoError as error:
        _exit_with_error(f"MongoDB connection failed: {error}")


@students_app.command("list")
def students_list(limit: int = typer.Option(20, min=1, max=500)) -> None:
    with mongo_database() as database:
        _print(list_students(database, limit=limit))


@students_app.command("grades")
def students_grades(
    student_id: str = typer.Option(..., "--student-id"),
    limit: int = typer.Option(20, min=1, max=500),
) -> None:
    try:
        with mongo_database() as database:
            _print(student_grades(database, student_id, limit=limit))
    except EntityNotFoundError as error:
        _exit_with_error(str(error))


@teachers_app.command("courses")
def teachers_courses(
    teacher_id: str = typer.Option(..., "--teacher-id"),
    limit: int = typer.Option(20, min=1, max=500),
) -> None:
    try:
        with mongo_database() as database:
            _print(teacher_courses(database, teacher_id, limit=limit))
    except EntityNotFoundError as error:
        _exit_with_error(str(error))


@courses_app.command("list")
def courses_list(limit: int = typer.Option(20, min=1, max=500)) -> None:
    with mongo_database() as database:
        _print(list_courses(database, limit=limit))


@grades_app.command("add")
def grades_add(
    student_id: str = typer.Option(..., "--student-id"),
    course_id: str = typer.Option(..., "--course-id"),
    grade: float = typer.Option(..., "--grade", min=0.0),
    grade_type: str = typer.Option(..., "--grade-type"),
    status: str = typer.Option("final", "--status"),
    notes: str | None = typer.Option(None, "--notes"),
) -> None:
    try:
        with mongo_database() as database:
            _print(add_grade(database, student_id, course_id, grade, grade_type, status=status, notes=notes))
    except EntityNotFoundError as error:
        _exit_with_error(str(error))
    except DuplicateKeyError as error:
        _exit_with_error(f"Could not insert grade because the pair student/course must be unique: {error.details}")


@reports_app.command("top-students")
def reports_top_students(
    course_id: str = typer.Option(..., "--course-id"),
    limit: int = typer.Option(10, min=1, max=500),
) -> None:
    try:
        with mongo_database() as database:
            _print(top_students(database, course_id, limit=limit))
    except EntityNotFoundError as error:
        _exit_with_error(str(error))


@reports_app.command("student-average")
def reports_student_average(student_id: str = typer.Option(..., "--student-id")) -> None:
    try:
        with mongo_database() as database:
            _print(student_average(database, student_id))
    except EntityNotFoundError as error:
        _exit_with_error(str(error))


def run() -> None:
    app()


if __name__ == "__main__":
    run()

