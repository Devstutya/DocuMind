import { useState, useEffect, useRef } from 'react'
import { Upload, FileText, Trash2, CheckCircle, AlertCircle, Loader } from 'lucide-react'
import api from '../services/api'

function DocumentUpload({ onDocumentsChange, demoMode = false }) {
  const [documents, setDocuments]   = useState([])
  const [uploading, setUploading]   = useState(false)
  const [error, setError]           = useState('')
  const [successMsg, setSuccessMsg] = useState('')
  const [dragActive, setDragActive] = useState(false)
  const inputRef = useRef(null)

  useEffect(() => {
    if (!demoMode) loadDocuments()
  }, [demoMode])

  const loadDocuments = async () => {
    try {
      const data = await api.getDocuments()
      const docs = data.documents || []
      setDocuments(docs)
      if (onDocumentsChange) onDocumentsChange(docs)
    } catch (err) {
      console.error('Failed to load documents:', err)
    }
  }

  const processFile = async (file) => {
    setError('')
    setSuccessMsg('')

    if (!file) return
    if (file.type !== 'application/pdf') {
      setError('Only PDF files are supported.')
      return
    }
    if (demoMode && documents.length >= 1) {
      setError('Demo mode supports 1 document. Sign up for unlimited access.')
      return
    }

    setUploading(true)
    try {
      const doc = demoMode
        ? await api.demoUploadDocument(file)
        : await api.uploadDocument(file)

      if (demoMode) {
        const updated = [...documents, doc]
        setDocuments(updated)
        if (onDocumentsChange) onDocumentsChange(updated)
      } else {
        await loadDocuments()
      }
      setSuccessMsg(`"${file.name}" uploaded successfully.`)
      setTimeout(() => setSuccessMsg(''), 4000)
    } catch (err) {
      setError(err.message || 'Upload failed. Please try again.')
    } finally {
      setUploading(false)
      if (inputRef.current) inputRef.current.value = ''
    }
  }

  const handleFileInput = (e) => processFile(e.target.files[0])

  const handleDrop = (e) => {
    e.preventDefault()
    setDragActive(false)
    processFile(e.dataTransfer.files[0])
  }

  const handleDragOver = (e) => { e.preventDefault(); setDragActive(true)  }
  const handleDragLeave = ()  => setDragActive(false)

  const handleDelete = async (documentId) => {
    setError('')
    if (demoMode) {
      const updated = documents.filter(d => d.document_id !== documentId)
      setDocuments(updated)
      if (onDocumentsChange) onDocumentsChange(updated)
      return
    }
    try {
      await api.deleteDocument(documentId)
      await loadDocuments()
    } catch (err) {
      setError(err.message || 'Failed to delete document.')
    }
  }

  const isLimitReached = demoMode && documents.length >= 1
  const dropDisabled   = uploading || isLimitReached

  return (
    <div className="bg-navy-900 rounded-2xl border border-navy-700 shadow-card p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-white">Documents</h2>
        {documents.length > 0 && (
          <span className="text-2xs font-medium text-navy-300 bg-navy-700 px-2 py-0.5 rounded-full">
            {documents.length} {documents.length === 1 ? 'file' : 'files'}
          </span>
        )}
      </div>

      {/* Status messages */}
      {error && (
        <div className="flex items-center gap-2 bg-red-900/30 border border-red-700/50 text-red-300 px-3 py-2.5
                        rounded-lg text-xs mb-3 animate-fade-in">
          <AlertCircle size={14} className="shrink-0" />
          {error}
        </div>
      )}
      {successMsg && (
        <div className="flex items-center gap-2 bg-emerald-900/30 border border-emerald-700/50 text-emerald-300
                        px-3 py-2.5 rounded-lg text-xs mb-3 animate-fade-in">
          <CheckCircle size={14} className="shrink-0" />
          {successMsg}
        </div>
      )}

      {/* Drop zone */}
      <label
        className={[
          'block w-full rounded-xl border-2 border-dashed text-center cursor-pointer',
          'transition-all duration-200 select-none',
          dropDisabled
            ? 'border-navy-700 bg-navy-800 opacity-60 cursor-not-allowed'
            : dragActive
              ? 'border-violet-500 bg-violet-600/10 shadow-glow-violet scale-[1.01]'
              : 'border-navy-700 bg-navy-800 hover:border-violet-500/50 hover:bg-violet-600/5',
        ].join(' ')}
        onDrop={dropDisabled ? undefined : handleDrop}
        onDragOver={dropDisabled ? undefined : handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <div className="py-6 px-4">
          {uploading ? (
            <div className="flex flex-col items-center gap-2">
              <Loader size={28} className="text-violet-400 animate-spin" />
              <p className="text-xs font-medium text-violet-300">Processing PDF…</p>
              <p className="text-2xs text-navy-400">Extracting text and generating embeddings</p>
            </div>
          ) : isLimitReached ? (
            <div className="flex flex-col items-center gap-2">
              <Upload size={28} className="text-navy-500" />
              <p className="text-xs font-medium text-navy-400">Demo limit reached</p>
              <p className="text-2xs text-navy-500">Sign up for unlimited documents</p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2">
              <div className={[
                'w-10 h-10 rounded-xl flex items-center justify-center transition-colors duration-200',
                dragActive ? 'bg-violet-600/20' : 'bg-navy-700',
              ].join(' ')}>
                <Upload size={20} className={dragActive ? 'text-violet-400' : 'text-navy-400'} />
              </div>
              <div>
                <p className="text-xs font-medium text-navy-200">
                  {dragActive ? 'Drop your PDF here' : 'Drop PDF or click to upload'}
                </p>
                <p className="text-2xs text-navy-500 mt-0.5">PDF files only · Max 50 MB</p>
              </div>
            </div>
          )}
        </div>
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          onChange={handleFileInput}
          disabled={dropDisabled}
          className="hidden"
          aria-label="Upload PDF document"
        />
      </label>

      {/* Document list */}
      {documents.length > 0 && (
        <ul className="mt-4 space-y-2" role="list" aria-label="Uploaded documents">
          {documents.map((doc) => (
            <li
              key={doc.document_id}
              className="group flex items-center gap-3 px-3 py-2.5 rounded-xl bg-navy-800
                         border border-navy-700 hover:border-violet-600/40 hover:bg-navy-800/80
                         transition-all duration-150"
            >
              <div className="w-8 h-8 rounded-lg bg-violet-600/15 border border-violet-500/20
                              flex items-center justify-center shrink-0">
                <FileText size={14} className="text-violet-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-gray-100 truncate">{doc.filename}</p>
                <p className="text-2xs text-navy-400 mt-0.5">
                  {doc.page_count} {doc.page_count === 1 ? 'page' : 'pages'}
                  {doc.chunk_count ? ` · ${doc.chunk_count} chunks` : ''}
                </p>
              </div>
              <button
                onClick={() => handleDelete(doc.document_id)}
                aria-label={`Delete ${doc.filename}`}
                className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg
                           text-navy-400 hover:text-red-400 hover:bg-red-900/30
                           transition-all duration-150"
              >
                <Trash2 size={13} />
              </button>
            </li>
          ))}
        </ul>
      )}

      {documents.length === 0 && !uploading && (
        <p className="text-center text-xs text-navy-500 mt-4 py-2">
          No documents yet — upload your first PDF above.
        </p>
      )}
    </div>
  )
}

export default DocumentUpload
