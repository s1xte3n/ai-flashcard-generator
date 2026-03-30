import os
import requests
import json
import logging
from datetime import datetime
from typing import List, Dict

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "mistral:7b")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_step(step, details=''):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f'[{timestamp}] [LLM] {step}: {details}')
    logger.info(f'{step}: {details}')

SIMPLE_PROMPT = """Generate 1-3 exam flashcards from this text.
Output as valid JSON array like: [{\"question\": \"...?\", \"answer\": \"...\"}]

Text: {chunk_text}

Only output JSON, no explanation."""

def generate_flashcards_from_chunk(
    chunk: str, 
    exam_name: str, 
    model: str = DEFAULT_MODEL,
    temperature: float = 0.3
) -> List[Dict]:
    chunk_chars = len(chunk)
    chunk_words = len(chunk.split())
    
    if chunk_chars < 50:
        log_step('SKIP_EMPTY', 'Chunk too small')
        return []
    
    prompt = SIMPLE_PROMPT.format(chunk_text=chunk[:3000])
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": temperature, "num_predict": 500}
    }
    
    log_step('LLM_CALL', f'Sending {min(chunk_chars, 3000)} chars to {model}...')
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        text = result.get("response", "").strip()
        
        if not text:
            log_step('LLM_EMPTY', 'Empty response')
            return []
        
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        if not text:
            log_step('LLM_EMPTY_CLEANED', 'Response empty after cleaning')
            return []
        
        cards = json.loads(text)
        if not isinstance(cards, list):
            log_step('LLM_INVALID_FORMAT', 'Response is not a list')
            return []
        
        valid_cards = [c for c in cards if isinstance(c, dict) and c.get('question') and c.get('answer')]
        log_step('LLM_RESPONSE', f'Received {len(valid_cards)} valid flashcards')
        
        return valid_cards
    
    except requests.Timeout:
        log_step('LLM_TIMEOUT', f'Timed out after 60s - model may be slow or overloaded')
        return []
    except requests.ConnectionError as e:
        log_step('LLM_CONNECTION_ERROR', 'Cannot connect to Ollama - check if it is running')
        return []
    except json.JSONDecodeError as e:
        log_step('LLM_JSON_ERROR', f'Invalid JSON: {str(text)[:200]}')
        return []
    except Exception as e:
        log_step('LLM_ERROR', f'{type(e).__name__}: {str(e)[:100]}')
        return []

def check_ollama_health() -> bool:
    try:
        response = requests.get(OLLAMA_URL.replace("/api/generate", "/api/tags"), timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False
