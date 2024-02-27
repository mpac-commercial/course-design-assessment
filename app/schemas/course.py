from pydantic import BaseModel
from typing import List


class CourseBase(BaseModel):
    course_name: str


class CourseCreate(CourseBase):
    pass


class CourseView(CourseBase):
    course_id: int


    class Config:
        from_attributes = True


class AllCourseView(BaseModel):
    count_course: int
    course_list: List[CourseView]
