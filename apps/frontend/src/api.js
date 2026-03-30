const API_URL = 'http://localhost:8003/api';

export const api = {
  async uploadPdf(file) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_URL}/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      throw new Error('Upload failed');
    }
    return res.json();
  },

  async getChapters(uploadId) {
    const res = await fetch(`${API_URL}/chapters?upload_id=${uploadId}`);
    if (!res.ok) {
      throw new Error('Failed to get chapters');
    }
    return res.json();
  },

  async generateChapter(uploadId, examName, chapterId, maxCards = 50) {
    const params = new URLSearchParams({
      upload_id: uploadId,
      exam_name: examName,
      chapter_id: chapterId,
      max_cards: maxCards.toString(),
    });
    const res = await fetch(`${API_URL}/generate-chapter?${params}`, {
      method: 'POST',
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Generation failed');
    }
    return res.json();
  },

  async generateFlashcards(uploadId, examName, maxCards = 50) {
    const res = await fetch(`${API_URL}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        upload_id: uploadId,
        exam_name: examName,
        max_cards: maxCards,
      }),
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Generation failed');
    }
    return res.json();
  },

  async exportCSV(flashcards) {
    const params = new URLSearchParams({
      flashcards: JSON.stringify(flashcards),
    });
    const res = await fetch(`${API_URL}/export/csv?${params}`);
    return res.blob();
  },

  async exportPDF(flashcards) {
    const params = new URLSearchParams({
      flashcards: JSON.stringify(flashcards),
    });
    const res = await fetch(`${API_URL}/export/pdf?${params}`);
    return res.blob();
  },
};
