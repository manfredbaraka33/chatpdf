# from fastapi import FastAPI, UploadFile, File, BackgroundTasks
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from services import process_pdfs, ask_question

# app = FastAPI(title="PDF Q&A API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Track backend status
# processing_status = {"ready": True}  # Initially ready

# @app.get("/status/")
# async def get_status():
#     return {"ready": processing_status["ready"]}

# @app.get("/")
# async def home():
#     return {"message":"API working fine!"}

# @app.post("/upload/")
# async def upload_pdfs(files: list[UploadFile] = File(...), background_tasks: BackgroundTasks = None):
#     # Set status to not ready
#     processing_status["ready"] = False

#     # Function to run in background
#     def process_files():
#         process_pdfs(files)
#         processing_status["ready"] = True  # Set ready when done

#     # Schedule background task
#     background_tasks.add_task(process_files)

#     return {"message": f"Processing {len(files)} PDFs..."}  # Returns immediately

# class Question(BaseModel):
#     query: str


# @app.post("/ask/")
# async def ask_pdf_question(question: Question):
#     if not processing_status["ready"]:
#         return {"answer": "PDFs are still being processed. Please wait..."}

#     result = ask_question(question.query)
#     return result





import anyio # <-- NEW: For running synchronous code asynchronously
from fastapi import FastAPI, UploadFile, File # BackgroundTasks is removed
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services import process_pdfs, ask_question
from starlette.background import BackgroundTasks # If you use it, but we are replacing it

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
async def upload_pdfs(files: list[UploadFile] = File(...)): # BackgroundTasks argument is REMOVED
    # Set status to not ready
    processing_status["ready"] = False
    
    try:
        # --- CRITICAL FIX: Use run_sync to move the heavy, blocking work to a background thread ---
        # The return value (total_chunks) is captured after the process completes.
        total_chunks = await anyio.to_thread.run_sync(process_pdfs, files)
        
        # This line only runs AFTER all PDF processing, embedding, and adding is finished.
        processing_status["ready"] = True
        
        return {"message": f"Successfully processed {len(files)} PDFs.",
                "chunks": total_chunks}
    
    except Exception as e:
        # If the background process crashes, set status to true (so the service isn't stuck) 
        # and re-raise the error for the client to see the failure.
        processing_status["ready"] = True 
        print(f"ERROR: PDF processing failed: {e}")
        # Re-raise the exception so FastAPI handles it and returns a 500
        raise e 


class Question(BaseModel):
    query: str


@app.post("/ask/")
async def ask_pdf_question(question: Question):
    if not processing_status["ready"]:
        return {"answer": "PDFs are still being processed. Please wait..."}

    result = ask_question(question.query)
    return result
