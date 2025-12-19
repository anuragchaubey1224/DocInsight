import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useDocuments } from '../context/DocumentContext';
import SummaryPanel from '../components/SummaryPanel';
import AskQuestion from '../components/AskQuestion';
import AnswerBox from '../components/AnswerBox';

export default function DocumentPage() {
  const { id } = useParams();
  const { setActiveDocId, getActiveDocument } = useDocuments();
  const [answer, setAnswer] = useState(null);
  const [isAnswerLoading, setIsAnswerLoading] = useState(false);

  // Sync activeDocId with URL
  useEffect(() => {
    if (id) {
      setActiveDocId(parseInt(id));
    }
  }, [id, setActiveDocId]);

  const activeDoc = getActiveDocument();
  const summary = activeDoc?.summary || null;
  const docId = activeDoc?.docId || parseInt(id);
  const isSummaryLoading = !summary && id;

  const handleAskQuestion = (answerData) => {
    setAnswer(answerData);
    setIsAnswerLoading(false);
  };

  const handleAskStart = () => {
    setIsAnswerLoading(true);
  };

  return (
    <div className="space-y-4 sm:space-y-6 lg:space-y-8">
      <div className="flex items-center justify-between">
        <div className="min-w-0 flex-1">
          <Link to="/dashboard" className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 text-xs sm:text-sm font-medium mb-2 inline-flex items-center">
            <svg className="w-3 h-3 sm:w-4 sm:h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Dashboard
          </Link>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mt-2">Document Analysis</h1>
          {activeDoc && <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400 mt-1 truncate">{activeDoc.fileName}</p>}
        </div>
      </div>
      
      <SummaryPanel summary={summary} loading={isSummaryLoading} />
      
      <AskQuestion 
        docId={docId}
        onAskQuestion={handleAskQuestion}
        onAskStart={handleAskStart}
        loading={false}
      />
      
      <AnswerBox answer={answer} loading={isAnswerLoading} />
    </div>
  );
}
