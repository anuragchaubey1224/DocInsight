import { useNavigate } from 'react-router-dom';
import { useDocuments } from '../context/DocumentContext';

export default function DocumentList() {
  const navigate = useNavigate();
  const { documents, activeDocId, setActiveDocId } = useDocuments();

  const handleDocumentClick = (docId) => {
    setActiveDocId(docId);
    navigate(`/document/${docId}`);
  };

  if (documents.length === 0) {
    return (
      <div className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 p-4">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">Documents</h2>
        <div className="text-center py-8">
          <div className="text-4xl mb-2">📄</div>
          <p className="text-sm text-gray-500 dark:text-gray-400">No documents yet</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 overflow-y-auto">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200">Documents</h2>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{documents.length} total</p>
      </div>
      <div className="p-2">
        {documents.map((doc) => (
          <button
            key={doc.docId}
            onClick={() => handleDocumentClick(doc.docId)}
            className={`w-full text-left p-3 rounded-lg mb-2 transition-all ${
              activeDocId === doc.docId
                ? 'bg-blue-50 dark:bg-blue-900 border-2 border-blue-500 dark:border-blue-400'
                : 'bg-gray-50 dark:bg-gray-700 border-2 border-transparent hover:bg-gray-100 dark:hover:bg-gray-600'
            }`}
          >
            <div className="flex items-start space-x-2">
              <span className="text-lg">📄</span>
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium truncate ${
                  activeDocId === doc.docId ? 'text-blue-700 dark:text-blue-300' : 'text-gray-900 dark:text-gray-100'
                }`}>
                  {doc.fileName}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{doc.uploadedAt}</p>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
