import { useState } from 'react'
import { FileText } from 'lucide-react'
import Sidebar from '../components/Sidebar'
import DocumentUpload from '../components/DocumentUpload'
import ChatInterface from '../components/ChatInterface'

function Dashboard() {
  const [selectedDocuments, setSelectedDocuments] = useState([])
  const [activeSection, setActiveSection] = useState('chat')

  const renderContent = () => {
    switch (activeSection) {
      case 'chat':
        return (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <DocumentUpload onDocumentsChange={setSelectedDocuments} />
            </div>
            <div className="lg:col-span-2">
              <ChatInterface selectedDocuments={selectedDocuments} />
            </div>
          </div>
        )
      case 'documents':
        return (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold mb-4">My Documents</h2>
            <p className="text-gray-600">Your uploaded documents will appear here.</p>
            <div className="mt-6 space-y-4">
              <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <FileText className="text-indigo-600" size={24} />
                    <div>
                      <p className="font-medium">Sample Document.pdf</p>
                      <p className="text-sm text-gray-500">Uploaded 2 days ago</p>
                    </div>
                  </div>
                  <button className="text-red-600 hover:text-red-700">Delete</button>
                </div>
              </div>
            </div>
          </div>
        )
      case 'history':
        return (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold mb-4">Chat History</h2>
            <p className="text-gray-600">Your previous conversations will be saved here.</p>
            <div className="mt-6 space-y-3">
              <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition cursor-pointer">
                <p className="font-medium">Questions about climate change research</p>
                <p className="text-sm text-gray-500">2 hours ago</p>
              </div>
              <div className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition cursor-pointer">
                <p className="font-medium">Company financial analysis</p>
                <p className="text-sm text-gray-500">Yesterday</p>
              </div>
            </div>
          </div>
        )
      case 'upload':
        return (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold mb-4">Upload Documents</h2>
            <DocumentUpload onDocumentsChange={setSelectedDocuments} />
          </div>
        )
      case 'settings':
        return (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold mb-4">Settings</h2>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  AI Model
                </label>
                <select className="w-full border border-gray-300 rounded-lg px-4 py-2">
                  <option>GPT-4o-mini (Fast, Cost-Effective)</option>
                  <option>GPT-4o (Balanced)</option>
                  <option>GPT-4 (Most Accurate)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Retrieval Results
                </label>
                <select className="w-full border border-gray-300 rounded-lg px-4 py-2">
                  <option>Top 3 chunks</option>
                  <option>Top 5 chunks (Recommended)</option>
                  <option>Top 10 chunks</option>
                </select>
              </div>
              <div>
                <label className="flex items-center space-x-2">
                  <input type="checkbox" className="rounded" defaultChecked />
                  <span className="text-sm text-gray-700">Show source citations</span>
                </label>
              </div>
              <div>
                <label className="flex items-center space-x-2">
                  <input type="checkbox" className="rounded" defaultChecked />
                  <span className="text-sm text-gray-700">Enable conversation memory</span>
                </label>
              </div>
            </div>
          </div>
        )
      case 'profile':
        return (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold mb-4">Profile</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                <input
                  type="email"
                  className="w-full border border-gray-300 rounded-lg px-4 py-2"
                  defaultValue="user@example.com"
                  disabled
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-lg px-4 py-2"
                  defaultValue="John Doe"
                />
              </div>
              <div className="pt-4">
                <h3 className="font-medium text-gray-900 mb-2">Usage Statistics</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Documents</p>
                    <p className="text-2xl font-bold text-indigo-600">12</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Queries</p>
                    <p className="text-2xl font-bold text-indigo-600">156</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )
      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar activeSection={activeSection} setActiveSection={setActiveSection} />

      <div className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto px-8 py-8">
          {renderContent()}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
