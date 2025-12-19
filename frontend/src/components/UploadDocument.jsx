import { uploadDocument } from '../api/upload';

export default function UploadDocument({ onUploadSuccess, loading }) {
  const handleFileUpload = async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
      return;
    }
    
    try {
      const data = await uploadDocument(file);
      onUploadSuccess(data);
      fileInput.value = '';
    } catch (error) {
      throw error;
    }
  };
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-md p-4 sm:p-6 transition-all duration-200">
      <h2 className="text-xl sm:text-2xl font-semibold text-gray-800 dark:text-gray-200 mb-3 sm:mb-4">Upload Document</h2>
      <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mb-3 sm:mb-4">Upload a PDF or TXT file to get started</p>
      <form onSubmit={handleFileUpload} className="space-y-3 sm:space-y-4">
        <div>
          <input 
            type="file" 
            id="fileInput" 
            accept=".pdf,.txt" 
            disabled={loading}
            className="block w-full text-xs sm:text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-xs sm:file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 file:transition-colors file:duration-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          />
        </div>
        <button 
          type="submit" 
          disabled={loading}
          className="w-full bg-blue-600 text-white font-semibold py-3 sm:py-3 px-4 rounded-lg hover:bg-blue-700 active:scale-95 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-sm hover:shadow-md text-sm sm:text-base min-h-[44px]"
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Uploading...
            </span>
          ) : 'Upload'}
        </button>
      </form>
    </div>
  );
}
