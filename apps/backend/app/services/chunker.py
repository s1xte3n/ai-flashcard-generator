import tiktoken
import logging
from datetime import datetime
from typing import List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_step(step, details=''):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f'[{timestamp}] [CHUNK] {step}: {details}')
    logger.info(f'{step}: {details}')

class TextChunker:
    def __init__(self, tokens_per_chunk: int = 1000, overlap: int = 100):
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.tokens_per_chunk = tokens_per_chunk
        self.overlap = overlap

    def chunk(self, text: str) -> List[str]:
        tokens = self.encoding.encode(text)
        total_tokens = len(tokens)
        log_step('TOKENIZE', f'Converted text to {total_tokens} tokens')
        
        chunks = []
        for i in range(0, len(tokens), self.tokens_per_chunk - self.overlap):
            chunk_tokens = tokens[i:i + self.tokens_per_chunk]
            chunk_text = self.encoding.decode(chunk_tokens)
            if len(chunk_text.strip()) > 100:
                chunks.append(chunk_text)
        
        log_step('CHUNK_DONE', f'Created {len(chunks)} chunks (size={self.tokens_per_chunk}, overlap={self.overlap})')
        return chunks

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))
