from pydantic import BaseModel
# from typing import 


class CourseBase(BaseModel):
    course_name: str


class CourseCreate(CourseBase):
    pass


class CourseView(CourseBase):
    course_id: int


    class Config:
        orm_mode = True