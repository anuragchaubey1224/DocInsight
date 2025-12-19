import { Link } from 'react-router-dom';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
      <div className="max-w-4xl w-full text-center">
        <div className="mb-8">
          <h1 className="text-6xl font-bold text-gray-900 mb-4">
            Doc<span className="text-blue-600">Insight</span>
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            Intelligent Document Analysis & Question Answering
          </p>
          <p className="text-lg text-gray-500">
            Upload your documents, get AI-powered summaries, and ask questions
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="p-6">
              <div className="text-4xl mb-4">📄</div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Upload</h3>
              <p className="text-gray-600 text-sm">
                Upload PDF or TXT documents
              </p>
            </div>
            <div className="p-6">
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Analyze</h3>
              <p className="text-gray-600 text-sm">
                Get AI-powered summaries
              </p>
            </div>
            <div className="p-6">
              <div className="text-4xl mb-4">💬</div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Ask</h3>
              <p className="text-gray-600 text-sm">
                Ask questions about content
              </p>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/signup"
              className="bg-blue-600 text-white font-semibold py-3 px-8 rounded-lg hover:bg-blue-700 transition-colors shadow-md"
            >
              Get Started
            </Link>
            <Link
              to="/login"
              className="bg-white text-blue-600 font-semibold py-3 px-8 rounded-lg border-2 border-blue-600 hover:bg-blue-50 transition-colors"
            >
              Login
            </Link>
          </div>
        </div>

        <p className="text-gray-500 text-sm">
          Powered by AI • Fast • Secure
        </p>
      </div>
    </div>
  );
}
