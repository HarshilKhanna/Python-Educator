import { useState, useEffect, useRef } from 'react'
import { getTopics, uploadMaterial } from '../api'

export default function UploadMaterials() {
  const [topics, setTopics] = useState([])
  const [topicId, setTopicId] = useState('')
  const [uploadedBy, setUploadedBy] = useState('instructor')
  const [file, setFile] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const fileRef = useRef()

  useEffect(() => {
    getTopics()
      .then(data => {
        setTopics(data.topics || [])
        if (data.topics?.length) setTopicId(data.topics[0])
      })
      .catch(() => { })
  }, [])

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped) setFile(dropped)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file || !topicId) return
    setUploading(true)
    setResult(null)
    setError(null)

    const fd = new FormData()
    fd.append('file', file)
    fd.append('topic_id', topicId)
    fd.append('uploaded_by', uploadedBy)

    try {
      const data = await uploadMaterial(fd)
      setResult(data)
      setFile(null)
    } catch (e) {
      setError(e.message)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div>
      <div className="page-header"><div className="page-header-left">
        <h1>Upload Materials</h1>
        <p>Upload supplementary handouts (PDF, DOCX, or Markdown). They are chunked, embedded, and surfaced alongside handbook content in student sessions.</p></div>
      </div>

      {result && (
        <div className="alert alert-success">
          Uploaded <strong>{result.filename}</strong> — <span className="chunk-chip">[{result.chunk_count}] chunks</span>
          &nbsp;tagged as <span className="badge badge-upload">instructor_upload</span> for topic <span className="badge badge-pending">{result.topic_id}</span>
        </div>
      )}
      {error && <div className="alert alert-error">Upload failed: {error}</div>}

      <div className="card">
        <form id="upload-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="topic-select">Topic</label>
            <select
              id="topic-select"
              value={topicId}
              onChange={e => setTopicId(e.target.value)}
              required
            >
              {topics.map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="uploaded-by">Uploaded by</label>
            <input
              id="uploaded-by"
              type="text"
              value={uploadedBy}
              onChange={e => setUploadedBy(e.target.value)}
              placeholder="Your name"
            />
          </div>

          <div className="form-group">
            <label>File (PDF, DOCX, or Markdown)</label>
            <div
              className={`drop-zone${dragging ? ' drag-over' : ''}`}
              onClick={() => fileRef.current?.click()}
              onDragOver={e => { e.preventDefault(); setDragging(true) }}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
            >

              {file
                ? <p><strong>{file.name}</strong> ({(file.size / 1024).toFixed(1)} KB)</p>
                : <p>Click to browse or drag a file here</p>
              }
              <input
                id="file-input"
                ref={fileRef}
                type="file"
                accept=".pdf,.docx,.doc,.md,.txt"
                onChange={e => setFile(e.target.files[0])}
              />
            </div>
          </div>

          <button
            id="upload-submit"
            type="submit"
            className="btn btn-primary"
            disabled={!file || !topicId || uploading}
          >
            {uploading
              ? <><span className="spinner" /> Uploading…</>
              : 'Upload & Ingest'}
          </button>
        </form>
      </div>

      <div className="card">
        <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>
          <strong style={{ color: 'var(--text)' }}>How it works:</strong>
          {' '}Files are split by heading boundaries (Markdown) or paragraph breaks (PDF/DOCX),
          embedded locally, and stored with <code>source_type=&#39;instructor_upload&#39;</code>.
          When a student asks a question, these chunks are ranked <em>after</em> handbook chunks
          of equal relevance. The Technical Agent explicitly signals when an answer comes from
          your notes rather than the core curriculum.
        </p>
      </div>
    </div>
  )
}
