import { useState, useEffect } from 'react'
import { Upload, File, Trash2 } from 'lucide-react'
import api from '../services/api'

function DocumentUpload({ onDocumentsChange, demoMode = false }) {
  const [documents, setDocuments] = useState([])
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!demoMode) {
      loadDocuments()
    }
  }, [demoMode])

  const loadDocuments = async () => {
    try {
      const data = await api.getDocuments()
      setDocuments(data.documents || [])
      if (onDocumentsChange) onDocumentsChange(data.documents || [])
    } catch (err) {
      console.error('Failed to load documents:', err)
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    if (file.type !== 'application/pdf') {
      setError('Only PDF files are supported')
      return
    }

    if (demoMode && documents.length >= 1) {
      setError('Demo mode supports 1 document. Sign up for unlimited access.')
      return
    }

    setUploading(true)
    setError('')

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
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  const handleDelete = async (documentId) => {
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
      setError(err.message)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Documents</h2>

      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded mb-4 text-sm">
          {error}
        </div>
      )}

      <label className="block w-full">
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer hover:border-indigo-500 transition">
          <Upload className="mx-auto h-12 w-12 text-gray-400 mb-2" />
          <p className="text-sm text-gray-600">
            {uploading
              ? 'Uploading...'
              : demoMode && documents.length >= 1
              ? 'Demo limit reached (1 PDF). Sign up for more.'
              : 'Click to upload PDF'}
          </p>
          <input
            type="file"
            accept="application/pdf"
            onChange={handleFileUpload}
            disabled={uploading || (demoMode && documents.length >= 1)}
            className="hidden"
          />
        </div>
      </label>

      <div className="mt-6 space-y-2">
        {documents.map((doc) => (
          <div
            key={doc.document_id}
            className="flex items-center justify-between p-3 bg-gray-50 rounded hover:bg-gray-100 transition"
          >
            <div className="flex items-center space-x-3 flex-1">
              <File className="h-5 w-5 text-indigo-600" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {doc.filename}
                </p>
                <p className="text-xs text-gray-500">
                  {doc.page_count} pages, {doc.chunk_count} chunks
                </p>
              </div>
            </div>
            <button
              onClick={() => handleDelete(doc.document_id)}
              className="text-red-500 hover:text-red-700"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        ))}

        {documents.length === 0 && !uploading && (
          <p className="text-sm text-gray-500 text-center py-4">
            No documents uploaded yet
          </p>
        )}
      </div>
    </div>
  )
}

export default DocumentUpload
