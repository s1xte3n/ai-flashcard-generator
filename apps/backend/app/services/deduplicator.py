from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging
from datetime import datetime
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_step(step, details=''):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f'[{timestamp}] [DEDUP] {step}: {details}')
    logger.info(f'{step}: {details}')

def deduplicate_flashcards(flashcards: List[Dict], threshold: float = 0.85) -> List[Dict]:
    if len(flashcards) <= 1:
        log_step('SKIPPED', 'Only 1 or fewer cards, skipping deduplication')
        return flashcards
    
    log_step('VECTORIZING', f'Creating TF-IDF vectors for {len(flashcards)} flashcards')
    
    texts = [f"{f['question']} {f['answer']}" for f in flashcards]
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    log_step('SIMILARITY', f'Computing cosine similarity matrix ({len(flashcards)}x{len(flashcards)})')
    sim_matrix = cosine_similarity(tfidf_matrix)
    
    to_remove = set()
    n = len(flashcards)
    duplicates_found = 0
    for i in range(n):
        for j in range(i + 1, n):
            if sim_matrix[i, j] > threshold:
                to_remove.add(j)
                duplicates_found += 1
    
    log_step('MARKED', f'Found {duplicates_found} duplicate pairs, marking {len(to_remove)} cards for removal')
    
    unique = [f for idx, f in enumerate(flashcards) if idx not in to_remove]
    log_step('FILTERED', f'Removed {len(flashcards) - len(unique)} duplicates, {len(unique)} unique cards remain')
    
    return unique
