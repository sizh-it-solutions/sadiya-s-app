from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import json, random, os

app = FastAPI(title="QnA Generator API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Serve index.html at root
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ----------------------
# Helper: Load questions
# ----------------------
def load_questions():
    file_path = "questions.json"
    if not os.path.exists(file_path):
        raise FileNotFoundError("Questions file not found.")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Questions file must be a list of questions.")
        return data


# ----------------------
# Helper: Pick random question
# ----------------------
def get_random_question():
    questions = load_questions()
    if not questions:
        raise ValueError("No questions available.")
    q = random.choice(questions)
    return {
        "question": q.get("question", ""),
        "options": [f"{key}. {val}" for key, val in q.get("options", {}).items()],
        "correct_answer": q.get("answer", ""),
        "brief_solution": q.get("brief_explanation", ""),
        "detailed_explanation": q.get("detailed_explanation", "")
    }


# ----------------------
# Single API endpoint
# ----------------------
@app.get("/api/generate_question")
def generate_question():
    try:
        return get_random_question()
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
