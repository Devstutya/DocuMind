import { useState } from 'react'
import { Link } from 'react-router-dom'
import DocumentUpload from '../components/DocumentUpload'
import ChatInterface from '../components/ChatInterface'

function DemoPage() {
  const [selectedDocuments, setSelectedDocuments] = useState([])

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">DocuMind Demo</h1>
          <Link
            to="/login"
            className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition"
          >
            Get Started
          </Link>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-blue-800">
            <strong>Try the demo!</strong> Upload a document and ask questions. Sign up to save your documents and chat history.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <DocumentUpload onDocumentsChange={setSelectedDocuments} />
          </div>

          <div className="lg:col-span-2">
            <ChatInterface selectedDocuments={selectedDocuments} />
          </div>
        </div>
      </div>
    </div>
  )
}

export default DemoPage
