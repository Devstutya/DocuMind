import { useState } from 'react'
import DocumentUpload from '../components/DocumentUpload'
import ChatInterface from '../components/ChatInterface'

function Dashboard() {
  const [selectedDocuments, setSelectedDocuments] = useState([])

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">DocuMind Dashboard</h1>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 py-8">
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

export default Dashboard
