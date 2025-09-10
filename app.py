from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import json, random, os, traceback

app = FastAPI(title="QnA Generator API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Path to questions.json
QUESTIONS_FILE = "questions.json"
questions_data = []

# Load questions at startup
try:
    print(f"Loading questions from {QUESTIONS_FILE}...")
    with open(QUESTIONS_FILE, "r") as f:
        data = json.load(f)
        questions_data = data.get("questions", [])
    print(f"Loaded {len(questions_data)} questions successfully.")
except Exception as e:
    print(f"Error loading questions.json: {e}")
    traceback.print_exc()
    questions_data = []

# Serve frontend automatically at /
@app.get("/")
async def serve_frontend():
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"error": "index.html not found in /static"}, status_code=404)

# API endpoint to generate a random question
@app.get("/api/generate_question")
async def generate_question():
    try:
        if not questions_data:
            return JSONResponse(
                {"error": "No questions available or questions.json missing/invalid."},
                status_code=500
            )

        question = random.choice(questions_data)
        image_path = question.get("image", "")
        question_out = {
            "question": question.get("question", ""),
            "options": [f"{k}. {v}" for k, v in question.get("options", {}).items()],
            "correct_answer": question.get("answer", ""),
            "brief_solution": question.get("brief_explanation", ""),
            "detailed_explanation": question.get("detailed_explanation", ""),
            "image_url": f"/static/{image_path}" if image_path else ""
        }
        return question_out
    except Exception as e:
        print("Exception in generate_question:", e)
        traceback.print_exc()
        return JSONResponse(
            {"error": f"Failed to generate question: {str(e)}"},
            status_code=500
        )
