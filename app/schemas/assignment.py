from pydantic import BaseModel
from .course import CourseView



class AssignmentBase(BaseModel):
    course_id: int
    assignment_name: str



class AssignmentCreate(AssignmentBase):
    pass



class AssignmentView(BaseModel):
    assignment_id: int
    course_instance: CourseView
    assignment_name: str


    class Config:
        from_attributes = True
