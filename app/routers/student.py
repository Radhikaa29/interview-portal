from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from auth import get_current_student, get_db
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard")
def dashboard(request: Request, current_student=Depends(get_current_student)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "username": current_student.username})
