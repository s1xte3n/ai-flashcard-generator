from fastapi import APIRouter, UploadFile, File, HTTPException
from uuid import uuid4
import os
import glob

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(400, detail="Only PDF files are supported")
    
    upload_id = str(uuid4())
    safe_filename = f"{upload_id}_{file.filename}"
    file_path = os.path.join(upload_dir, safe_filename)
    
    content = await file.read()
    
    max_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", 50))
    if len(content) > max_size_mb * 1024 * 1024:
        raise HTTPException(400, detail="File too large")
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    return {"upload_id": upload_id, "filename": file.filename}

def get_upload_path(upload_id: str) -> str:
    upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
    pattern = os.path.join(upload_dir, f"{upload_id}_*")
    matches = glob.glob(pattern)
    if not matches:
        raise HTTPException(404, detail="Upload not found")
    return matches[0]
