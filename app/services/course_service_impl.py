from typing import List
from app.services.course_service import CourseService
from app.db.connection import get_db, LocalSession
from app.models.course import Course
from app.models.assignment import Assignment


class CourseServiceImpl(CourseService):
  """
  Please implement the CourseService interface according to the requirements.
  """
  def get_course_by_id(self, course_id) -> Course:
    with LocalSession() as session:
      db_course = session.get(Course, course_id)
    return db_course
  

  def get_courses(self) -> list[Course]:
    with LocalSession() as session:
      db_courses = session.query(Course).all()
    return db_courses
  

  def create_course(self, course_name) -> Course:
    with LocalSession() as session:
      db_course = Course(course_name=course_name)
      session.add(db_course)
      session.commit()
      session.refresh(db_course)
    return db_course  
  
  
  def delete_course(self, course_id) -> Course:
    with LocalSession() as session:
      db_course = session.get(Course, course_id)
      session.delete(db_course)
      session.commit()
    return db_course
  
  
  def create_assignment(self, course_id, assignment_name) -> Assignment:
    with LocalSession() as session:
      db_assignemnt = Assignment(course_id=course_id, assignment_name=assignment_name)      
      session.add(db_assignemnt)
      session.commit()
      session.refresh(db_assignemnt)
      return db_assignemnt

  
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
  
