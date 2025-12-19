import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDocuments } from '../context/DocumentContext';
import UploadDocument from '../components/UploadDocument';
import Loader from '../components/Loader';
import ErrorMessage from '../components/ErrorMessage';
import { summarizeDocument, indexDocument } from '../api/upload';

export default function DashboardPage() {
  const navigate = useNavigate();
  const { addDocument } = useDocuments();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleUploadSuccess = async (uploadData) => {
    setLoading(true);
    setError(null);
    
    try {
      // Summarize document
      const summaryData = await summarizeDocument(uploadData.doc_id);
      
      // Index document
      await indexDocument(uploadData.doc_id);
      
      // Add to documents with summary
      addDocument(uploadData.doc_id, uploadData.filename, summaryData);
      
      // Navigate to document page
      navigate(`/document/${uploadData.doc_id}`);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4 sm:space-y-6 lg:space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-2">Dashboard</h1>
        <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">Upload and manage your documents</p>
      </div>

      <ErrorMessage error={error} onRetry={error ? () => setError(null) : null} retryLabel="Dismiss" />
      
      {loading && <Loader />}
      
      <UploadDocument 
        onUploadSuccess={handleUploadSuccess} 
        loading={loading}
      />
    </div>
  );
}
