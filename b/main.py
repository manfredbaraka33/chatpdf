from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services import process_pdfs, ask_question

app = FastAPI(title="PDF Q&A API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track backend status
processing_status = {"ready": True}  # Initially ready

@app.get("/status/")
async def get_status():
    return {"ready": processing_status["ready"]}

@app.get("/")
async def home():
    return {"message":"API working fine!"}

@app.post("/upload/")
async def upload_pdfs(files: list[UploadFile] = File(...), background_tasks: BackgroundTasks = None):
    # Set status to not ready
    processing_status["ready"] = False

    # Function to run in background
    def process_files():
        process_pdfs(files)
        processing_status["ready"] = True  # Set ready when done

    # Schedule background task
    background_tasks.add_task(process_files)

    return {"message": f"Processing {len(files)} PDFs..."}  # Returns immediately

class Question(BaseModel):
    query: str


@app.post("/ask/")
async def ask_pdf_question(question: Question):
    if not processing_status["ready"]:
        return {"answer": "PDFs are still being processed. Please wait..."}

    result = ask_question(question.query)
    return result

