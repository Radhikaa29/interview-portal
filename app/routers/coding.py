from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import CodingQuestion, TestCase,CodingResult,Student
from schemas import CodeSubmissionRequest,CodeRunRequest
from auth import get_current_student
import requests
import random
from auth import get_db

router = APIRouter()

PISTON_API_URL = "https://emkc.org/api/v2/piston/execute"

@router.get("/coding-question/")
def get_random_coding_questions(db: Session = Depends(get_db)):
    questions = db.query(CodingQuestion).all()

    if not questions:
        return []  # ✅ Always return a list to prevent "NoneType" issues

    random_questions = random.sample(questions, min(5, len(questions)))  

    result = []
    for q in random_questions:
        test_cases = db.query(TestCase).filter(TestCase.question_id == q.question_id).all()
        result.append({
            "question_id": q.question_id,
            "question": q.question,
            "test_cases": [{"input": tc.input_data, "expected_output": tc.expected_output} for tc in test_cases]
        })

    return result

@router.post("/submit-code")
def execute_code(submission: CodeSubmissionRequest, db: Session = Depends(get_db)):
    question = db.query(CodingQuestion).filter(CodingQuestion.question_id == submission.question_id).first()
    if not question:
        return {"error": "Invalid question ID"}
    
    test_cases = db.query(TestCase).filter(TestCase.question_id == submission.question_id).all()
    if not test_cases:
        return {"error": "No test cases found"}

    results = []

    for test_case in test_cases:
        payload = {
            "language": submission.language,
            "version": submission.version,
            "files": [{"name": "main", "content": submission.code}],
            "stdin": test_case.input_data                      
        }
        
        response = requests.post(PISTON_API_URL, json=payload)
        api_response = response.json()

        expected_output = test_case.expected_output.strip()
        actual_output = api_response.get("run", {}).get("stdout", "").strip()
        success = expected_output == actual_output

        results.append({
            "input": test_case.input_data,
            "expected_output": expected_output,
            "actual_output": actual_output,
            "success": success
        })

    return {"question": question.question, "test_results": results}
@router.get("/question/{question_id}")
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(CodingQuestion).filter(CodingQuestion.question_id == question_id).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    test_cases = db.query(TestCase).filter(TestCase.question_id == question_id).all()

    return {
        "question_id": question.question_id,
        "question": question.question,
        "test_cases": [{"input": tc.input_data, "expected_output": tc.expected_output} for tc in test_cases]
    }


@router.post("/coding/submit/{question_id}")
async def submit_code(
    question_id: int, 
    code_data: dict, 
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_student)  # Ensure only logged-in students can submit
):
    """
    Handles code submission by running against stored test cases.
    Stores "Passed" or "Failed" in the database based on the results.
    """

    # Extract submitted code and language
    language = code_data.get("language")
    submitted_code = code_data.get("code")

    # Fetch the question and test cases from the database
    question = db.query(CodingQuestion).filter(CodingQuestion.question_id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    test_cases = db.query(TestCase).filter(TestCase.question_id == question_id).all()

    if not test_cases:
        raise HTTPException(status_code=404, detail="No test cases found for this question")

    # Define language settings for Piston API
    language_settings = {
        "python": { "version": "3.10.0", "fileName": "main.py" },
        "javascript": { "version": "18.15.0", "fileName": "main.js" },
        "cpp": { "version": "10.2.0", "fileName": "main.cpp" },
        "java": { "version": "15.0.2", "fileName": "Main.java" },
        "php": { "version": "8.2.3", "fileName": "main.php" }
    }

    if language not in language_settings:
        raise HTTPException(status_code=400, detail="Unsupported programming language")

    # Fetch the correct version and file name
    lang_version = language_settings[language]["version"]
    file_name = language_settings[language]["fileName"]

    # Check for Java-specific requirement
    if language == "java" and "class Main" not in submitted_code:
        raise HTTPException(status_code=400, detail="Java code must include class Main with a main method.")

    # Run the submitted code against each test case
    all_passed = True

    for test_case in test_cases:
        request_body = {
            "language": language,
            "version": lang_version,
            "files": [{ "name": file_name, "content": submitted_code }],
            "stdin": test_case.input_data
        }

        # Execute the code using Piston API
        response = requests.post(PISTON_API_URL, json=request_body)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error communicating with code execution server")

        result = response.json()

        # Extract output and compare with expected output
        output = result.get("run", {}).get("output", "").strip()
        expected_output = test_case.expected_output.strip()

        print(f"Test Case Input: {test_case.input_data}")  # Debugging
        print(f"Expected Output: {expected_output}")  # Debugging
        print(f"Actual Output: {output}") 

        if output != expected_output:
            all_passed = False
            break

    # Store the result in the database
    coding_result = CodingResult(
        student_id=current_user.id,
        question_id=question_id,
        language=language,
        code_submitted=submitted_code,
        status="Passed" if all_passed else "Failed"
    )

    db.add(coding_result)
    db.commit()

    return { "status": "Passed" if all_passed else "Failed" }

@router.post("/coding/run")
async def run_code(
    code_data: CodeRunRequest,
    current_user: Student = Depends(get_current_student)  # Ensure only logged-in students can run code
):
    """
    Handles running the user's code and returns the output.
    This does NOT check against test cases or store results in the database.
    """

    # Extract submitted code and language
    language = code_data.language
    submitted_code = code_data.code
    stdin = code_data.stdin  # Optional input (for testing)

    # Define language settings for Piston API
    language_settings = {
        "python": { "version": "3.10.0", "fileName": "main.py" },
        "javascript": { "version": "18.15.0", "fileName": "main.js" },
        "cpp": { "version": "10.2.0", "fileName": "main.cpp" },
        "java": { "version": "15.0.2", "fileName": "Main.java" },
        "php": { "version": "8.2.3", "fileName": "main.php" }
    }

    if language not in language_settings:
        raise HTTPException(status_code=400, detail="Unsupported programming language")

    # Fetch the correct version and file name
    lang_version = language_settings[language]["version"]
    file_name = language_settings[language]["fileName"]

    # Check for Java-specific requirement
    if language == "java" and "class Main" not in submitted_code:
        raise HTTPException(status_code=400, detail="Java code must include class Main with a main method.")

    # Prepare request body for Piston API
    request_body = {
        "language": language,
        "version": lang_version,
        "files": [{ "name": file_name, "content": submitted_code }],
        "stdin": stdin or ""  # Use provided input or empty string
    }

    # Execute the code using Piston API
    response = requests.post(PISTON_API_URL, json=request_body)
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error communicating with code execution server")

    result = response.json()

    # Extract output and errors
    output = result.get("run", {}).get("output", "").strip()
    stderr = result.get("run", {}).get("stderr", "").strip()

    return { "output": output, "error": stderr }
