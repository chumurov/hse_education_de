from pydantic import BaseModel, ConfigDict

class TaskBase(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
