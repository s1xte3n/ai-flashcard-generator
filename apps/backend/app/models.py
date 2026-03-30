from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UploadResponse(BaseModel):
    upload_id: str
    filename: str

class GenerateRequest(BaseModel):
    upload_id: str
    exam_name: str
    max_cards: int = 50

class Chapter(BaseModel):
    id: str
    title: str
    start_page: int
    end_page: int
    page_range: str

class ChaptersResponse(BaseModel):
    upload_id: str
    total_pages: int
    chapters: List[Chapter]

class GenerateRequest(BaseModel):
    upload_id: str
    exam_name: str
    max_cards: int = 50
    start_page: Optional[int] = None
    end_page: Optional[int] = None
    chapter_id: Optional[str] = None

class Flashcard(BaseModel):
    id: str
    question: str
    answer: str
    topic: Optional[str] = None

class GenerateResponse(BaseModel):
    flashcards: List[Flashcard]
    total_processed: int
    duplicates_removed: int
