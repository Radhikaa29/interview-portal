from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from routers import auth, student, mcq, coding , admin
import os
from fastapi.templating import Jinja2Templates


app = FastAPI()




# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory="templates")

# Include Routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(student.router, prefix="/student", tags=["Student"])
app.include_router(mcq.router, prefix="/mcq", tags=["MCQ Test"])
app.include_router(coding.router, prefix="/coding", tags=["Coding Test"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/mcq-test")
def mcq_test(request: Request):
    return templates.TemplateResponse("mcq-test.html", {"request": request})

@app.get("/coding-test")
def coding_test(request: Request):
    return templates.TemplateResponse("coding-test.html", {"request": request})

@app.get("/code-editor")
def code_editor(request: Request, questionId: int):
    print(f"Received questionId: {questionId}") 
    return templates.TemplateResponse("code-editor.html", {"request": request, "questionId": questionId})

@app.get("/admin-login")
def admin_login(request: Request):
    return templates.TemplateResponse("admin-login.html",{"request": request})
    
@app.get("/admin-dashboard")
def admin_dashboard(request:Request) :
    return templates.TemplateResponse("admin-dashboard.html",{"request" : request})

