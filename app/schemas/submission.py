from pydantic import BaseModel
from app.schemas.course import CourseView
from app.schemas.student import StudentView
from app.schemas.assignment import AssignmentView
from typing import List



class SumissionBase(BaseModel):
    course_id: int
    student_id: int
    assignment_id:int
    grade: int



class SubmissionCreate(SumissionBase):
    pass



class SubmissionView(BaseModel):
    submission_id: int
    course_instance: CourseView
    student_instance: StudentView
    assignment_instance: AssignmentView
    grade: int


    class Config:
        from_attributes = True



class SubmissionAvgCourseStudent(BaseModel):
    course_instance: CourseView
    student_instance: StudentView
    grade: int



class SubmissionAvgCourseAssignment(BaseModel):
    course_instance: CourseView
    assignment_instance: AssignmentView
    grade: int



class CourseAssignment(BaseModel):
    course_id: int
    assignment_id: int



class SubmissionTopCourseGrades(BaseModel):
    course_instance: CourseView
    students: List[int]