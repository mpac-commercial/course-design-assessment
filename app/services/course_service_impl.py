from typing import List
from app.services.course_service import CourseService
from app.db.connection import get_db, LocalSession
from app.models.course import Course
from app.models.student import Student
from app.models.assignment import Assignment
from app.models.student_course import StudentCourse
from app.models.submission import Submission
from sqlalchemy import func, desc, text



class CourseServiceMixin:
  def get_student_by_id(self, student_id) -> Student:
    with LocalSession() as session:
      db_student = session.get(Student, ident=student_id)
    return db_student
    

  def get_assignment_by_id(self, assignment_id: int) -> Assignment:
    with LocalSession() as session:
      db_assignment = session.get(Assignment, assignment_id)
    return db_assignment



class CourseServiceImpl(CourseService, CourseServiceMixin):
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


  def enroll_student(self, course_id, student_id) -> StudentCourse:
    with LocalSession() as session:
      db_student_course = StudentCourse(student_id=student_id, course_id=course_id)
      session.add(db_student_course)
      session.commit()
      session.refresh(db_student_course)
    return db_student_course


  def dropout_student(self, course_id, student_id) -> StudentCourse:
    with LocalSession() as session:
      db_student_course = session.query(StudentCourse).where(
        StudentCourse.course_id==course_id,
        StudentCourse.student_id==student_id
      ).order_by(StudentCourse.student_course_id.desc()).first()
      
      session.delete(db_student_course)
      session.commit()

    return db_student_course


  def submit_assignment(self, course_id, student_id, assignment_id, grade: int):
    with LocalSession() as session:
      db_submission = Submission(
        course_id=course_id,
        student_id=student_id,
        assignment_id=assignment_id,
        grade=grade
      )
      session.add(db_submission)
      session.commit()
      session.refresh(db_submission)
    return db_submission

  
  def get_assignment_grade_avg(self, course_id, assignment_id) -> int:
    with LocalSession() as session:
      return int(session.query(func.round(func.avg(Submission.grade))).filter(Submission.course_id==course_id, Submission.assignment_id==assignment_id).scalar())
  

  def get_student_grade_avg(self, course_id, student_id) -> int:
    with LocalSession() as session:
      return int(session.query(func.round(func.avg(Submission.grade))).filter(Submission.course_id==course_id, Submission.student_id==student_id).scalar())
  

  def get_top_five_students(self, course_id) -> List[int]:
    with LocalSession() as session:
        top_5 = session.query(
          Submission.student_id,
          func.avg(Submission.grade).label('average_grade')
          ).filter_by(course_id=course_id)\
          .group_by(Submission.student_id)\
          .order_by(desc('average_grade'))\
          .limit(5)\
          .all()
    return [student_id for student_id, _ in top_5]
  
