from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Student, MCQ, TestResult, CodingQuestion,TestCase
from auth import create_access_token, hash_password, verify_password, get_current_student, get_db
from datetime import timedelta
from schemas import StudentCreate
from pydantic import BaseModel
from fastapi import APIRouter


router = APIRouter()



# Ensure database tables are created
Student.metadata.create_all(bind=engine)

# Authentication Models
class StudentCreate(BaseModel):
    username: str
    email: str
    password: str
    mobile_number: str  # Add this field
    language: str 

class StudentLogin(BaseModel):
    username: str
    password: str

    

@router.post("/register/")
def register(student: StudentCreate, db: Session = Depends(get_db)):
    existing_student = db.query(Student).filter(Student.username == student.username).first()
    if existing_student:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    
    hashed_pwd = hash_password(student.password)
    db_student = Student(
        username=student.username, 
        email=student.email, 
        hashed_password=hashed_pwd,
        mobile_number=student.mobile_number,  # Add this line
        language=student.language  # Add this line
    )
    
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    
    return {"message": "Student registered successfully"}

@router.post("/token/")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.username == form_data.username).first()
    if not student or not verify_password(form_data.password, student.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": student.username}, expires_delta=timedelta(minutes=120))
    return {"access_token": access_token, "token_type": "bearer"}
