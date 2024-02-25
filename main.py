from app.services.course_service_impl import CourseServiceImpl
from fastapi import FastAPI
from app.schemas.course import CourseView, CourseCreate 
from app.schemas.assignment import AssignmentCreate, AssignmentView
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.models import course as course_model
import uvicorn
from typing import List



if __name__ == "__main__":
  course_service = CourseServiceImpl()

  app = FastAPI()
  

  @app.get('/course/', response_model=List[CourseView])
  def get_all_courses():
    return course_service.get_courses()


  @app.get(path='/course/{course_id}', response_model=CourseView)
  def get_course(course_id: int):
    print('input: ',course_id)
    db_course = course_service.get_course_by_id(course_id)
    print(db_course)
    return db_course
  

  @app.post(path="/course/create/", response_model=CourseCreate)
  def create_course(course: CourseCreate):
    print(course)
    db_course = course_service.create_course(course.course_name)
    return db_course
  

  @app.delete(path="/course/delete/{course_id}", response_model=CourseView)
  def delete_course_by_id(course_id: int):
    db_course = course_service.delete_course(course_id=course_id)
    return db_course


  @app.post(path='/assignment/create/', response_model=AssignmentView)
  def create_assignment(assignment: AssignmentCreate):
    db_assignment = course_service.create_assignment(
      course_id=assignment.course_id,
      assignment_name=assignment.assignment_name
    )

    db_course = course_service.get_course_by_id(db_assignment.course_id)

    return AssignmentView(
      assignment_id=db_assignment.assignment_id,
      course_instance={'course_id':db_course.course_id, 'course_name': db_course.course_name},
      assignment_name=db_assignment.assignment_name
    )


    

  uvicorn.run(app, host='127.0.0.1', port=8080)

  
