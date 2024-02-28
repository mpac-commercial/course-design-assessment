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
        assert self.fetch_if_exist(Course, course_id=new_obj.course_id) == None
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

    def test_student_enrollment_already_enrolled(self):
        with LocalSession() as session:
            new_course_obj = self.fetch_if_exist(Course, course_name='course enrollment already enrolled')
            if not new_course_obj:
                new_course_obj = Course(course_name='course enrollment already enrolled')
                session.add(new_course_obj)
                session.commit()
                session.refresh(new_course_obj)

            new_student_obj = self.fetch_if_exist(Student, student_name='student enrollment already enrolled')
            if not new_student_obj:
                new_student_obj = Student(Student, student_name='student enrollment already enrolled')
                session.add(new_student_obj)
                session.commit()
                session.refresh(new_student_obj)

            student_course_new_obj = self.fetch_if_exist(StudentCourse, course_id=new_course_obj.course_id, student_id=new_student_obj.student_id)
            if not student_course_new_obj:
                student_course_new_obj = StudentCourse(student_id=new_student_obj.student_id, course_id=new_course_obj.course_id)
                session.add(student_course_new_obj)
                session.commit()

            
        payload = {
            'student_id': new_student_obj.student_id,
            'course_id': new_course_obj.course_id
        }

        response = self.client.post('/student/enroll', json=payload)

        assert response.status_code == 409
        assert response.json() == {
            'detail': {
                'description': 'cannot enroll student.',
                'message': f'student with ID {new_student_obj.student_id} is already enrolled in course with ID {new_course_obj.course_id}.'
            }
        }


    def test_dropout_student_success(self):
        with LocalSession() as session:
            new_student_obj = self.fetch_if_exist(Student, student_name='student for dropout')
            if not new_student_obj:
                new_student_obj = Student(student_name='student for dropout')
                session.add(new_student_obj)
                session.commit()
                session.refresh(new_student_obj)

            new_course_obj = self.fetch_if_exist(Course, course_name='course for dropout')
            if not new_course_obj:
                new_course_obj = Course(course_name='course for dropout')
                session.add(new_course_obj)
                session.commit()
                session.refresh(new_course_obj)

            new_student_course_obj = self.fetch_if_exist(StudentCourse, student_id=new_student_obj.student_id, course_id=new_course_obj.course_id)
            if not new_student_course_obj:
                new_student_course_obj = StudentCourse(course_id=new_course_obj.course_id, student_id=new_student_obj.student_id)
                session.add(new_student_course_obj)
                session.commit()
                session.refresh(new_student_course_obj)

        payload = {
            'student_id': new_student_obj.student_id,
            'course_id': new_course_obj.course_id
        }

        response = self.client.request("DELETE", '/student/dropout', json=payload)

        assert response.status_code == 200
        assert self.fetch_if_exist(StudentCourse, student_course_id=new_student_course_obj.student_course_id) == None
        assert response.json() == {
            'student_course_id': new_student_course_obj.student_course_id,
            'student_instance': {
                'student_id': new_student_obj.student_id,
                'student_name': new_student_obj.student_name
            },
            'course_instance': {
                'course_id': new_course_obj.course_id,
                'course_name': new_course_obj.course_name
            }
        }

    
    def test_dropout_student_not_found(self):
        with LocalSession() as session:
            new_student_obj = self.fetch_if_exist(table=Student, student_name='student dropout student not found')
            if new_student_obj:
                session.delete(new_student_obj)
                session.commit()
            else:
                new_student_obj = Student(student_name='student dropout student not found')
                session.add(new_student_obj)
                session.commit()
                session.refresh(new_student_obj)
                session.delete(new_student_obj)
                session.commit()
            
            new_course_obj = self.fetch_if_exist(Course, course_name='course dropout student not found')
            if not new_course_obj:
                new_course_obj = Course(course_name='course dropout student not found')
                session.add(new_course_obj)
                session.commit()
                session.refresh(new_course_obj)
            
        payload = {
            'student_id': new_student_obj.student_id,
            'course_id': new_course_obj.course_id
        }                

        response = self.client.request('DELETE', '/student/dropout', json=payload)

        assert response.status_code == 404
        assert response.json() == {
            'detail': {
                'description': 'cannot dropout student.',
                'message': f'student with ID {new_student_obj.student_id} was not found!'
            }
        }


    def test_dropout_course_not_found(self):
        with LocalSession() as session:
            new_student_obj = self.fetch_if_exist(Student, student_name='student dropout course not found')
            if not new_student_obj:
                new_student_obj = Student(student_name='student dropout course not found')
                session.add(new_student_obj)
                session.commit()
                session.refresh(new_student_obj)

            new_course_obj = self.fetch_if_exist(Course, course_name='course dropout course not found')
            if new_course_obj:
                session.delete(new_course_obj)
                session.commit()
            else:
                new_course_obj = Course(course_name='course dropout course not found')
                session.add(new_course_obj)
                session.commit()
                session.refresh(new_course_obj)
                session.delete(new_course_obj)
                session.commit()
            
        payload = {
            'student_id': new_student_obj.student_id,
            'course_id': new_course_obj.course_id
        }

        response = self.client.request('DELETE', '/student/dropout', json=payload)

        assert response.status_code == 404
        assert response.json() == {
            'detail': {
                'description': 'cannot dropout student.',
                'message': f'course with ID {new_course_obj.course_id} was not found!'
            }
        }

    
    def test_student_dopoout_not_enrolled(self):
        with LocalSession() as session:
            new_student_obj = self.fetch_if_exist(table=Student, student_name='student dropout not enrolled')
            print(new_student_obj)
            if new_student_obj is None:
                print('ok')
                new_student_obj = Student(student_name='student dropout not enrolled')
                session.add(new_student_obj)
                session.commit()
                session.refresh(new_student_obj)
            # print(new_student_obj.student_name)
            
            new_course_obj = self.fetch_if_exist(table=Course, course_name='course dropout not enrolled')
            if new_course_obj is None:
                new_course_obj = Course(course_name='course dropout not enrolled')
                session.add(new_course_obj)
                session.commit()
                session.refresh(new_course_obj)
            # print(new_course_obj.course_name)
            
            payload = {
                'student_id': new_student_obj.student_id,
                'course_id': new_course_obj.course_id
            }

        response = self.client.request('DELETE', '/student/dropout', json=payload)

        assert response.status_code == 404
        assert response.json() == {
            'detail': {
                'description': 'cannot dropout student.',
                'message': f'student with ID {new_student_obj.student_id} is not enrolled in course with ID {new_course_obj.course_id}!'
            }
        }



class TestSubmission(TestBase):
    def test_create_submission(self):
        with LocalSession() as session:
            new_course_obj = self.fetch_if_exist(table=Course, course_name='course for submission')
            if new_course_obj is None:
                new_course_obj = Course(course_name='course for submission')
                session.add(new_course_obj)
                session.commit()
                session.refresh(new_course_obj)
            
            new_student_obj = self.fetch_if_exist(table=Student, student_name='student for submission')
            if new_student_obj is None:
                new_student_obj = Student(student_name='student for submission')
                session.add(new_student_obj)
                session.commit()
                session.refresh(new_student_obj)

            new_assignment_obj = self.fetch_if_exist(table=Assignment, assignment_name='assignment for submission', course_id=new_course_obj.course_id)
            if new_assignment_obj is None:
                new_assignment_obj = Assignment(assignment_name='assignment for submission', course_id=new_course_obj.course_id)
                session.add(new_assignment_obj)
                session.commit()
                session.refresh(new_assignment_obj)

            submission_obj = self.fetch_if_exist(
                table=Submission,
                assignment_id=new_assignment_obj.assignment_id,
                course_id=new_course_obj.course_id,
                student_id=new_student_obj.student_id
            )
            if submission_obj is not None:
                session.delete(submission_obj)
                session.commit()
            
            submission_obj = Submission(
                assignment_id=new_assignment_obj.assignment_id,
                course_id=new_course_obj.course_id,
                student_id=new_student_obj.student_id,
                grade=80
            )
            session.add(submission_obj)
            session.commit()
            session.refresh(submission_obj)
            session.delete(submission_obj)
            session.commit()

            payload = {
                'assignment_id': new_assignment_obj.assignment_id,
                'course_id': new_course_obj.course_id,
                'student_id': new_student_obj.student_id,
                'grade': submission_obj.grade
            }

        response = self.client.post('/submission/create', json=payload)

        assert response.status_code == 200
        assert self.fetch_if_exist(Assignment, course_id=new_assignment_obj.course_id, assignment_name=new_assignment_obj.assignment_name).course_id == new_course_obj.course_id
        assert response.json() == {
            'submission_id': submission_obj.submission_id+1,
            'course_instance': {
                'course_id': new_course_obj.course_id,
                'course_name': new_course_obj.course_name
            },
            'student_instance': {
                'student_name': new_student_obj.student_name,
                'student_id': new_student_obj.student_id
            },
            'assignment_instance': {
                'assignment_id': new_assignment_obj.assignment_id,
                'assignment_name': new_assignment_obj.assignment_name,
                'course_instance': {
                    'course_id': new_course_obj.course_id,
                    'course_name': new_course_obj.course_name
                },
            },
            'grade': submission_obj.grade
        }


    def test_submission_course_assignment_conflict(self):
        with LocalSession() as session:
            new_course_obj = self.fetch_if_exist(Course, course_name='course assignment conflict input')
            if new_course_obj is None:
                new_course_obj = Course(course_name='course assignment conflict input')
                session.add(new_course_obj)
                session.commit()
                session.refresh(new_course_obj)

            new_conflict_course_obj = self.fetch_if_exist(Course, course_name='course assignment conflict')
            if new_conflict_course_obj is None:
                new_conflict_course_obj = Course(course_name='course assignment conflict')
                session.add(new_conflict_course_obj)
                session.commit()
                session.refresh(new_conflict_course_obj)

            new_assignment_obj = self.fetch_if_exist(Assignment, assignment_name='assignment with conflict', course_id=new_conflict_course_obj.course_id)
            if new_assignment_obj is None:
                new_assignment_obj = Assignment(course_id=new_conflict_course_obj.course_id, assignment_name='assignment with conflict')
                session.add(new_assignment_obj)
                session.commit()
                session.refresh(new_assignment_obj)

            new_student_obj = self.fetch_if_exist(Student, student_name='submission student conflict')
            if new_student_obj is None:
                new_student_obj = Student(student_name='submission student conflict')
                session.add(new_student_obj)
                session.commit()
                session.refresh(new_student_obj)

            payload = {
                'student_id': new_student_obj.student_id,
                'course_id': new_course_obj.course_id,
                'assignment_id': new_assignment_obj.assignment_id,
                'grade': 80
            }

        response = self.client.post('/submission/create', json=payload)
        print(response.json())

        assert response.status_code == 409
        assert response.json() == {
            'detail': {
                'description': 'cannot create submission.',
                'message': f'course ID with ID {new_course_obj.course_id} is not matched with assignment\'s course ID {new_assignment_obj.course_id}.'
            }
        }

    
    def test_submission_student_not_found(self):
        with LocalSession() as session:
            new_course_obj = self.fetch_if_exist(Course, course_name='course submission student not found')
            if new_course_obj is None:
                new_course_obj = Course(course_name='course submission student not found')
                session.add(new_course_obj)
                session.commit()
                session.refresh(new_course_obj)

            new_assignment_obj = self.fetch_if_exist(Assignment, assignment_name='assignment submission student not found', course_id=new_course_obj.course_id)
            if new_assignment_obj is None:
                new_assignment_obj = Assignment(assignment_name='assignment submission student not found', course_id=new_course_obj.course_id)
                session.add(new_assignment_obj)
                session.commit()
                session.refresh(new_assignment_obj)

            new_student_obj = self.fetch_if_exist(Student, student_name='student submission student not found')
            if new_student_obj is None:
                new_student_obj = Student(student_name='student submission student not found')
                session.add(new_student_obj)
                session.commit()
                session.refresh(new_student_obj)
                session.delete(new_student_obj)
                session.commit()
            else:
                session.delete(new_student_obj)
                session.commit()
            
            payload = {
                'student_id': new_student_obj.student_id,
                'course_id': new_course_obj.course_id,
                'assignment_id': new_assignment_obj.assignment_id,
                'grade': 80
            }

        response = self.client.post('/submission/create', json=payload)

        assert response.status_code == 404
        assert response.json() == {
            'detail': {
                'description': 'cannot create submission',
                'message': f'could not find student with ID {new_student_obj.student_id}'
            }
        }


    def test_submission_course_not_found(self):
        with LocalSession() as session:
            new_course_obj = self.fetch_if_exist(Course, course_name='course submission course not found')
            if new_course_obj is None:
                new_course_obj = Course(course_name='course submission course not found')
                session.add(new_course_obj)
                session.commit()
                session.refresh(new_course_obj)
                session.delete(new_course_obj)
                session.commit()
            else:
                session.delete(new_course_obj)
                session.commit()

            new_student_obj = self.fetch_if_exist(Student, student_name='student submission course not found')
            if new_student_obj is None:
                new_student_obj = Student(student_name='student submission course not found')
                session.add(new_student_obj)
                session.commit()
                session.refresh(new_student_obj)
            
            new_assignment_obj = self.fetch_if_exist(Assignment, assignment_name='assignment submission course not found')
            if new_assignment_obj is None:
                new_assignment_obj = Assignment(course_id=2, assignment_name='assignment submission course not found')
                session.add(new_assignment_obj)
                session.commit()
                session.refresh(new_assignment_obj)

            payload = {
                'student_id': new_student_obj.student_id,
                'course_id': new_course_obj.course_id,
                'assignment_id': new_assignment_obj.assignment_id,
                'grade': 80
            }

        response = self.client.post('/submission/create', json=payload)

        assert response.status_code == 404
        assert response.json() == {
            'detail': {
                'description': 'cannot create submission.',
                'message': f'could not find course with ID {new_course_obj.course_id}'
            }
        }


    def test_submission_assignment_not_found(self):
        with LocalSession() as session:
            new_student_obj = self.fetch_if_exist(Student, student_name='student submission assignment not found')
            if new_student_obj is None:
                new_student_obj = Student(student_name='student submission assignment not found')
                session.add(new_student_obj)
                session.commit()
                session.refresh(new_student_obj)

            new_course_obj = self.fetch_if_exist(Course, course_name='course submission assignment not found')
            if new_course_obj is None:
                new_course_obj = Course(course_name='course submission assignment not found')
                session.add(new_course_obj)
                session.commit()
                session.refresh(new_course_obj)

            new_assignment_obj = self.fetch_if_exist(Assignment, course_id=new_course_obj.course_id, assignment_name='assignment submission assignment not found')
            if new_assignment_obj is None:
                new_assignment_obj = Assignment(course_id=new_course_obj.course_id, assignment_name='assignment submission assignment not found')
                session.add(new_assignment_obj)
                session.commit()
                session.refresh(new_assignment_obj)
                session.delete(new_assignment_obj)
                session.commit()
            else:
                session.delete(new_assignment_obj)
                session.commit()

            payload = {
                'assignment_id': new_assignment_obj.assignment_id,
                'course_id': new_course_obj.course_id,
                'student_id': new_student_obj.student_id,
                'grade': 80
            }
        
        response = self.client.post('/submission/create', json=payload)
        
        assert response.status_code == 404
        assert response.json() == {
            'detail': {
                'description': 'cannot create submission.',
                'message': f'could not find assignment with ID {new_assignment_obj.assignment_id}'
            }
        }


    def test_submission_grade_gt_100(self):
        with LocalSession() as session:
            new_student_obj = self.fetch_if_exist(Student, student_name='student submission grade not in range')
            if new_student_obj is None:
                new_student_obj = Student(student_name='stdent submission grade not in range')
                session.add(new_student_obj)
                session.commit()
                session.refresh(new_student_obj)

            new_course_obj = self.fetch_if_exist(Course, course_name='course submission grade not in range')
            if new_course_obj is None:
                new_course_obj = Course(course_name='course submission grade not in range')
                session.add(new_course_obj)
                session.commit()
                session.refresh(new_course_obj)

            new_assignment_obj = self.fetch_if_exist(Assignment, assignment_name='assignment submission grade not in range', course_id=new_course_obj.course_id)
            if new_assignment_obj is None:
                new_assignment_obj = Assignment(assignment_name='assignment submission grade not in range', course_id=new_course_obj.course_id)
                session.add(new_assignment_obj)
                session.commit()
                session.refresh(new_assignment_obj)

            payload = {
                'student_id': new_student_obj.student_id,
                'course_id': new_course_obj.course_id,
                'assignment_id': new_assignment_obj.assignment_id,
                'grade': 110
            }

        response = self.client.post('/submission/create', json=payload)

        assert response.status_code == 422
        assert response.json() == {
            'detail': {
                'description': 'cannot create submission',
                'message': 'grade out of range. grade should be between 0 and 100.'
            }
        }


    def test_submission_grade_le_0(self):
        with LocalSession() as session:
            new_course_obj = self.fetch_if_exist(Course, course_name='course submission grade not in range')
            if new_course_obj is None:
                new_course_obj = Course(course_name='course submission grade not in range')
                session.add(new_course_obj)
                session.commit()
                session.refresh(new_course_obj)

            new_student_obj = self.fetch_if_exist(Student, student_name='student submission grade not in range')
            if new_student_obj is None:
                new_student_obj = Student(student_name='student submission grade not in range')
                session.add(new_student_obj)
                session.commit()
                session.refresh(new_student_obj)

            new_assignment_obj = self.fetch_if_exist(Assignment, course_id=new_course_obj.course_id, assignment_name='assignment submission grade not in range')
            if new_assignment_obj is None:
                new_assignment_obj = Assignment(course_id=new_course_obj.course_id, assignment_name='assignment submission grade not in range')
                session.add(new_assignment_obj)
                session.commit()
                session.refresh(new_assignment_obj)
            
            payload = {
                'student_id': new_student_obj.student_id,
                'course_id': new_course_obj.course_id,
                'assignment_id': new_assignment_obj.assignment_id,
                'grade': -10
            }

        response = self.client.post('/submission/create', json=payload)
        
        assert response.status_code == 422
        assert response.json() == {
            'detail': {
                'description': 'cannot create submission',
                'message': 'grade out of range. grade should be between 0 and 100.'
            }
        }

    def test_submission_duplicate(self):
        with LocalSession() as session:
            new_student_obj = self.fetch_if_exist(Student, student_name='student submission duplicate')
            if new_student_obj is None:
                new_student_obj = Student(student_name='student submission duplicate')
                session.add(new_student_obj)
                session.commit()
                session.refresh(new_student_obj)

            new_course_obj = self.fetch_if_exist(Course, course_name='course submission duplicate')
            if new_course_obj is None:
                new_course_obj = Course(course_name='course submission duplicate')
                session.add(new_course_obj)
                session.commit()
                session.refresh(new_course_obj)

            new_assignment_obj = self.fetch_if_exist(Assignment, course_id=new_course_obj.course_id, assignment_name='assignment submission duplicate')
            if new_assignment_obj is None:
                new_assignment_obj = Assignment(course_id=new_course_obj.course_id, assignment_name='assignment submission duplicate')
                session.add(new_assignment_obj)
                session.commit()
                session.refresh(new_assignment_obj)

            new_submission_obj = self.fetch_if_exist(Submission, course_id=new_course_obj.course_id, assignment_id=new_assignment_obj.assignment_id, student_id=new_student_obj.student_id)
            if new_submission_obj is None:
                new_submission_obj = Submission(course_id=new_course_obj.course_id, assignment_id=new_assignment_obj.assignment_id, student_id=new_student_obj.student_id, grade=70)
                session.add(new_submission_obj)
                session.commit()
                session.refresh(new_submission_obj)

            payload = {
                'assignment_id': new_assignment_obj.assignment_id,
                'course_id': new_course_obj.course_id,
                'student_id': new_student_obj.student_id,
                'grade': 40
            }

        response = self.client.post('/submission/create', json=payload)

        assert response.status_code == 409
        assert response.json() == {
            'detail': {
                'description': 'cannot create submission.',
          'message': f'dupliacate values not allowed! record is available for course with ID {new_course_obj.course_id}, assignment with ID {new_assignment_obj.assignment_id}, and student with ID {new_student_obj.student_id}.'
            }
        }

    def test_average_student(self):
        with LocalSession() as session:
            new_course_obj = self.fetch_if_exist(Course, course_name='course average student')
            if new_course_obj is None:
                new_course_obj = Course(course_name='course average student')
                session.add(new_course_obj)
                session.commit()
                session.refresh(new_course_obj)
            
            new_student_obj = self.fetch_if_exist(Student, student_name='student average student')
            if new_student_obj is None:
                new_student_obj = Student(student_name='student average student')
                session.add(new_student_obj)
                session.commit()
                session.refresh(new_student_obj)

            assignment_list = list()
            for idx in range(1, 6):
                new_assignment_obj = self.fetch_if_exist(Assignment, course_id=new_course_obj.course_id, assignment_name=f'assignment {idx} average student')
                if new_assignment_obj:
                    assignment_list.append(new_assignment_obj)
                else:
                    assignment_list.append(Assignment(course_id=new_course_obj.course_id, assignment_name=f'assignment {idx} average student'))
            session.add_all(assignment_list)
            session.commit()
            for i in range(len(assignment_list)):
                session.refresh(assignment_list[i])
                
            submission_list = list()
            for idx in range(1, 6):
                new_submission_obj = self.fetch_if_exist(
                    Submission,
                    course_id=new_course_obj.course_id,
                    student_id=new_student_obj.student_id,
                    assignment_id=assignment_list[idx-1].assignment_id
                )
                if new_submission_obj:
                    submission_list.append(new_submission_obj)
                else:
                    submission_list.append(Submission(
                        student_id=new_student_obj.student_id,
                        course_id=new_course_obj.course_id,
                        assignment_id=assignment_list[idx-1].assignment_id,
                        grade=10*idx + 35
                    ))

            session.add_all(submission_list)
            session.commit()
            for i in range(len(submission_list)):
                session.refresh(submission_list[i])

            payload = {
                'course_id': new_course_obj.course_id,
                'student_id': new_student_obj.student_id,
            }

            avg_grade = session.query(func.round(func.avg(Submission.grade)))\
                .filter_by(course_id=new_course_obj.course_id, student_id=new_student_obj.student_id)\
                .scalar()
        
        print(avg_grade)

        response = self.client.request('GET', '/submission/average-course-student', json=payload)

        assert response.status_code == 200
        assert round(sum([10*idx +35 for idx in range(1,6)])/5) == avg_grade
        assert response.json() == {
            'student_instance': {
                'student_id': new_student_obj.student_id,
                'student_name': new_student_obj.student_name
            },
            'course_instance': {
                'course_id': new_course_obj.course_id,
                'course_name': new_course_obj.course_name
            },
            'grade': avg_grade
        }


    def test_average_student_course_not_found(self):
        with LocalSession() as session:
            new_course_obj = self.fetch_if_exist(table=Course, course_name='course to be deleted student average')
            if new_course_obj is None:
                new_course_obj = Course(course_name='course to be deleted student average')
                session.add(new_course_obj)
                session.commit()
                session.refresh(new_course_obj)
                session.delete(new_course_obj)
                session.commit()
            else:
                session.delete(new_course_obj)
                session.commit()


            payload = {
                'course_id': new_course_obj.course_id,
                'student_id': 1,
            }

        response= self.client.request('GET', '/submission/average-course-student', json=payload)

        assert response.status_code == 404
        assert response.json() == {
            'detail': {
                'description': 'request cannot be made.',
                'message': f'no course was found with ID {new_course_obj.course_id}'
            }
        }


    def test_average_student_student_not_found(self):
        with LocalSession() as session:
            new_course_obj = self.fetch_if_exist(Course, course_name='course for student average student not found')
            if new_course_obj is None:
                new_course_obj = Course(course_name='course for student average student not found')
                session.add(new_course_obj)
                session.commit()
                session.refresh(new_course_obj)
            
            new_student_obj = self.fetch_if_exist(Student, student_name='student for student average student not found')
            if new_student_obj is None:
                new_student_obj = Student(student_name='student for student average student not found')
                session.add(new_student_obj)
                session.commit()
                session.refresh(new_student_obj)
                session.delete(new_student_obj)
                session.commit()
            
            else:
                session.delete(new_student_obj)
                session.commit()

            payload = {
                'course_id': new_course_obj.course_id,
                'student_id': new_student_obj.student_id
            }

        response = self.client.request('GET', '/submission/average-course-student', json=payload)

        assert response.status_code == 404
        assert response.json() == {
            'detail': {
                'description': 'request cannot be made.',
                'message': f'no student was found with ID {new_student_obj.student_id}'
            }
        }

    
    def test_average_student_no_record_found(self):
        with LocalSession() as session:
            new_course_obj = self.fetch_if_exist(Course, course_name='course without student submission')
            if new_course_obj is None:
                new_course_obj = Course(course_name='course without student submission')
                session.add(new_course_obj)
                session.commit()
                session.refresh(new_course_obj)

            new_student_obj = self.fetch_if_exist(Student, student_name='student without course submission record')
            if new_student_obj is None:
                new_student_obj = Student(student_name='student without course submission record')
                session.add(new_student_obj)
                session.commit()
                session.refresh(new_student_obj)

            all_records = session.query(Submission)\
                .filter_by(course_id=new_course_obj.course_id, student_id=new_student_obj.student_id)\
                .all()
            
            for record in all_records:
                session.delete(record)
            session.commit()

            payload = {
                'student_id': new_student_obj.student_id,
                'course_id': new_course_obj.course_id
            }

        response = self.client.request('GET', '/submission/average-course-student', json=payload)

        assert response.status_code == 404
        assert response.json() == {
            'detail': {
                'description': 'request cannot be made',
                'message': f'could not find any grade for course with ID {new_course_obj.course_id} and student with ID {new_student_obj.student_id}'
            }
        }


    def test_average_assignment(self):
        with LocalSession() as session:
            new_course_obj = self.fetch_if_exist(Course, course_name='course for assignment average')
            if new_course_obj is None:
                new_course_obj = Course(course_name='course for assignment average')
                session.add(new_course_obj)
                session.commit()
                session.refresh(new_course_obj)

            new_assignment_obj = self.fetch_if_exist(Assignment, course_id=new_course_obj.course_id, assignment_name='assignment for assignment average')
            if new_assignment_obj is None:
                new_assignment_obj = Assignment(course_id=new_course_obj.course_id, assignment_name='assignment for assignment average')
                session.add(new_assignment_obj)
                session.commit()
                session.refresh(new_assignment_obj)

            student_list = list()
            for idx in range(1,6):
                student_instance = self.fetch_if_exist(Student, student_name=f'student {idx} assignment average')
                if not student_instance:
                    student_instance = student_list.append(Student(student_name=f'student {idx} assignment average'))
                else:
                    student_list.append(student_instance)
            session.add_all(student_list)
            session.commit()
            for idx in range(len(student_list)):
                session.refresh(student_list[idx])
            
            grades_list = list()
            submission_list = list()
            for idx in range(1, 6):
                submission_instace = self.fetch_if_exist(
                    Submission,
                    course_id=new_course_obj.course_id,
                    assignment_id=new_assignment_obj.assignment_id,
                    student_id=student_list[idx-1].student_id,
                )
                if not submission_instace:
                    submission_instace = Submission(course_id=new_course_obj.course_id,
                                                    assignment_id=new_assignment_obj.assignment_id,
                                                    student_id=student_list[idx-1].student_id,
                                                    grade=10*idx + 35
                                                    )
                submission_list.append(submission_instace)
                grades_list.append(submission_instace.grade)
            session.add_all(submission_list)
            session.commit()

            payload = {
                'course_id': new_course_obj.course_id,
                'assignment_id': new_assignment_obj.assignment_id
            }

            avg_grade = session.query(func.round(func.avg(Submission.grade))).filter_by(assignment_id=new_assignment_obj.assignment_id, course_id=new_course_obj.course_id).scalar()

        response = self.client.request('GET', '/submission/average-course-assignment', json=payload)
        print(response.json())
        
        assert response.status_code == 200
        assert int(avg_grade) == sum(grades_list)/5
        assert response.json() == {
            'course_instance': {
                'course_id': new_course_obj.course_id,
                'course_name': new_course_obj.course_name
            },
            'assignment_instance': {
                'assignment_id': new_assignment_obj.assignment_id,
                'assignment_name': new_assignment_obj.assignment_name,
                'course_instance': {
                    'course_id': new_course_obj.course_id,
                    'course_name': new_course_obj.course_name
                }
            },
            'grade': int(avg_grade)
        }


    def test_average_submission_course_not_found(self):
        with LocalSession() as session:
            new_course_obj = self.fetch_if_exist(Course, course_name='course to be deleted average submission course not found')
            if new_course_obj is None:
                new_course_obj = Course(course_name='course to be deleted average submission course not found')
                session.add(new_course_obj)
                session.commit()
                session.refresh(new_course_obj)
                session.delete(new_course_obj)
                session.commit()
            else:
                session.delete(new_course_obj)
                session.commit()

            payload = {
                'course_id': new_course_obj.course_id,
                'assignment_id': 1
            }

        response = self.client.request('GET', '/submission/average-course-assignment', json=payload)

        assert response.status_code == 404
        assert response.json() == {
            'detail': {
                'description': 'request cannot be made.',
                'message': f'could not find course with ID {new_course_obj.course_id}'
            }
        }


