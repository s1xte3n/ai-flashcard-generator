import os
import logging
from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Query
from app.models import GenerateRequest, GenerateResponse, Flashcard, ChaptersResponse, Chapter
from app.services.pdf_extractor import extract_text_from_pdf, extract_text_from_pages, get_page_count, extract_chapters
from app.services.chunker import TextChunker
from app.services.llm_generator import generate_flashcards_from_chunk
from app.services.deduplicator import deduplicate_flashcards
from app.routers.upload import get_upload_path

router = APIRouter()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_step(step, details=''):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f'[{timestamp}] [GENERATE] {step}: {details}')
    logger.info(f'{step}: {details}')

@router.get("/chapters", response_model=ChaptersResponse)
async def get_chapters(upload_id: str):
    log_step('GET_CHAPTERS', f'upload_id={upload_id}')
    
    try:
        full_path = get_upload_path(upload_id)
    except HTTPException:
        log_step('FILE_NOT_FOUND', upload_id)
        raise HTTPException(404, detail="Upload not found")
    
    total_pages = get_page_count(full_path)
    log_step('PAGE_COUNT', f'Total pages: {total_pages}')
    
    chapters_data = extract_chapters(full_path)
    
    chapters = []
    for i, ch in enumerate(chapters_data):
        chapter = Chapter(
            id=str(i),
            title=ch['title'],
            start_page=ch['start_page'] + 1,
            end_page=ch['end_page'] if ch['end_page'] else total_pages,
            page_range=f"Pages {ch['start_page'] + 1}-{ch['end_page'] if ch['end_page'] else total_pages}"
        )
        chapters.append(chapter)
    
    log_step('CHAPTERS_FOUND', f'{len(chapters)} chapters detected')
    
    return ChaptersResponse(
        upload_id=upload_id,
        total_pages=total_pages,
        chapters=chapters
    )

@router.post("/generate-chapter", response_model=GenerateResponse)
async def generate_chapter_flashcards(
    upload_id: str,
    exam_name: str,
    max_cards: int = 50,
    start_page: int = None,
    end_page: int = None,
    chapter_id: str = None
):
    start_time = datetime.now()
    log_step('CHAPTER_GEN_START', f'exam="{exam_name}", chapter={chapter_id or f"pages {start_page}-{end_page}"}')
    
    try:
        full_path = get_upload_path(upload_id)
    except HTTPException:
        log_step('FILE_NOT_FOUND', upload_id)
        raise HTTPException(404, detail="Upload not found")
    
    total_pages = get_page_count(full_path)
    
    if chapter_id is not None:
        chapters_data = extract_chapters(full_path)
        if int(chapter_id) >= len(chapters_data):
            raise HTTPException(400, detail="Invalid chapter ID")
        ch = chapters_data[int(chapter_id)]
        start_page = ch['start_page']
        end_page = ch['end_page'] if ch['end_page'] else total_pages
        log_step('CHAPTER_INFO', f'"{ch["title"]}" pages {start_page + 1}-{end_page}')
    elif start_page is not None and end_page is not None:
        start_page = max(0, start_page - 1)
        end_page = min(total_pages, end_page)
        log_step('PAGE_RANGE', f'Custom range: pages {start_page + 1}-{end_page}')
    else:
        raise HTTPException(400, detail="Must specify chapter_id or start_page/end_page")
    
    log_step('EXTRACT_TEXT', f'Extracting text from pages {start_page + 1}-{end_page}')
    text = extract_text_from_pages(full_path, start_page, end_page)
    text_chars = len(text)
    text_words = len(text.split())
    log_step('EXTRACT_COMPLETE', f'{text_chars} chars, {text_words} words')
    
    if text_chars < 100:
        log_step('EMPTY_CHAPTER', 'No text found in specified range')
        return GenerateResponse(
            flashcards=[],
            total_processed=0,
            duplicates_removed=0
        )
    
    chunk_tokens = int(os.getenv("CHUNK_TOKENS", 1000))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 100))
    chunker = TextChunker(tokens_per_chunk=chunk_tokens, overlap=chunk_overlap)
    chunks = chunker.chunk(text)
    log_step('CHUNK_COMPLETE', f'{len(chunks)} chunks created')
    
    max_cards = min(max_cards, int(os.getenv("MAX_CARDS", 50)))
    all_cards = []
    
    log_step('LLM_GENERATION', f'Starting generation for {len(chunks)} chunks')
    
    for i, chunk in enumerate(chunks):
        chunk_preview = chunk[:80].replace('\n', ' ') + '...'
        log_step(f'CHUNK_{i+1}/{len(chunks)}', f'Processing (len={len(chunk)}, preview="{chunk_preview}")')
        
        try:
            cards = generate_flashcards_from_chunk(chunk, exam_name)
            all_cards.extend(cards)
            log_step(f'CHUNK_{i+1}_DONE', f'Generated {len(cards)} flashcards')
        except Exception as e:
            log_step(f'CHUNK_{i+1}_ERROR', str(e))
            continue
        
        if len(all_cards) >= max_cards * 2:
            log_step('EARLY_STOP', f'Reached {max_cards * 2} cards')
            break
    
    log_step('DEDUPLICATION', f'Deduplicating {len(all_cards)} cards')
    dedup_threshold = float(os.getenv("DEDUPLICATION_THRESHOLD", 0.85))
    unique_cards = deduplicate_flashcards(all_cards, threshold=dedup_threshold)
    duplicates_removed = len(all_cards) - len(unique_cards)
    log_step('DEDUP_COMPLETE', f'Removed {duplicates_removed}, {len(unique_cards)} unique')
    
    final_cards = unique_cards[:max_cards]
    
    flashcard_objs = [
        Flashcard(
            id=str(i), 
            question=c.get('question', ''), 
            answer=c.get('answer', ''), 
            topic=c.get('topic')
        )
        for i, c in enumerate(final_cards)
    ]
    
    elapsed = (datetime.now() - start_time).total_seconds()
    log_step('CHAPTER_GEN_COMPLETE', f'{elapsed:.2f}s, {len(flashcard_objs)} cards ready')
    
    return GenerateResponse(
        flashcards=flashcard_objs,
        total_processed=len(chunks),
        duplicates_removed=duplicates_removed
    )

@router.post("/generate", response_model=GenerateResponse)
async def generate_flashcards(req: GenerateRequest):
    start_time = datetime.now()
    log_step('GENERATE_START', f'exam="{req.exam_name}", max_cards={req.max_cards}')
    
    try:
        full_path = get_upload_path(req.upload_id)
        file_size = os.path.getsize(full_path)
        log_step('FILE_FOUND', f'{full_path} ({file_size / 1024 / 1024:.2f} MB)')
    except HTTPException:
        log_step('FILE_NOT_FOUND', req.upload_id)
        raise HTTPException(404, detail="Upload not found")
    
    log_step('EXTRACT_TEXT', 'Starting PDF text extraction')
    text = extract_text_from_pdf(full_path)
    text_chars = len(text)
    text_words = len(text.split())
    log_step('EXTRACT_COMPLETE', f'{text_chars} chars, {text_words} words')
    
    chunk_tokens = int(os.getenv("CHUNK_TOKENS", 1000))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 100))
    chunker = TextChunker(tokens_per_chunk=chunk_tokens, overlap=chunk_overlap)
    chunks = chunker.chunk(text)
    log_step('CHUNK_COMPLETE', f'{len(chunks)} chunks created')
    
    max_cards = min(req.max_cards, int(os.getenv("MAX_CARDS", 50)))
    all_cards = []
    
    log_step('LLM_GENERATION', f'Starting generation for {len(chunks)} chunks')
    
    for i, chunk in enumerate(chunks):
        chunk_preview = chunk[:100].replace('\n', ' ') + '...'
        log_step(f'CHUNK_{i+1}/{len(chunks)}', f'Processing (len={len(chunk)}, preview="{chunk_preview}")')
        
        try:
            cards = generate_flashcards_from_chunk(chunk, req.exam_name)
            all_cards.extend(cards)
            log_step(f'CHUNK_{i+1}_DONE', f'Generated {len(cards)} flashcards from this chunk')
        except Exception as e:
            log_step(f'CHUNK_{i+1}_ERROR', str(e))
            continue
        
        if len(all_cards) >= max_cards * 2:
            log_step('EARLY_STOP', f'Reached {max_cards * 2} cards, stopping chunk processing')
            break
    
    log_step('DEDUPLICATION', f'Starting deduplication on {len(all_cards)} cards')
    dedup_threshold = float(os.getenv("DEDUPLICATION_THRESHOLD", 0.85))
    unique_cards = deduplicate_flashcards(all_cards, threshold=dedup_threshold)
    duplicates_removed = len(all_cards) - len(unique_cards)
    log_step('DEDUPLICATION_COMPLETE', f'Removed {duplicates_removed} duplicates, {len(unique_cards)} unique cards')
    
    final_cards = unique_cards[:max_cards]
    log_step('LIMIT_APPLIED', f'Limited to {len(final_cards)} cards (max_cards={max_cards})')
    
    flashcard_objs = [
        Flashcard(
            id=str(i), 
            question=c.get('question', ''), 
            answer=c.get('answer', ''), 
            topic=c.get('topic')
        )
        for i, c in enumerate(final_cards)
    ]
    
    elapsed = (datetime.now() - start_time).total_seconds()
    log_step('GENERATE_COMPLETE', f'Total time: {elapsed:.2f}s, {len(flashcard_objs)} flashcards ready')
    
    return GenerateResponse(
        flashcards=flashcard_objs,
        total_processed=len(chunks),
        duplicates_removed=duplicates_removed
    )
