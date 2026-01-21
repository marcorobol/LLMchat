from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import time
import os
from dotenv import load_dotenv

# Load env variables (API keys)
load_dotenv()

from llm.factory import get_llm_provider
from utils.ocr import extract_text_from_image
from utils.pdf import extract_text_from_pdf

# ... (imports) ...

app = FastAPI()

# Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    print(f"Incoming Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    print(f"Request handled in {process_time:.2f}ms - Status: {response.status_code}")
    
    return response

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for simple testing
UPLOADED_DOCS = {}

@app.post("/upload/documents")
async def upload_documents(files: List[UploadFile] = File(...)):
    # Simulate processing time
    uploaded_names = []
    for file in files:
        content = await file.read()
        # If it's an image, try OCR
        if file.content_type.startswith("image/"):
            text = extract_text_from_image(content)
            UPLOADED_DOCS[file.filename] = text
        elif file.content_type == "application/pdf" or file.filename.lower().endswith(".pdf"):
            text = extract_text_from_pdf(content)
            UPLOADED_DOCS[file.filename] = text
        else:
            # Assume text/pdf (for now just decoding text, PDF parsing not fully implemented in this step)
            try:
                text = content.decode("utf-8")
                UPLOADED_DOCS[file.filename] = text
            except:
                UPLOADED_DOCS[file.filename] = "[Binary Content / Parser Error]"
        
        uploaded_names.append(file.filename)
        
    return {"message": f"Successfully uploaded {len(files)} documents", "filenames": uploaded_names}

@app.post("/upload/laws")
async def upload_laws(files: List[UploadFile] = File(...)):
    # Similar logic for laws
    uploaded_names = []
    for file in files:
        uploaded_names.append(file.filename)
from utils.lmstudio_utils import get_model_context_length, get_models_list, load_model, unload_model

# ...

@app.post("/models/{model_id}/load")
async def load_model_endpoint(model_id: str):
    """
    Load a model in LM Studio.
    """
    result = await load_model(model_id)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@app.post("/models/{model_id}/unload")
async def unload_model_endpoint(model_id: str):
    """
    Unload a model from LM Studio.
    """
    result = await unload_model(model_id)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@app.get("/models")
async def list_models():
    """
    Retrieves all available models with their information including state.
    """
    models = await get_models_list()
    return {"data": models}

@app.get("/model/info")
async def get_model_info(model_id: str):
    """
    Retrieves information about a specific model using the LM Studio SDK.
    """
    context_length = await get_model_context_length(model_id)
    return {
        "model_id": model_id,
        "context_length": context_length
    }


@app.post("/ask")
async def ask_question(
    question: str = Form(...), 
    context_files: List[str] = Form([]),
    model_provider: str = Form("local"), # openai, local, zai, custom_openai
    model_id: Optional[str] = Form(None),
    api_key: Optional[str] = Form(None),
    base_url: Optional[str] = Form(None),
    context_limit: Optional[int] = Form(None)
):
    try:
        # 1. Gather Context
        context_texts = []
        
        # Filter files if context_files is provided
        files_to_use = UPLOADED_DOCS.keys()
        if context_files:
             # context_files is a list of strings, but due to Form() it might be ["file1,file2"] or ["file1", "file2"] depending on frontend
             # In Vue it's sending multiple params so it should be a list
             files_to_use = [f for f in context_files if f in UPLOADED_DOCS]
        
        total_chars = 0
        # Use provided limit or default to 12000 chars (~3k tokens)
        MAX_CHARS = int(context_limit) if context_limit else 12000 

        for filename in files_to_use:
            text = UPLOADED_DOCS[filename]
            # Truncate individual file if huge
            if len(text) > MAX_CHARS:
                text = text[:MAX_CHARS] + "... [Truncated]"
            
            # Check total accumulation
            if total_chars + len(text) > MAX_CHARS:
                remaining = MAX_CHARS - total_chars
                if remaining > 100:
                    text = text[:remaining] + "... [Total Context Limit Reached]"
                    context_texts.append(f"--- Document: {filename} ---\n{text}\n")
                break
            
            context_texts.append(f"--- Document: {filename} ---\n{text}\n")
            total_chars += len(text)

        # 2. Initialize Provider
        provider = get_llm_provider(model_provider, api_key=api_key, model=model_id, base_url=base_url)

        # 3. Generate Response
        # (Pass empty images list for now unless we handle direct image upload in chat)
        result = await provider.generate_response(prompt=question, context_documents=context_texts)
        
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Backend is running"}
