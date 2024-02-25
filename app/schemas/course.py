from pydantic import BaseModel
# from typing import 


class CourseBase(BaseModel):
    name: str


class CourseCreate(CourseBase):
    pass


class Course(CourseBase):
    id: int
    name: str


    class Config:
        orm_mode = True