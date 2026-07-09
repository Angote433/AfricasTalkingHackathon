import React, { useState, useEffect } from 'react';
import UploadPage from './components/UploadPage';
import ResultsPage from './components/ResultsPage';
import './index.css';

function App() {
  const [analysisResults, setAnalysisResults] = useState(null);
  const [theme, setTheme] = useState(() => {
    try {
      const saved = localStorage.getItem('theme');
      if (saved) return saved;
    } catch (e) {
      // ignore
    }
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  });

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    console.log('[theme] applied:', theme);
    try {
      localStorage.setItem('theme', theme);
    } catch (e) {
      // ignore
    }
  }, [theme]);

  const handleUploadSuccess = (results) => {
    setAnalysisResults(results);
  };

  const handleNewUpload = () => {
    setAnalysisResults(null);
  };

  const toggleTheme = () => setTheme((t) => (t === 'dark' ? 'light' : 'dark'));

  return (
    <div className="App">
      <button
        className="theme-toggle"
        onClick={toggleTheme}
        aria-label="Toggle dark mode"
        title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
      >
        {theme === 'dark' ? '🌙' : '☀️'}
      </button>

      {analysisResults ? (
        <ResultsPage 
          claimData={analysisResults} 
          onNewUpload={handleNewUpload}
        />
      ) : (
        <UploadPage onUploadSuccess={handleUploadSuccess} />
      )}
    </div>
  );
}

export default App;