import React, { useState } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [useRelatedSearch, setUseRelatedSearch] = useState(false);
  const [results, setResults] = useState([]);
  const [noResults, setNoResults] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [file, setFile] = useState(null);
  const [selectedDocument, setSelectedDocument] = useState(null);

  const handleSearch = async (searchQuery = query, relatedSearch = useRelatedSearch) => {
    setLoading(true);
    setError('');
    setNoResults(false);
    setResults([]);
    setSelectedDocument(null); // Clear the selected document when search starts

    try {
      const response = await fetch(`http://localhost:8000/search?query=${searchQuery}&related=${relatedSearch}`);
      if (!response.ok) {
        throw new Error('Failed to fetch results');
      }
      const data = await response.json();
      setResults(data);
      setNoResults(data.length === 0);
    } catch (err) {
      setError('An error occurred during the search. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleFileUpload = async () => {
    if (!file) {
      setError('Please select a file to upload.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/uploadfile/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to upload file');
      }

      const data = await response.json();
      if (data.error) {
        setError(data.error);
      } else {
        setError('');
        alert('File uploaded successfully');
      }
    } catch (err) {
      setError('An error occurred during the file upload. Please try again.');
    }
  };

  const fetchDocument = async (id) => {
    try {
      const response = await fetch(`http://localhost:8000/document/${id}`);
      if (!response.ok) {
        throw new Error('Failed to fetch document');
      }
      const data = await response.json();
      setSelectedDocument(data);
    } catch (err) {
      setError('An error occurred while fetching the document. Please try again.');
    }
  };

  const deleteDocument = async (id) => {
    try {
      const response = await fetch(`http://localhost:8000/document/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error('Failed to delete document');
      }
      alert('Document deleted successfully');
      handleSearch(); // Refresh the search results
    } catch (err) {
      setError('An error occurred while deleting the document. Please try again.');
    }
  };

  const handleRefresh = () => {
    setQuery('');
    setUseRelatedSearch(false);
    handleSearch('', false); // Call handleSearch with default parameters
  };

  return (
    <div className="container">
      <h1>Search Documents</h1>
      <div className="search-bar">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="search-input"
          placeholder="Search..."
        />
        <button onClick={() => handleSearch()} disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
        <button onClick={handleRefresh} disabled={loading}>
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>
      <label className="related-search">
        <input
          type="checkbox"
          checked={useRelatedSearch}
          onChange={(e) => setUseRelatedSearch(e.target.checked)}
        />
        Use related search
      </label>
      {error && <p className="error">{error}</p>}
      {noResults && <p className="no-results">No search results found.</p>}
      <div className="results">
        <ul>
          {results.map((result, index) => (
            <li key={index}>
              <div onClick={() => fetchDocument(result.id)}>
                {result.title}: {result.content}...
              </div>
              <button onClick={() => deleteDocument(result.id)}>Delete</button>
            </li>
          ))}
        </ul>
      </div>
      {selectedDocument && (
        <div className="document-details">
          <h2>{selectedDocument.title}</h2>
          <div className="document-content">
            <p>{selectedDocument.content}</p>
          </div>
          <button onClick={() => setSelectedDocument(null)}>Close</button>
        </div>
      )}
      <h2>Upload File</h2>
      <div className="upload-bar">
        <label htmlFor="file-upload" className="custom-file-upload">
          {file ? file.name : 'Choose File'}
        </label>
        <input id="file-upload" type="file" onChange={handleFileChange} style={{ display: 'none' }} />
        <button onClick={handleFileUpload}>Upload</button>
      </div>
    </div>
  );
}

export default App;
