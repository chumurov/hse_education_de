import pytest
# Ожидается, что эти импорты могут быть не реализованы изначально
try:
    from todo_app.models import Task, TaskCreate
except ImportError:
    Task = None
    TaskCreate = None

def test_task_create_model():
    if TaskCreate is None:
        pytest.fail("TaskCreate model not implemented")
    task = TaskCreate(title="Test Task")
    assert task.title == "Test Task"
    assert task.completed is False

def test_task_model():
    if Task is None:
        pytest.fail("Task model not implemented")
    task = Task(id=1, title="Test", completed=True)
    assert task.id == 1
    assert task.completed is True
