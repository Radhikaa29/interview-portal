from sqlalchemy import Column, Integer, Text, String, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime 



class Student(Base):  # Renamed User to Student
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    username = Column(String, nullable=False)
    mobile_number = Column(String, unique=True, nullable=False)  
    language = Column(String, nullable=False)  
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    test_results = relationship("TestResult", back_populates="student")  
    coding_results = relationship("CodingResult", back_populates="student", cascade="all, delete-orphan")  # ✅ Added Relationship


class MCQ(Base):
    __tablename__ = "mcqs"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    option_a = Column(String, nullable=False)
    option_b = Column(String, nullable=False)
    option_c = Column(String, nullable=False)
    option_d = Column(String, nullable=False)
    correct_option = Column(String, nullable=False)  # Store correct answer (A, B, C, or D)


class TestResult(Base):
    __tablename__ = "test_results"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id")) 
    score = Column(Integer, nullable=False) 
    
    student = relationship("Student", back_populates="test_results")  # ✅ Fixed ForeignKey reference


class CodingQuestion(Base):
    __tablename__ = "coding_questions"

    question_id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)

    test_cases = relationship("TestCase", back_populates="coding_question", cascade="all, delete-orphan")
    coding_results = relationship("CodingResult", back_populates="coding_question", cascade="all, delete-orphan")  # ✅ Added Relationship


class TestCase(Base):
    __tablename__ = "test_cases"

    testcase_id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("coding_questions.question_id", ondelete="CASCADE"))
    input_data = Column(String, nullable=False)
    expected_output = Column(String, nullable=False)
    description = Column(Text, nullable=True) 

    coding_question = relationship("CodingQuestion", back_populates="test_cases")


class CodingResult(Base):
    __tablename__ = "coding_results"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)  # ✅ Fixed ForeignKey reference
    question_id = Column(Integer, ForeignKey("coding_questions.question_id"), nullable=False)  # ✅ Fixed ForeignKey reference
    language = Column(String, nullable=False)  # Example: "python", "cpp"
    code_submitted = Column(Text, nullable=False)  # Stores the submitted code
    status = Column(String, nullable=False, default="Failed")  # "Passed" or "Failed"
    timestamp = Column(DateTime, default=datetime.utcnow)  # Stores submission time

    student = relationship("Student", back_populates="coding_results")  # ✅ Fixed Reference
    coding_question = relationship("CodingQuestion", back_populates="coding_results")  # ✅ Fixed Reference

