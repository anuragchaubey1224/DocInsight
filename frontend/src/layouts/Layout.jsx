import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import DocumentList from '../components/DocumentList';

export default function Layout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout } = useAuth();
  const { isDarkMode, toggleTheme } = useTheme();
  
  const showSidebar = location.pathname.startsWith('/dashboard') || location.pathname.startsWith('/document');

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col transition-colors">
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
        <div className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8">
          <div className="flex justify-between items-center h-14 sm:h-16">
            <Link to="/dashboard" className="flex items-center">
              <h1 className="text-lg sm:text-2xl font-bold text-gray-900 dark:text-white">
                Doc<span className="text-blue-600 dark:text-blue-400">Insight</span>
              </h1>
            </Link>

            <nav className="flex items-center space-x-2 sm:space-x-4">
              <Link
                to="/dashboard"
                className="text-sm sm:text-base text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 font-medium transition-colors"
              >
                Dashboard
              </Link>
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-lg sm:text-xl"
                aria-label="Toggle theme"
              >
                {isDarkMode ? '☀️' : '🌙'}
              </button>
              <button
                onClick={handleLogout}
                className="bg-red-50 dark:bg-red-900 text-red-600 dark:text-red-300 hover:bg-red-100 dark:hover:bg-red-800 font-medium px-2 sm:px-4 py-1.5 sm:py-2 rounded-md transition-colors text-sm sm:text-base"
              >
                Logout
              </button>
            </nav>
          </div>
        </div>
      </header>

      <main className="flex flex-1 overflow-hidden">
        {showSidebar && (
          <aside className="hidden md:block flex-shrink-0">
            <DocumentList />
          </aside>
        )}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8 py-4 sm:py-6 lg:py-8">
            {children}
          </div>
        </div>
      </main>

      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 flex-shrink-0">
        <div className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8 py-4 sm:py-6">
          <p className="text-center text-gray-500 dark:text-gray-400 text-xs sm:text-sm">
            © 2025 DocInsight. Powered by AI.
          </p>
        </div>
      </footer>
    </div>
  );
}
