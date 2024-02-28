from fastapi.testclient import TestClient
from main import app
from app.db.connection import LocalSession
import pytest
from app.models.course import Course
from app.models.student import Student
from app.models.student_course import StudentCourse
from app.models.assignment import Assignment
from app.models.submission import Submission
from sqlalchemy import func, text



class TestBase:
    client = TestClient(app)

    def delete_if_exist(self, table, **kwargs):
        with LocalSession() as session:
            instance_obj = session.query(table).filter_by(**kwargs).first()
            if instance_obj:
                session.delete(instance_obj)
                session.commit()
        return None
        

    def fetch_if_exist(self, table, **kwargs):
        with LocalSession() as session:
            return session.query(table)\
            .filter_by(**kwargs)\
            .first()


    def fetch_last_value(self, table_name, table_id):
        with LocalSession() as session:
            session.execute(text(
                f'delete from {table_name} where id={table_id};'
            ))
            session.commit()
            session.execute(text(
                f'alter table {table_name} auto_increment={table_id}'
            ))
            session.commit()
        return table_id


class TestCourse(TestBase):
    def test_create_course(self):
        payload = {
            'course_name': 'test course'
        }
        
        with LocalSession() as session:
            instance_obj = session.query(Course).filter_by(course_name=payload['course_name']).first()
            if instance_obj:
                session.delete(instance_obj)
                session.commit()

            new_obj = Course(**payload)
            session.add(new_obj)
            session.commit()
            session.refresh(new_obj)

        max_id = self.fetch_last_value('course', new_obj.course_id)
        response = self.client.post('/course/create', json=payload)
        
        assert response.status_code == 200
        assert response.json() == {'course_id': max_id, 'course_name': payload['course_name']}


    def test_create_duplicate_course(self):
        new_obj = Course(course_name='test for duplicate')
        self.delete_if_exist(table=Course, course_name=new_obj.course_name)
        with LocalSession() as session:
            session.add(new_obj)
            session.commit()
            session.refresh(new_obj)
        
        payload = {
            'course_name': new_obj.course_name
        }

        response = self.client.post('/course/create', json=payload)

        assert response.status_code == 409
        assert response.json() == {
            'detail': {
          'description': 'cannot insert duplicate.',
          'message': f'A course with {new_obj.course_name} name is available and cannot insert duplicate'
        }
        }


    def test_create_course_more_than_100_char(self):
        payload = {
            'course_name': 'a' * 101
        }

        response = self.client.post('/course/create', json=payload)

        assert response.status_code == 406
        assert response.json() == {
            'detail': {
          'description': 'cannot create course.',
          'message': 'course name should have less than 100 characters.'
        }
        }


    def test_get_course_by_id(self):
        self.delete_if_exist(table=Course, course_name='test for get by id')
        
        with LocalSession() as session:
            new_obj = Course(course_name='test for get by id')
            session.add(new_obj)
            session.commit()
            session.refresh(new_obj)
        
        response = self.client.get(f'/course/{new_obj.course_id}')

        assert response.status_code == 200
        assert response.json() == {'course_id': new_obj.course_id, 'course_name': new_obj.course_name}

    
    def test_course_not_found_by_id(self):
        with LocalSession() as session:
            new_obj = Course(course_name='test for error by get id')
            self.delete_if_exist(table=Course, course_name=new_obj.course_name)
            session.add(new_obj)
            session.commit()
            session.refresh(new_obj)
            session.delete(new_obj)
            session.commit()

        response = self.client.get(f'/course/{new_obj.course_id}')
        
        assert response.status_code == 404
        assert response.json() == {'detail': {
      'description': 'Item not found.',
      'message': f'course not found with ID {new_obj.course_id}!'
    }}
        
    def test_get_all_courses(self):
        with LocalSession() as session:
            objs = session.query(Course).all()

        course_list = [{'course_id': obj.course_id, 'course_name': obj.course_name} for obj in objs]

        response = self.client.get('/course/all')

        assert response.status_code == 200
        assert response.json() == {
            'count_course': len(objs),
            'course_list': course_list
        }

    
    def test_delete_course_by_id(self):
        with LocalSession() as session:
            new_obj = Course(course_name='course to be deleted')
            self.delete_if_exist(table=Course, course_name=new_obj.course_name)
            session.add(new_obj)
            session.commit()
            session.refresh(new_obj)

        response = self.client.delete(f'/course/delete/{new_obj.course_id}')

        assert response.status_code == 200
        assert response.json() == {
            'course_id': new_obj.course_id,
            'course_name': new_obj.course_name
        }

    
    def test_delete_course_by_id_not_found(self):
        with LocalSession() as session:
            new_obj = Course(course_name='test for id not found')
            session.add(new_obj)
            session.commit()
            session.refresh(new_obj)

        self.delete_if_exist(table=Course, course_name=new_obj.course_name)

        response = self.client.delete(f'/course/delete/{new_obj.course_id}')

        assert response.status_code == 404
        assert response.json() == {
            'detail': {
          'description': 'cannot delete course.',
          'message': f'course couldn\'t be found with ID {new_obj.course_id}.' 
        }
        }




class TestAssignment(TestBase):
    def test_create_assignment(self):
        self.delete_if_exist(table=Assignment, assignment_name='test for create')
        with LocalSession() as session:
            new_course_obj = Course(course_name='test course for assignment')
            self.delete_if_exist(table=Course, course_name=new_course_obj.course_name)
            session.add(new_course_obj)
            session.commit()
            session.refresh(new_course_obj)
        payload = {'assignment_name': 'test for create', 'course_id': new_course_obj.course_id}

        with LocalSession() as session:
            self.delete_if_exist(Assignment, assignment_name=payload['assignment_name'], course_id=new_course_obj.course_id)
            new_assignment_obj = Assignment(assignment_name=payload['assignment_name'],
                                             course_id=new_course_obj.course_id)
            session.add(new_assignment_obj)
            session.commit()
            session.refresh(new_assignment_obj)
            session.delete(new_assignment_obj)
            session.commit()

        response = self.client.post('/assignment/create', json=payload)

        assert response.status_code == 200
        assert response.json() == {
            'assignment_id': new_assignment_obj.assignment_id+1,
            'assignment_name': new_assignment_obj.assignment_name,
            'course_instance': {
                'course_id': new_course_obj.course_id,
                'course_name': new_course_obj.course_name
            }
        }


    def test_create_assignment_course_not_found(self):
        with LocalSession() as session:
            new_course_obj = Course(course_name='assignemnt course to be deleted')
            self.delete_if_exist(Course, course_name=new_course_obj.course_name)
            session.add(new_course_obj)
            session.commit()
            session.refresh(new_course_obj)
            session.delete(new_course_obj)
            session.commit()

        payload = {
            'course_id': new_course_obj.course_id,
            'assignment_name': 'assignment for course not found error'
        }

        respone = self.client.post('/assignment/create', json=payload)

        assert respone.status_code == 404
        assert respone.json() == {
            'detail': {
      'desccription': 'cannot create assignment.',
      'message': f'Course not found with ID {new_course_obj.course_id}'
    }
        }

    
    def test_create_assignment_long_assignment_name(self):
        with LocalSession() as session:
            new_course_obj = Course(course_name='course for long assignment name error')
            self.delete_if_exist(table=Course, course_name=new_course_obj.course_name)
            session.add(new_course_obj)
            session.commit()
            session.refresh(new_course_obj)


        payload = {
            'assignment_name': 'c' * 101,
            'course_id': new_course_obj.course_id
        }

        response = self.client.post('/assignment/create', json=payload)

        assert response.status_code == 406
        assert response.json() == {
            'detail': {
          'description': 'cannot create assignment.',
          'message': 'assignment name should have between 0 and 100 characters.'
        }
        }


    def test_create_assignment_dupilcate(self):
        payload = {
            'assignment_name': 'duplicate assignment',
            'course_id': None
        }

        with LocalSession() as session:
            self.delete_if_exist(table=Assignment, assignment_name=payload['assignment_name'])
            new_course_obj = Course(course_name='course for duplicate')
            self.delete_if_exist(table=Course, course_name=new_course_obj.course_name)
            session.add(new_course_obj)
            session.commit()
            session.refresh(new_course_obj)
    
        payload['course_id'] = new_course_obj.course_id

        with LocalSession() as session:
            new_assignment_obj = Assignment(assignment_name=payload['assignment_name'], course_id=new_course_obj.course_id)
            self.delete_if_exist(Assignment, course_id=new_course_obj.course_id, assignment_name=payload['assignment_name'])
            session.add(new_assignment_obj)
            session.commit()
            session.refresh(new_assignment_obj)

        
        response = self.client.post('/assignment/create', json=payload)
        print(response.json())
        
        assert response.status_code == 409
        assert response.json() == {
            'detail': {
          'description': 'cannot create assignment.',
          'message': f'An assignment was found with name {new_assignment_obj.assignment_name} and course ID {new_course_obj.course_id}'
        }
        }

    

class TestStudent(TestBase):
    def test_enroll_student(self):
        with LocalSession() as session:
            new_course_obj = self.fetch_if_exist(table=Course, course_name='course for student enrollment')
            if not new_course_obj:
                new_course_obj = Course(course_name='course for student enrollment')
                session.add(new_course_obj)
                session.commit()
                session.refresh(new_course_obj)

        with LocalSession() as session:
            new_student_obj = self.fetch_if_exist(Student, student_name='student for enrollment')
            if not new_student_obj:
                new_student_obj = Student(student_name='student for enrollment')
                session.add(new_student_obj)
                session.commit()
                session.refresh(new_student_obj)

        payload = {
            'student_id': new_student_obj.student_id,
            'course_id': new_course_obj.course_id
        }

        with LocalSession() as session:
            new_student_course_obj = StudentCourse(course_id=new_course_obj.course_id, student_id=new_student_obj.student_id)
            self.delete_if_exist(StudentCourse, student_id=new_student_obj.student_id, course_id=new_course_obj.course_id)
            session.add(new_student_course_obj)
            session.commit()
            session.refresh(new_student_course_obj)
        self.delete_if_exist(StudentCourse, student_id=new_student_obj.student_id, course_id=new_course_obj.course_id)

        response = self.client.post('/student/enroll', json=payload)

        assert response.status_code == 200
        assert response.json() == {
            'student_course_id': new_student_course_obj.student_course_id+1,
            'student_instance': {
                'student_id': new_student_obj.student_id,
                'student_name': new_student_obj.student_name
            },
            'course_instance': {
                'course_id': new_course_obj.course_id,
                'course_name': new_course_obj.course_name
            }
        }

    
    def test_student_enrollment_student_not_found(self):
        with LocalSession() as session:
            new_student_obj = self.delete_if_exist(Student, student_name='student enrollment student not found')
            if new_student_obj:
                session.delete(new_student_obj)
                session.commit()
            if not new_student_obj:
                new_student_obj = Student(student_name='student enrollment student not found')
                session.add(new_student_obj)
                session.commit()
                session.refresh(new_student_obj)
                session.delete(new_student_obj)
                session.commit()

        with LocalSession() as session:
            new_course_obj = self.fetch_if_exist(Course, course_name='student enrollment student not found')
            if not new_course_obj:
                new_course_obj = Course(course_name='student enrollment student not found')
                session.add(new_course_obj)
                session.commit()
                session.refresh(new_course_obj)

        payload = {
            'student_id': new_student_obj.student_id,
            'course_id': new_course_obj.course_id
        }

        response = self.client.post('/student/enroll', json=payload)
        print(response.json())

        assert response.status_code == 404
        assert response.json() == {
            'detail': 
                {
          'description': 'cannot enroll student.',
          'message': f'could not find student with ID {new_student_obj.student_id}'
            }
        }


    def test_student_enrollment_course_not_found(self):
        with LocalSession() as session:
            new_student_obj = self.fetch_if_exist(Student, student_name='student enrollment course not found')
            if not new_student_obj:
                new_student_obj = Student(student_name='student enrollment course not found')
                session.add(new_student_obj)
                session.commit()
                session.refresh(new_student_obj)
        
        with LocalSession() as session:
            new_course_obj = self.fetch_if_exist(Course, course_name='course enrollment course not found')
            if new_course_obj:
                session.delete(new_course_obj)
                session.commit()
            if not new_course_obj:
                new_course_obj = Course(course_name='course enrollment course not found')
                session.add(new_course_obj)
                session.commit()
                session.refresh(new_course_obj)
                session.delete(new_course_obj)
                session.commit()
        

        payload = {
            'student_id': new_student_obj.student_id,
            'course_id': new_course_obj.course_id
        }

        response = self.client.post('/student/enroll', json=payload)

        assert response.status_code == 404
        assert response.json() == {
            'detail': {
                'description': 'cannot enroll student',
                'message': f'could not find course with ID {new_course_obj.course_id}'
            }
        }        
