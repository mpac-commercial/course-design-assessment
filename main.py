from app.services.course_service_impl import CourseServiceImpl
from fastapi import FastAPI
from app.schemas.course import Course as CourseSchema, CourseCreate 
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.models import course as course_model
import uvicorn
from typing import List



if __name__ == "__main__":
  course_service = CourseServiceImpl()

  app = FastAPI()
  

  @app.get('/course/', response_model=List[CourseSchema])
  def get_all_courses():
    return course_service.get_courses()


  @app.get(path='/course/{course_id}', response_model=CourseSchema)
  def get_course(course_id: int):
    print('input: ',course_id)
    db_course = course_service.get_course_by_id(course_id)
    print(db_course)
    return db_course
  

  @app.post(path="/course/create/", response_model=CourseCreate)
  def create_course(course: CourseCreate):
    print(course)
    db_course = course_service.create_course(course.name)
    return db_course
  

  @app.delete(path="/course/delete/{course_id}", response_model=CourseSchema)
  def delete_course_by_id(course_id: int):
    course_db = course_service.delete_course(course_id=course_id)
    return course_db



  uvicorn.run(app, host='127.0.0.1', port=8080)

  
