from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from auth import get_current_student, get_db
from models import MCQ, TestResult,Student
from pydantic import BaseModel
import random
import html

router = APIRouter()

class MCQAnswer(BaseModel):
    question_id: int
    selected_option: str

@router.get("/mcq-test/")
def fetch_mcq_questions(db: Session = Depends(get_db), current_student: Student = Depends(get_current_student)):
    questions = db.query(MCQ).all()
    random_questions = random.sample(questions, 20) if len(questions) >= 20 else questions
    response = []
    for q in random_questions:
        response.append({
            "id": q.id,
            "question": html.escape(q.question),  # Escape special characters
            "options": [
                html.escape(q.option_a) if q.option_a else "",
                html.escape(q.option_b) if q.option_b else "",
                html.escape(q.option_c) if q.option_c else "",
                html.escape(q.option_d) if q.option_d else ""
            ]
        })
    
    return response
@router.post("/submit-mcq-test/")
def submit_mcq_test(answers: list[MCQAnswer], db: Session = Depends(get_db), current_student: Student = Depends(get_current_student)):
    score = 0
    for ans in answers:
        question = db.query(MCQ).filter(MCQ.id == ans.question_id).first()
        if question and question.correct_option == ans.selected_option:
            score += 1

    db_result = TestResult(student_id=current_student.id, score=score)
    db.add(db_result)
    db.commit()
    
    return {"message": "Test submitted successfully", "score": score}
