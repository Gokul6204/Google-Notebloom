import { useState, useRef, useEffect } from 'react'
import './App.css'

function App() {
  const [messages, setMessages] = useState([
    { type: 'ai', text: 'Welcome to Noteboolm! Upload documents to get started.', sources: [] }
  ])
  const [input, setInput] = useState('')
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploadingFile, setUploadingFile] = useState(null)
  const fileInputRef = useRef(null)
  const chatEndRef = useRef(null)

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim()) return

    const userMsg = { type: 'user', text: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: input })
      })
      const data = await response.json()
      setMessages(prev => [...prev, { type: 'ai', text: data.answer, sources: data.sources }])
    } catch (error) {
      setMessages(prev => [...prev, { type: 'ai', text: 'Error connecting to backend. Make sure it is running on port 8000.', sources: [] }])
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    // Initialize progress
    setUploadingFile({ name: file.name, progress: 0 })

    // Simulate progress animation
    const progressInterval = setInterval(() => {
      setUploadingFile(prev => {
        if (!prev || prev.progress >= 90) return prev
        return { ...prev, progress: prev.progress + 10 }
      })
    }, 500)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData
      })

      clearInterval(progressInterval)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: `Server error: ${response.status}` }))
        throw new Error(errorData.detail || `Server error: ${response.status}`)
      }

      const data = await response.json()

      // Complete progress
      setUploadingFile({ name: file.name, progress: 100 })

      // Short delay before showing as completed source
      setTimeout(() => {
        setSources(prev => [...prev, { name: file.name, type: file.name.split('.').pop().toUpperCase() }])
        setMessages(prev => [...prev, {
          type: 'ai',
          text: `✅ ${data.message} (${data.chunks} chunks created)`,
          sources: []
        }])
        setUploadingFile(null)
      }, 500)

    } catch (error) {
      clearInterval(progressInterval)
      setUploadingFile(null)
      setMessages(prev => [...prev, {
        type: 'ai',
        text: `❌ Upload failed: ${error.message}`,
        sources: []
      }])
      console.error('Upload error:', error)
    } finally {
      // Reset file input
      event.target.value = ''
    }
  }

  return (
    <div className="app-container">
      <div className="sidebar">
        <button className="audio-guide-btn">
          ✨ Generate Audio Overview
        </button>

        <div className="sidebar-title">
          <span>Sources</span>
          <button onClick={() => fileInputRef.current.click()} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.2rem' }}>+</button>
        </div>

        <div className="source-list premium-scroll">
          {sources.map((source, i) => (
            <div key={i} className="source-item">
              <div className="source-icon">{source.type}</div>
              <span className="source-name">{source.name}</span>
            </div>
          ))}
          {uploadingFile && (
            <div className="source-item uploading">
              <div className="source-icon">...</div>
              <div className="upload-info">
                <span className="source-name">{uploadingFile.name}</span>
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${uploadingFile.progress}%` }}
                  />
                </div>
                <span className="progress-text">{uploadingFile.progress}%</span>
              </div>
            </div>
          )}
          {sources.length === 0 && !uploadingFile && <p style={{ color: '#9aa0a6', fontSize: '0.9rem' }}>No sources yet.</p>}
        </div>

        <input
          type="file"
          ref={fileInputRef}
          style={{ display: 'none' }}
          onChange={handleFileUpload}
          accept=".pdf,.txt"
        />
      </div>

      <div className="main-content">
        <header className="header">
          <div className="logo">Noteboolm</div>
          <div className="user-profile">👤</div>
        </header>

        <div className="chat-area premium-scroll">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.type === 'user' ? 'user-message' : 'ai-message'}`}>
              <div className="msg-content">{msg.text}</div>
              {msg.sources && msg.sources.length > 0 && (
                <div className="sources-container">
                  {msg.sources.map((s, si) => (
                    <span key={si} className="source-badge">{s}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
          {loading && <div className="message ai-message">Thinking...</div>}
          <div ref={chatEndRef} />
        </div>

        <div className="input-container">
          <div className="input-wrapper">
            <input
              type="text"
              className="chat-input"
              placeholder="Ask a question about your documents..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            />
            <button className="action-btn" onClick={handleSend} disabled={loading}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
