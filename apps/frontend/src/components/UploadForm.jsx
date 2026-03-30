import { useState } from 'react';
import { api } from '../api';

export default function UploadForm({ onGenerated, setIsGenerating }) {
  const [file, setFile] = useState(null);
  const [examName, setExamName] = useState('');
  const [maxCards, setMaxCards] = useState(50);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState(null);
  const [uploadId, setUploadId] = useState(null);
  const [chapters, setChapters] = useState([]);
  const [selectedChapter, setSelectedChapter] = useState(null);
  const [generatedChapterIds, setGeneratedChapterIds] = useState(new Set());
  const [allFlashcards, setAllFlashcards] = useState([]);
  const [view, setView] = useState('upload');

  const log = (step, details = '') => {
    const timestamp = new Date().toLocaleTimeString();
    console.log(`[${timestamp}] [FRONTEND] ${step}${details ? ': ' + details : ''}`);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    setError('');
    if (!file) {
      setError('Please select a PDF file');
      return;
    }
    if (!examName.trim()) {
      setError('Please enter an exam name');
      return;
    }
    setIsGenerating(true);
    try {
      log('UPLOAD_START', file.name);
      setProgress({ step: 'upload', message: 'Uploading PDF...' });
      const uploadResult = await api.uploadPdf(file);
      log('UPLOAD_SUCCESS', `upload_id: ${uploadResult.upload_id}`);
      setUploadId(uploadResult.upload_id);
      setProgress({ step: 'chapters', message: 'Detecting chapters...' });
      log('GET_CHAPTERS', 'Fetching chapter list from PDF');
      const chaptersData = await api.getChapters(uploadResult.upload_id);
      log('CHAPTERS_FOUND', `${chaptersData.chapters.length} chapters detected`);
      setChapters(chaptersData.chapters);
      setProgress(null);
      setView('chapters');
    } catch (err) {
      log('ERROR', err.message || 'Unknown error');
      setError(err.message || 'Upload failed');
      setProgress(null);
    } finally {
      setIsGenerating(false);
    }
  };
  const handleGenerateChapter = async (chapterId) => {
    setError('');
    setIsGenerating(true);
    setSelectedChapter(chapterId);
    try {
      const chapter = chapters.find(c => c.id === chapterId);
      log('CHAPTER_START', `"${chapter.title}" (pages ${chapter.start_page}-${chapter.end_page})`);
      setProgress({ step: 'generating', message: `Generating flashcards for: ${chapter.title}...` });
      const result = await api.generateChapter(
        uploadId,
        examName,
        chapterId,
        maxCards
      );
      log('CHAPTER_COMPLETE', `Generated ${result.flashcards.length} flashcards`);
      log('DEDUPLICATION', `Removed ${result.duplicates_removed} duplicates`);
      const newCards = result.flashcards.map((card, idx) => ({
        ...card,
        topic: chapter.title,
        id: `${chapterId}-${idx}`
      }));
      setAllFlashcards(prev => [...prev, ...newCards]);
      setGeneratedChapterIds(prev => new Set(prev).add(chapterId));
      setProgress(null);
      onGenerated([...allFlashcards, ...newCards], {
        processed: result.total_processed,
        duplicates: result.duplicates_removed,
      });
    } catch (err) {
      log('ERROR', err.message || 'Unknown error');
      setError(err.message || 'Generation failed');
    } finally {
      setIsGenerating(false);
      setSelectedChapter(null);
    }
  };
  const handleNextChapter = () => {
    setError('');
    setView('chapters');
  };
  const handleStartOver = () => {
    setFile(null);
    setUploadId(null);
    setChapters([]);
    setSelectedChapter(null);
    setGeneratedChapterIds(new Set());
    setAllFlashcards([]);
    setView('upload');
    setError('');
    setProgress(null);
    onGenerated([], { processed: 0, duplicates: 0 });
  };
  if (view === 'chapters') {
    const remainingChapters = chapters.filter(c => !generatedChapterIds.has(c.id));
    const currentChapter = chapters.find(c => c.id === selectedChapter);
    return (
      <div className="bg-white p-6 rounded-lg shadow-md max-w-2xl mx-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Select a Chapter</h2>
          <button
            onClick={handleStartOver}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            Start Over
          </button>
        </div>
        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded mb-4 text-sm">
            {error}
          </div>
        )}
        {progress && progress.step === 'generating' && (
          <div className="bg-blue-50 text-blue-700 p-3 rounded mb-4 text-sm flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-700 mr-2"></div>
            {progress.message}
          </div>
        )}
        {currentChapter && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
            <h3 className="font-semibold text-green-800 mb-2">Generated: {currentChapter.title}</h3>
            <p className="text-sm text-green-700 mb-3">
              {allFlashcards.filter(c => c.topic === currentChapter.title).length} flashcards created
            </p>
            <button
              onClick={handleNextChapter}
              className="bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 text-sm"
            >
              Continue to Next Chapter
            </button>
          </div>
        )}
        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2">
            Total flashcards: <strong>{allFlashcards.length}</strong> | 
            Chapters completed: <strong>{generatedChapterIds.size}</strong>/<strong>{chapters.length}</strong>
          </p>
        </div>
        {remainingChapters.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-600 mb-4">All chapters completed!</p>
            <div className="flex justify-center gap-4">
              <button
                onClick={() => onGenerated(allFlashcards, { processed: 0, duplicates: 0 })}
                className="bg-blue-600 text-white py-2 px-6 rounded hover:bg-blue-700"
              >
                Review All Flashcards ({allFlashcards.length})
              </button>
              <button
                onClick={handleStartOver}
                className="bg-gray-500 text-white py-2 px-6 rounded hover:bg-gray-600"
              >
                Start New PDF
              </button>
            </div>
          </div>
        ) : (
          <div className="max-h-96 overflow-y-auto border rounded-lg">
            {chapters.map((chapter) => {
              const isGenerated = generatedChapterIds.has(chapter.id);
              const isSelected = selectedChapter === chapter.id;
              return (
                <div
                  key={chapter.id}
                  className={`p-3 border-b flex justify-between items-center ${
                    isGenerated ? 'bg-green-50' : isSelected ? 'bg-blue-50' : 'hover:bg-gray-50'
                  }`}
                >
                  <div>
                    <p className="font-medium text-sm">{chapter.title}</p>
                    <p className="text-xs text-gray-500">{chapter.page_range}</p>
                  </div>
                  <div>
                    {isGenerated ? (
                      <span className="text-green-600 text-sm font-medium">
                        {allFlashcards.filter(c => c.topic === chapter.title).length} cards
                      </span>
                    ) : isSelected ? (
                      <div className="flex items-center text-blue-600 text-sm">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                        Generating...
                      </div>
                    ) : (
                      <button
                        onClick={() => handleGenerateChapter(chapter.id)}
                        className="bg-blue-600 text-white py-1 px-3 rounded text-sm hover:bg-blue-700"
                      >
                        Generate
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  }
  return (
    <div className="bg-white p-6 rounded-lg shadow-md max-w-md mx-auto">
      <h2 className="text-xl font-semibold mb-4">Upload PDF Textbook</h2>   
      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded mb-4 text-sm">
          {error}
        </div>
      )}
      {progress && progress.step !== 'complete' && (
        <div className="bg-blue-50 text-blue-700 p-3 rounded mb-4 text-sm flex items-center">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-700 mr-2"></div>
          {progress.message}
        </div>
      )}
      <form onSubmit={handleUpload}>
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            PDF File
          </label>
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => {
              setFile(e.target.files?.[0] || null);
              if (e.target.files?.[0]) {
                log('FILE_SELECTED', `${e.target.files[0].name} (${(e.target.files[0].size / 1024 / 1024).toFixed(2)} MB)`);
              }
            }}
            className="w-full p-2 border border-gray-300 rounded text-sm"
          />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Exam Name / Code
          </label>
          <input
            type="text"
            value={examName}
            onChange={(e) => setExamName(e.target.value)}
            placeholder="e.g., USMLE Step 1, AP Biology, CompTIA A+"
            className="w-full p-2 border border-gray-300 rounded text-sm"
          />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Max Cards per Chapter: {maxCards}
          </label>
          <input
            type="range"
            min="10"
            max="100"
            value={maxCards}
            onChange={(e) => setMaxCards(Number(e.target.value))}
            className="w-full"
          />
        </div>
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors text-sm font-medium"
        >
          Upload & Detect Chapters
        </button>
      </form>
    </div>
  );
}
