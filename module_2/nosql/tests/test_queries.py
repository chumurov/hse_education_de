from nosql_app.queries import add_grade, list_students, student_average, student_grades, top_students


def test_list_students_returns_seeded_student(test_database):
    students = list_students(test_database, limit=10)
    assert len(students) == 1
    assert students[0]["studentId"] == "STU-TEST-001"


def test_student_grades_returns_joined_course(test_database):
    grades = student_grades(test_database, "STU-TEST-001", limit=10)
    assert len(grades) == 1
    assert grades[0]["courseCode"] == "COURSE-TEST-001"


def test_student_average_returns_aggregate(test_database):
    average = student_average(test_database, "STU-TEST-001")
    assert average["avgGrade"] == 4.5
    assert average["courseCount"] == 1


def test_add_grade_inserts_document(test_database):
    test_database.courses.insert_one(
        {
            "courseCode": "COURSE-TEST-002",
            "courseName": "Вторая дисциплина",
            "department": "Информатика",
            "credits": 3,
            "semester": 4,
            "hours": 48,
            "teacherId": test_database.teachers.find_one({})["_id"],
            "startDate": test_database.courses.find_one({})["startDate"],
            "endDate": test_database.courses.find_one({})["endDate"],
            "maxStudents": 30,
        }
    )

    document = add_grade(
        test_database,
        student_identifier="STU-TEST-001",
        course_identifier="COURSE-TEST-002",
        grade=4.8,
        grade_type="зачёт",
    )

    assert document["grade"] == 4.8
    assert test_database.grades.count_documents({}) == 2


def test_top_students_returns_ranked_students(test_database):
    ranking = top_students(test_database, "COURSE-TEST-001", limit=10)
    assert len(ranking) == 1
    assert ranking[0]["studentId"] == "STU-TEST-001"

