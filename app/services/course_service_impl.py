from typing import List
from app.services.course_service import CourseService
from app.db.connection import get_db, LocalSession
from app import models


class CourseServiceImpl(CourseService):
  """
  Please implement the CourseService interface according to the requirements.
  """
  def get_course_by_id(self, course_id):
    with LocalSession() as session:
      db_course = session.get(models.course.Course, course_id)
    return db_course
  

  def get_courses(self):
    with LocalSession() as session:
      db_courses = session.query(models.course.Course).all()
    return db_courses
  

  def create_course(self, course_name):
    with LocalSession() as session:
      db_course = models.course.Course(name=course_name)
      session.add(db_course)
      session.commit()
      session.refresh(db_course)
    return db_course  
  
  
  def delete_course(self, course_id):
    return super().delete_course(course_id)
  
  def create_assignment(self, course_id, assignment_name):
    return super().create_assignment(course_id, assignment_name)
  
  def enroll_student(self, course_id, student_id):
    return super().enroll_student(course_id, student_id)
  
  def dropout_student(self, course_id, student_id):
    return super().dropout_student(course_id, student_id)
  
  def submit_assignment(self, course_id, student_id, assignment_id, grade: int):
    return super().submit_assignment(course_id, student_id, assignment_id, grade)
  
  def get_assignment_grade_avg(self, course_id, assignment_id) -> int:
    return super().get_assignment_grade_avg(course_id, assignment_id)
  
  def get_student_grade_avg(self, course_id, student_id) -> int:
    return super().get_student_grade_avg(course_id, student_id)
  
  def get_top_five_students(self, course_id) -> List[int]:
    return super().get_top_five_students(course_id)
  
