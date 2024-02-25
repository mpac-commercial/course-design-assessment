from pydantic import BaseModel
from .course import CourseView



class AssignmentBase(BaseModel):
    course_id: int
    name: str



class AssignmentCreate(AssignmentBase):
    pass



class AssignmentView:
    assignment_id: int
    course_instance: CourseView
    name: str
