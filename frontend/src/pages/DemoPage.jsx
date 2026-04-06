import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Brain, ArrowRight, Info } from 'lucide-react'
import DocumentUpload from '../components/DocumentUpload'
import ChatInterface from '../components/ChatInterface'

function DemoPage() {
  const [selectedDocuments, setSelectedDocuments] = useState([])

  return (
    <div className="min-h-screen bg-navy-950 flex flex-col">
      {/* Nav */}
      <header className="bg-navy-950 border-b border-navy-800 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-500 to-violet-700
                            flex items-center justify-center shadow">
              <Brain size={14} className="text-white" />
            </div>
            <span className="font-bold text-sm text-white tracking-tight">DocuMind</span>
            <span className="text-xs text-navy-300 font-medium bg-navy-800 px-2 py-0.5 rounded-full ml-1 border border-navy-700">
              Demo
            </span>
          </div>
          <Link
            to="/login"
            className="inline-flex items-center gap-1.5 bg-violet-600 hover:bg-violet-700
                       text-white font-semibold text-xs px-4 py-2 rounded-lg
                       transition-colors duration-150"
          >
            Get full access
            <ArrowRight size={13} />
          </Link>
        </div>
      </header>

      <main className="flex-1 max-w-6xl mx-auto w-full px-6 py-8">
        {/* Demo banner */}
        <div className="flex items-start gap-3 bg-violet-600/10 border border-violet-500/30 rounded-xl px-4 py-3.5 mb-6">
          <Info size={15} className="text-violet-400 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-violet-300">Demo mode — 1 document limit</p>
            <p className="text-xs text-violet-400 mt-0.5">
              Upload one PDF and start asking questions.{' '}
              <Link to="/login" className="underline hover:no-underline font-medium text-violet-300">
                Sign up free
              </Link>{' '}
              for unlimited documents, chat history, and more.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <div className="lg:col-span-1">
            <DocumentUpload onDocumentsChange={setSelectedDocuments} demoMode={true} />
          </div>
          <div className="lg:col-span-2">
            <ChatInterface selectedDocuments={selectedDocuments} />
          </div>
        </div>
      </main>
    </div>
  )
}

export default DemoPage
