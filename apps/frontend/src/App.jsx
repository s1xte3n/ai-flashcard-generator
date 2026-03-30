import { useState } from 'react';
import UploadForm from './components/UploadForm';
import FlashcardList from './components/FlashcardList';

function App() {
  const [flashcards, setFlashcards] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState({ processed: 0, duplicates: 0 });

  const handleReset = () => {
    setFlashcards(null);
    setProgress({ processed: 0, duplicates: 0 });
  };

  return (
    <div className='min-h-screen bg-gray-50'>
      <header className='bg-white shadow-sm'>
        <div className='max-w-4xl mx-auto px-4 py-4'>
          <h1 className='text-2xl font-bold text-gray-800'>
            AI Flashcard Generator
          </h1>
          <p className='text-sm text-gray-500 mt-1'>
            Upload a PDF textbook and generate exam-focused flashcards
          </p>
        </div>
      </header>

      <main className='max-w-4xl mx-auto px-4 py-8'>
        {isGenerating && (
          <div className='bg-blue-50 text-blue-700 p-4 rounded-lg mb-6 text-center'>
            <div className='inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-700 mr-2'></div>
            Generating flashcards... This may take a few minutes.
          </div>
        )}

        {!flashcards ? (
          <UploadForm
            onGenerated={(cards, stats) => {
              setFlashcards(cards);
              setProgress(stats);
            }}
            setIsGenerating={setIsGenerating}
          />
        ) : (
          <FlashcardList
            flashcards={flashcards}
            onReset={handleReset}
            stats={progress}
          />
        )}
      </main>

      <footer className='bg-white border-t mt-auto py-4'>
        <div className='max-w-4xl mx-auto px-4 text-center text-sm text-gray-500'>
          Powered by local LLMs • No data leaves your machine
        </div>
      </footer>
    </div>
  );
}

export default App;
