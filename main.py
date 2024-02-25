from app.services.course_service_impl import CourseServiceImpl
from fastapi import FastAPI
from app.schemas.course import Course as CourseSchema, CourseCreate as CourseCreateSchema
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
  
  uvicorn.run(app, host='127.0.0.1', port='8000')

  
