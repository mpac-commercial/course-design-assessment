from app.services.course_service_impl import CourseServiceImpl
from fastapi import FastAPI
from app.schemas.course import CourseView, CourseCreate 
from app.schemas.assignment import AssignmentCreate, AssignmentView
from app.schemas.student import StudentView
from app.schemas.student_course import StudentCourseView, StudentCourseCreate
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
  
  
  @app.post(path='/student/enroll/', response_model=StudentCourseView)
  def enroll_student(student_course: StudentCourseCreate):
    db_student_course = course_service.enroll_student(
      course_id=student_course.course_id,
      student_id=student_course.student_id
    )

    db_student = course_service.get_student_by_id(student_course.student_id)
    student_instance = StudentView(
      student_name=db_student.student_name,
      student_id=db_student.student_id
      )

    db_course = course_service.get_course_by_id(db_student_course.course_id)
    course_instance = CourseView(
      course_id=db_course.course_id,
      course_name=db_course.course_name
    )

    return StudentCourseView(
      student_course_id=db_student_course.student_course_id,
      course_instance=course_instance, 
      student_instance=student_instance
      )

  @app.delete(path='/student/dropout/', response_model=StudentCourseView)
  def dropout_student(student_course: StudentCourseCreate):
    delted_student_course = course_service.dropout_student(
      student_id=student_course.student_id,
      course_id=student_course.course_id
    )

    db_student = course_service.get_student_by_id(delted_student_course.student_id)
    student_instance = StudentView(
      student_name=db_student.student_name,
      student_id=db_student.student_id
    )

    db_course = course_service.get_course_by_id(delted_student_course.course_id)
    course_instance = CourseView(

      course_name=db_course.course_name,
      course_id=db_course.course_id
    )

    return StudentCourseView(
      student_course_id=delted_student_course.student_course_id,
      student_instance=student_instance,
      course_instance=course_instance
    )


    

  uvicorn.run(app, host='127.0.0.1', port=8080)

  
