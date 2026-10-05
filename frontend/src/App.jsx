import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import './index.css';

function App() {
  const [query, setQuery] = useState('');
  const [documents, setDocuments] = useState([]);

  // Persistence for messages
  const [messages, setMessages] = useState(() => {
    const saved = localStorage.getItem('chatHistory');
    return saved ? JSON.parse(saved) : [];
  });

  const [uploadStatus, setUploadStatus] = useState('');
  const chatEndRef = useRef(null);

  const loadDocuments = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/documents/');
      const data = await res.json();
      if (Array.isArray(data)) setDocuments(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  // Save chat to localstorage on change
  useEffect(() => {
    localStorage.setItem('chatHistory', JSON.stringify(messages));
  }, [messages]);

  // auto-scroll when new messages arrive
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleUpload = async (e) => {
    if (!e.target.files?.length) return;
    const files = Array.from(e.target.files);

    const formData = new FormData();
    files.forEach(f => formData.append('files', f));

    setUploadStatus(`Uploading ${files.length} document(s)...`);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/documents/upload', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();

      const fails = data.results?.filter(r => r.error);
      if (fails?.length > 0) {
        setUploadStatus(`Error on ${fails.length}: ${fails[0].error}`);
      } else {
        setUploadStatus('Success!');
      }
      loadDocuments();
    } catch (err) {
      setUploadStatus('Upload failed.');
    }

    setTimeout(() => {
      setUploadStatus('');
    }, 4000);
  };

  const handleDelete = async (filename) => {
    if (!window.confirm(`Are you sure you want to delete ${filename}?`)) return;
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/documents/${filename}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        loadDocuments();
      } else {
        alert("Failed to delete document.");
      }
    } catch (e) {
      alert("Error deleting document.");
    }
  };

  const handleChat = async () => {
    if (!query) return;

    const newMessages = [...messages, { sender: 'User', text: query }];
    setMessages(newMessages);
    setQuery('');

    try {
      const res = await fetch('http://127.0.0.1:8000/api/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: query })
      });
      const data = await res.json();

      if (!res.ok) {
        setMessages([...newMessages, { sender: 'SmartDocs AI', text: data.detail || 'Error connecting to backend.' }]);
        return;
      }

      setMessages([...newMessages, { sender: 'SmartDocs AI', text: data.answer, sources: data.sources }]);
    } catch (err) {
      setMessages([...newMessages, { sender: 'SmartDocs AI', text: 'Error connecting to RAG backend.' }]);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>SmartDocs <span className="highlight">AI</span></h1>
        <p className="subtitle">Your Intelligent RAG Assistant</p>
      </header>

      <main className="app-main">
        {/* Sidebar / Documents */}
        <section className="glass-panel knowledge-base">
          <div className="panel-header">
            <h2>Knowledge Base</h2>
            <div className="badge">{documents.length} Docs</div>
          </div>

          <div className="doc-list">
            {documents.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📁</div>
                <p>No documents uploaded yet.</p>
              </div>
            ) : null}
            {documents.map((doc, idx) => (
              <div key={idx} className="doc-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>

                  <div className="doc-info" style={{ marginBottom: 0 }}>
                    <span className="doc-icon">📄</span>
                    <span className="doc-title">{doc.filename}</span>
                  </div>

                  <button onClick={() => handleDelete(doc.filename)} className="delete-btn" title="Delete Document">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                  </button>

                </div>

                <div className="doc-meta" style={{ marginTop: '0.75rem' }}>
                  <span className="pill">Pages: {doc.pages}</span>
                  <span className="pill">Chunks: {doc.chunks}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="upload-section">
            <label className="upload-btn">
              <span className="upload-icon">⬆️</span>
              {uploadStatus || 'Upload Documents'}
              <input type="file" multiple accept=".pdf" className="hidden-input" onChange={handleUpload} />
            </label>
          </div>
        </section>

        {/* Chat Interface */}
        <section className="glass-panel chat-interface">
          <div className="panel-header">
            <h2>Context Engine</h2>
            {messages.length > 0 && (
              <button
                onClick={() => { if (window.confirm('Clear chat history?')) setMessages([]) }}
                className="clear-chat-btn">
                Clear
              </button>
            )}
          </div>

          <div className="chat-window">
            {messages.length === 0 ? (
              <div className="empty-state chat-empty">
                <div className="empty-icon">✨</div>
                <p>Ask a question to search your documents contextually!</p>
              </div>
            ) : null}

            <div className="messages">
              {messages.map((msg, i) => (
                <div key={i} className={`message-wrapper ${msg.sender === 'User' ? 'user-wrapper' : 'ai-wrapper'}`}>
                  <div className="message-sender">{msg.sender}</div>
                  <div className={`message-bubble ${msg.sender === 'User' ? 'user-bubble' : 'ai-bubble'}`}>
                    {msg.sender === 'User' ? (
                      msg.text
                    ) : (
                      <div className="markdown-body">
                        <ReactMarkdown>{msg.text}</ReactMarkdown>
                      </div>
                    )}
                  </div>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="sources-container">
                      <span className="sources-label">Sources:</span>
                      {msg.sources.map((s, idx) => (
                        <span key={idx} className="source-tag">{s.document} (pg {s.page})</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              <div ref={chatEndRef} />
            </div>
          </div>

          <div className="input-area">
            <input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleChat()}
              placeholder="Ask anything about your documents..."
              className="chat-input"
            />
            <button onClick={handleChat} className="send-btn">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
