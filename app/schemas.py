from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# Student Schema
class StudentBase(BaseModel):
    email: EmailStr
    full_name: str
    mobile_number: str
    language: str

class StudentCreate(BaseModel):
    username: str
    email: str
    password: str
    mobile_number: str  # Add this field
    language: str  # Add this field


class StudentResponse(StudentBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Authentication Schema
class StudentLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# MCQ Test Schema
class MCQBase(BaseModel):
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str

class MCQResponse(MCQBase):
    id: int

    class Config:
        from_attributes = True

class MCQAnswer(BaseModel):
    question_id: int
    selected_option: str

class MCQTestSubmissionResponse(BaseModel):
    message: str
    score: int

# Test Result Schema
class TestResultBase(BaseModel):
    student_id: int
    score: int

class TestResultResponse(TestResultBase):
    id: int

    class Config:
        from_attributes = True

class CodeSubmissionRequest(BaseModel):
    question_id: int
    language: str   
    version: str
    code: str
    test_cases: Optional[List[str]] = None

class CodeRunRequest(BaseModel):
    language: str  
    code: str  
    stdin: Optional[str] = ""  