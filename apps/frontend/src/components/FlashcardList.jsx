import { useState, useEffect } from 'react';
import { FlashcardArray } from "react-quizlet-flashcard";
import "react-quizlet-flashcard/dist/index.css";
import { api } from '../api';

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export default function FlashcardList({ flashcards, onReset, stats }) {
  const [deck, setDeck] = useState([]);

  useEffect(() => {
    if (flashcards && flashcards.length > 0) {
      const formatted = flashcards
        .filter(f => f && f.question && f.answer)
        .map((f, idx) => ({
        id: f.id || `card-${idx}`,
        front: { html: <div className="text-lg p-4">{f.question}</div> },
        back: { html: <div className="text-lg p-4">{f.answer}</div> },
      }));
      setDeck(formatted);
    } else {
      setDeck([]);
    }
  }, [flashcards]);

  const handleExportCSV = async () => {
    try {
      const blob = await api.exportCSV(flashcards);
      downloadBlob(blob, 'flashcards.csv');
    } catch (err) {
      console.error('CSV export failed:', err);
    }
  };

  const handleExportPDF = async () => {
    try {
      const blob = await api.exportPDF(flashcards);
      downloadBlob(blob, 'flashcards.pdf');
    } catch (err) {
      console.error('PDF export failed:', err);
    }
  };

  if (!flashcards || flashcards.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md max-w-2xl mx-auto text-center">
        <h3 className="text-xl font-semibold mb-4">No Flashcards Generated</h3>
        <p className="text-gray-600 mb-4">
          The chapter was processed but no flashcards could be generated.
          This might be due to the PDF text format or LLM response issues.
        </p>
        <div className="flex justify-center gap-4">
          <button
            onClick={onReset}
            className="bg-blue-600 text-white py-2 px-6 rounded hover:bg-blue-700"
          >
            Try Another Chapter
          </button>
          <button
            onClick={onReset}
            className="bg-gray-500 text-white py-2 px-6 rounded hover:bg-gray-600"
          >
            Start Over
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex flex-wrap justify-between items-center mb-4 gap-4">
        <div className="text-sm text-gray-600">
          Processed {stats.processed} chunks • Removed {stats.duplicates} duplicates •{' '}
          {flashcards.length} cards
        </div>
        <button
          onClick={onReset}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          ← Continue to Next Chapter
        </button>
      </div>
      
      {deck.length > 0 ? (
        <div className="bg-white p-6 rounded-lg shadow-md mb-6">
          <FlashcardArray deck={deck} />
        </div>
      ) : (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6 text-center">
          <p className="text-yellow-800">
            Generated data but couldn't render flashcards. Export to view results.
          </p>
        </div>
      )}
      
      <div className="flex justify-center gap-4">
        <button
          onClick={handleExportCSV}
          className="bg-green-600 text-white py-2 px-6 rounded hover:bg-green-700 transition-colors text-sm font-medium"
        >
          Export CSV
        </button>
        <button
          onClick={handleExportPDF}
          className="bg-red-600 text-white py-2 px-6 rounded hover:bg-red-700 transition-colors text-sm font-medium"
        >
          Export PDF
        </button>
      </div>
    </div>
  );
}
