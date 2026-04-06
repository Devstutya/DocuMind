import { useState, useEffect } from 'react'
import { FileText, Upload, Settings, Sliders, MessageSquare, BarChart3, User as UserIcon } from 'lucide-react'
import Sidebar from '../components/Sidebar'
import DocumentUpload from '../components/DocumentUpload'
import ChatInterface from '../components/ChatInterface'
import api from '../services/api'

/* ── Shared section wrapper ── */
function Section({ title, description, children }) {
  return (
    <div className="space-y-6 animate-fade-up">
      {(title || description) && (
        <div>
          {title && <h1 className="text-xl font-bold text-white">{title}</h1>}
          {description && <p className="text-sm text-navy-300 mt-1">{description}</p>}
        </div>
      )}
      {children}
    </div>
  )
}

/* ── Card wrapper ── */
function Card({ children, className = '' }) {
  return (
    <div className={`bg-navy-800 rounded-2xl border border-navy-700 shadow-card ${className}`}>
      {children}
    </div>
  )
}

/* ── Stat card ── */
function StatCard({ label, value, icon: Icon, accent = 'violet' }) {
  const colors = {
    violet: 'bg-violet-600/20 text-violet-300 border-violet-600/30',
    navy:   'bg-navy-700 text-navy-300 border-navy-600',
  }
  return (
    <div className="bg-navy-800 rounded-2xl border border-navy-700 shadow-card p-5 flex items-center gap-4">
      <div className={`w-11 h-11 rounded-xl border flex items-center justify-center shrink-0 ${colors[accent]}`}>
        <Icon size={20} />
      </div>
      <div>
        <p className="text-2xl font-bold text-white leading-none">{value}</p>
        <p className="text-xs text-navy-300 mt-1">{label}</p>
      </div>
    </div>
  )
}

/* ── Form field ── */
function Field({ label, children }) {
  return (
    <div>
      <label className="block text-xs font-semibold text-navy-300 mb-1.5 uppercase tracking-wide">
        {label}
      </label>
      {children}
    </div>
  )
}

const selectClass =
  'w-full px-3 py-2.5 text-sm bg-navy-900 border border-navy-600 rounded-xl text-gray-100 ' +
  'focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-violet-400 transition-all duration-150'

const inputClass =
  'w-full px-3 py-2.5 text-sm bg-navy-900 border border-navy-700 rounded-xl text-navy-300 ' +
  'cursor-not-allowed'

/* ── Section renderers ── */
function ChatSection({ selectedDocuments, setSelectedDocuments }) {
  return (
    <Section>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-1">
          <DocumentUpload onDocumentsChange={setSelectedDocuments} />
        </div>
        <div className="lg:col-span-2">
          <ChatInterface selectedDocuments={selectedDocuments} />
        </div>
      </div>
    </Section>
  )
}

function DocumentsSection() {
  return (
    <Section title="My Documents" description="All PDFs you've uploaded for analysis.">
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <p className="text-xs font-semibold uppercase tracking-widest text-navy-400">Recent uploads</p>
          </div>
          <div className="space-y-3">
            {[
              { name: 'Sample Document.pdf', ago: '2 days ago', pages: 24 },
            ].map(doc => (
              <div key={doc.name}
                className="flex items-center justify-between p-3.5 rounded-xl bg-navy-900
                           border border-navy-700 hover:border-violet-600/40 hover:bg-navy-900/80
                           transition-all duration-150">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-violet-600/15 border border-violet-500/20 flex items-center justify-center">
                    <FileText size={16} className="text-violet-400" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-100">{doc.name}</p>
                    <p className="text-xs text-navy-400">{doc.pages} pages · Uploaded {doc.ago}</p>
                  </div>
                </div>
                <button className="text-xs text-red-400 hover:text-red-300 px-2.5 py-1.5 rounded-lg
                                   hover:bg-red-900/30 transition-all duration-150 font-medium">
                  Delete
                </button>
              </div>
            ))}
          </div>
        </div>
      </Card>
    </Section>
  )
}

function HistorySection() {
  const items = [
    { title: 'Questions about climate change research', time: '2 hours ago', msgs: 6 },
    { title: 'Company financial analysis',              time: 'Yesterday',   msgs: 4 },
    { title: 'Legal contract review',                  time: '3 days ago',  msgs: 11 },
  ]
  return (
    <Section title="Chat History" description="Browse and revisit your previous conversations.">
      <Card>
        <div className="divide-y divide-navy-700">
          {items.map(item => (
            <button
              key={item.title}
              className="w-full flex items-center gap-4 px-6 py-4
                         hover:bg-navy-700/50 transition-colors duration-150 text-left"
            >
              <div className="w-9 h-9 rounded-xl bg-navy-700 flex items-center justify-center shrink-0">
                <MessageSquare size={16} className="text-navy-300" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-100 truncate">{item.title}</p>
                <p className="text-xs text-navy-400 mt-0.5">{item.msgs} messages · {item.time}</p>
              </div>
              <span className="text-2xs text-navy-400 shrink-0">&rsaquo;</span>
            </button>
          ))}
        </div>
      </Card>
    </Section>
  )
}

function UploadSection({ setSelectedDocuments }) {
  return (
    <Section title="Upload Documents" description="Add PDFs to your knowledge base.">
      <div className="max-w-lg">
        <DocumentUpload onDocumentsChange={setSelectedDocuments} />
      </div>
    </Section>
  )
}

function SettingsSection() {
  return (
    <Section title="Settings" description="Configure your AI model and retrieval preferences.">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <Card>
          <div className="p-6 space-y-5">
            <div className="flex items-center gap-2 mb-1">
              <Sliders size={16} className="text-violet-400" />
              <h3 className="text-sm font-semibold text-white">AI Model</h3>
            </div>
            <Field label="Language model">
              <select className={selectClass}>
                <option>GPT-4o-mini — Fast &amp; cost-effective</option>
                <option>GPT-4o — Balanced</option>
                <option>GPT-4 — Most accurate</option>
              </select>
            </Field>
            <Field label="Retrieval results">
              <select className={selectClass}>
                <option>Top 3 chunks</option>
                <option>Top 5 chunks (Recommended)</option>
                <option>Top 10 chunks</option>
              </select>
            </Field>
          </div>
        </Card>

        <Card>
          <div className="p-6 space-y-4">
            <div className="flex items-center gap-2 mb-1">
              <Settings size={16} className="text-violet-400" />
              <h3 className="text-sm font-semibold text-white">Features</h3>
            </div>
            {[
              { id: 'citations', label: 'Show source citations', desc: 'Display page-level references in answers', defaultChecked: true  },
              { id: 'memory',    label: 'Conversation memory',   desc: 'Remember context from previous turns',  defaultChecked: true  },
              { id: 'streaming', label: 'Streaming responses',   desc: 'Show answers as they are generated',    defaultChecked: false },
            ].map(opt => (
              <label key={opt.id}
                className="flex items-start gap-3 cursor-pointer p-3 rounded-xl hover:bg-navy-700/50 transition-colors duration-150">
                <input
                  type="checkbox"
                  defaultChecked={opt.defaultChecked}
                  className="mt-0.5 w-4 h-4 rounded accent-violet-500 cursor-pointer"
                />
                <div>
                  <p className="text-sm font-medium text-gray-100">{opt.label}</p>
                  <p className="text-xs text-navy-400 mt-0.5">{opt.desc}</p>
                </div>
              </label>
            ))}
          </div>
        </Card>
      </div>
    </Section>
  )
}

function ProfileSection({ user, documentCount }) {
  return (
    <Section title="Profile" description="Your account details and usage statistics.">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <Card>
          <div className="p-6 space-y-4">
            <div className="flex items-center gap-2 mb-1">
              <UserIcon size={16} className="text-violet-400" />
              <h3 className="text-sm font-semibold text-white">Account details</h3>
            </div>
            {!user ? (
              <div className="space-y-3">
                {[1, 2, 3].map(i => (
                  <div key={i} className="h-9 bg-navy-700 rounded-xl animate-pulse" />
                ))}
              </div>
            ) : (
              <>
                <Field label="Username">
                  <input type="text" value={user.username} disabled className={inputClass} />
                </Field>
                <Field label="Email">
                  <input type="email" value={user.email} disabled className={inputClass} />
                </Field>
                <Field label="Member since">
                  <input
                    type="text"
                    value={new Date(user.created_at).toLocaleDateString('en-US', {
                      year: 'numeric', month: 'long', day: 'numeric',
                    })}
                    disabled
                    className={inputClass}
                  />
                </Field>
              </>
            )}
          </div>
        </Card>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <StatCard label="Documents uploaded" value={documentCount} icon={FileText}       accent="violet" />
            <StatCard label="Total queries"       value="—"           icon={MessageSquare}   accent="violet" />
          </div>
          <Card>
            <div className="p-5 flex items-center gap-3">
              <BarChart3 size={16} className="text-navy-400" />
              <p className="text-xs text-navy-300">
                Detailed analytics coming soon — track usage, popular topics, and answer quality.
              </p>
            </div>
          </Card>
        </div>
      </div>
    </Section>
  )
}

/* ── Dashboard shell ── */
function Dashboard() {
  const [selectedDocuments, setSelectedDocuments] = useState([])
  const [activeSection, setActiveSection]         = useState('chat')
  const [user, setUser]                           = useState(null)
  const [documentCount, setDocumentCount]         = useState(0)

  useEffect(() => {
    api.getMe().then(setUser).catch(() => {})
    api.getDocuments()
      .then(data => setDocumentCount(data.total ?? 0))
      .catch(() => {})
  }, [])

  const sectionTitles = {
    chat:      'Chat',
    documents: 'My Documents',
    history:   'Chat History',
    upload:    'Upload',
    settings:  'Settings',
    profile:   'Profile',
  }

  const renderContent = () => {
    switch (activeSection) {
      case 'chat':
        return <ChatSection selectedDocuments={selectedDocuments} setSelectedDocuments={setSelectedDocuments} />
      case 'documents':
        return <DocumentsSection />
      case 'history':
        return <HistorySection />
      case 'upload':
        return <UploadSection setSelectedDocuments={setSelectedDocuments} />
      case 'settings':
        return <SettingsSection />
      case 'profile':
        return <ProfileSection user={user} documentCount={documentCount} />
      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-navy-950 flex">
      <Sidebar activeSection={activeSection} setActiveSection={setActiveSection} />

      <main className="flex-1 overflow-y-auto" role="main">
        {/* Top bar */}
        <div className="sticky top-0 z-10 bg-navy-950/90 backdrop-blur-sm border-b border-navy-800 px-8 py-4">
          <div className="flex items-center justify-between max-w-6xl mx-auto">
            <div>
              <h1 className="text-sm font-bold text-white">
                {sectionTitles[activeSection]}
              </h1>
            </div>
            {user && (
              <div className="flex items-center gap-2.5">
                <div className="w-7 h-7 rounded-full bg-violet-600 flex items-center justify-center">
                  <span className="text-xs font-bold text-white">
                    {user.username?.[0]?.toUpperCase() ?? 'U'}
                  </span>
                </div>
                <span className="text-xs font-medium text-navy-300">{user.username}</span>
              </div>
            )}
          </div>
        </div>

        <div className="max-w-6xl mx-auto px-8 py-8">
          {renderContent()}
        </div>
      </main>
    </div>
  )
}

export default Dashboard
