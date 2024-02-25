from pydantic import BaseModel
from app.schemas.student import StudentView
from app.schemas.course import CourseView
from app.models.student_course import StudentCourse



class StudentCourseBase(BaseModel):
    student_id: int
    course_id: int



class StudentCourseCreate(StudentCourseBase):
    pass



class StudentCourseView(BaseModel):
    student_course_id: int
    student_instance: StudentView
    course_instance: CourseView


