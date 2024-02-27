from pydantic import BaseModel



class StudentBase(BaseModel):
    student_name: str



class StudentCreate(StudentBase):
    pass



class StudentView(StudentBase):
    student_id: int


    class Config:
        from_attributes = True