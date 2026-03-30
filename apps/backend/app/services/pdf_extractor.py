import pdfplumber
import re
import logging
from datetime import datetime
from typing import List, Optional, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_step(step, details=''):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f'[{timestamp}] [PDF] {step}: {details}')
    logger.info(f'{step}: {details}')

CHAPTER_PATTERN = re.compile(
    r'^(?:Chapter\s+\d+|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*[.:]?\s*.+$',
    re.MULTILINE
)

SHORT_CHAPTER_PATTERN = re.compile(
    r'^(Chapter\s+\d+(?:\s*[-–—:]\s*.{1,60}?)?|\d+\.\s+[A-Z][A-Za-z\s]{1,50}|[IVX]+\.?\s+[A-Z][A-Za-z\s]{1,50})',
    re.MULTILINE
)

ANY_CHAPTER_PATTERN = re.compile(
    r'^(?:Chapter\s+\d+|Part\s+[A-Z]|\d{1,2}\.\s*[A-Z]|[IVX]{1,4}\.?\s+[A-Z])',
    re.MULTILINE | re.IGNORECASE
)

def _sanitize_title(title: str) -> str:
    import unicodedata
    cleaned = unicodedata.normalize('NFKD', title)
    cleaned = ''.join(c for c in cleaned if c.isascii() or c == ' ')
    cleaned = re.sub(r'[^\x20-\x7E\s]', '', cleaned)
    return cleaned.strip()[:100]

def extract_text_from_pdf(file_path: str) -> str:
    log_step('EXTRACT_PDF', f'Opening {file_path}')
    text_parts = []
    page_count = 0
    
    with pdfplumber.open(file_path) as pdf:
        page_count = len(pdf.pages)
        log_step('PDF_PAGES', f'Found {page_count} pages')
        
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text:
                cleaned = _clean_text(text)
                text_parts.append(cleaned)
                log_step(f'PAGE_{page_num}', f'Extracted {len(cleaned)} chars')
            else:
                log_step(f'PAGE_{page_num}', 'No text found (possibly image-only)')
    
    full_text = "\n\n".join(text_parts)
    log_step('EXTRACT_DONE', f'Total: {len(full_text)} chars from {len(text_parts)} pages')
    return full_text

def extract_text_from_pages(file_path: str, start_page: int, end_page: int) -> str:
    log_step('EXTRACT_PAGES', f'Opening {file_path}, pages {start_page}-{end_page}')
    text_parts = []
    
    with pdfplumber.open(file_path) as pdf:
        total_pages = len(pdf.pages)
        for page_num in range(start_page, min(end_page, total_pages)):
            page = pdf.pages[page_num]
            text = page.extract_text()
            if text:
                cleaned = _clean_text(text)
                text_parts.append(cleaned)
                log_step(f'PAGE_{page_num + 1}', f'Extracted {len(cleaned)} chars')
    
    full_text = "\n\n".join(text_parts)
    log_step('EXTRACT_DONE', f'Total: {len(full_text)} chars from {len(text_parts)} pages')
    return full_text

def get_page_count(file_path: str) -> int:
    with pdfplumber.open(file_path) as pdf:
        return len(pdf.pages)

def extract_chapters(file_path: str) -> List[Dict]:
    log_step('EXTRACT_TOC', f'Scanning for chapters in {file_path}')
    chapters = []
    
    with pdfplumber.open(file_path) as pdf:
        total_pages = len(pdf.pages)
        current_chapter = None
        
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue
            
            text = _clean_text(text)
            lines = text.split('\n')
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                chapter_match = ANY_CHAPTER_PATTERN.match(line)
                if chapter_match:
                    title = _sanitize_title(line)
                    if len(title) < 5 or len(title) > 120:
                        continue
                    
                    if current_chapter:
                        chapters.append({
                            'title': current_chapter['title'],
                            'start_page': current_chapter['start_page'],
                            'end_page': page_num
                        })
                    
                    current_chapter = {
                        'title': title,
                        'start_page': page_num,
                        'end_page': None
                    }
                    log_step(f'CHAPTER_FOUND', f'"{title}" starting at page {page_num + 1}')
                    break
        
        if current_chapter and current_chapter['end_page'] is None:
            chapters.append({
                'title': current_chapter['title'],
                'start_page': current_chapter['start_page'],
                'end_page': total_pages
            })
    
    if len(chapters) == 0:
        log_step('NO_CHAPTERS', 'No chapters detected, creating page ranges')
        chapters = _create_page_ranges(file_path)
    
    log_step('EXTRACT_TOC_DONE', f'Found {len(chapters)} chapters')
    return chapters

def _create_page_ranges(file_path: str) -> List[Dict]:
    log_step('PAGE_RANGES', 'Creating page ranges based on text availability')
    chapters = []
    
    with pdfplumber.open(file_path) as pdf:
        total_pages = len(pdf.pages)
        text_pages = []
        
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and len(text.strip()) > 50:
                text_pages.append(page_num)
        
        if not text_pages:
            return [{'title': 'Full Document', 'start_page': 0, 'end_page': total_pages}]
        
        chunk_size = 10
        for i in range(0, len(text_pages), chunk_size):
            chunk = text_pages[i:i + chunk_size]
            if chunk:
                start_p = chunk[0]
                end_p = chunk[-1] + 1
                chapters.append({
                    'title': f'Pages {start_p + 1}-{end_p}',
                    'start_page': start_p,
                    'end_page': end_p
                })
    
    log_step('PAGE_RANGES_DONE', f'Created {len(chapters)} page ranges')
    return chapters

def _clean_text(text: str) -> str:
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'Page \d+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
