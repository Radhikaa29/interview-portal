from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schemas import AdminLogin
from models import Admin
from database import get_db
from auth import verify_password 
from auth import get_current_admin
from models import Student, TestResult, CodingResult,CodingQuestion
from auth import create_access_token
from datetime import timedelta
from models import Student # Assuming your student table is User
from schemas import StudentBasicInfo
from typing import List

 # We'll use this to compare hashed passwords

router = APIRouter(prefix="/admin", tags=["Admin"])

#  Admin Login
@router.post("/login")
def admin_login(credentials: AdminLogin, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == credentials.username).first()
    if not admin or not verify_password(credentials.password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": str(admin.id)}, expires_delta=timedelta(minutes=120))

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/students", response_model=List[StudentBasicInfo])
def get_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return students


@router.get("/search-user/{student_id}")
def search_user_by_id(student_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    mcq_result = db.query(TestResult).filter(TestResult.student_id == student_id).first()

    coding_results = (
        db.query(CodingResult)
        .filter(CodingResult.student_id == student_id)
        .join(CodingQuestion)
        .all()
    )

    return {
        "student": {
            "id": student.id,
            "name": student.username,
            "email": student.email,
            "mobile": student.mobile_number,
            "language": student.language,
        },
        "mcq_result": mcq_result.score if mcq_result else "Not Attempted",
        "coding_results": [
            {
                "question": cr.coding_question.question,  # ← using actual `question` field here
                "code_submitted": cr.code_submitted,
                "status": cr.status,
                "language": cr.language,
                "submitted_at": cr.timestamp,
            }
            for cr in coding_results
        ]
    }

