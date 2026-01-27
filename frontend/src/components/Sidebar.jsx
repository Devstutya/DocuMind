import { Link } from 'react-router-dom'
import { FileText, MessageSquare, Settings, User, LogOut, Upload, History } from 'lucide-react'

function Sidebar({ activeSection, setActiveSection }) {
  const sidebarItems = [
    { id: 'chat', icon: MessageSquare, label: 'Chat' },
    { id: 'documents', icon: FileText, label: 'My Documents' },
    { id: 'history', icon: History, label: 'Chat History' },
    { id: 'upload', icon: Upload, label: 'Upload' },
    { id: 'settings', icon: Settings, label: 'Settings' },
    { id: 'profile', icon: User, label: 'Profile' },
  ]

  return (
    <div className="w-64 bg-white shadow-lg flex flex-col">
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-2xl font-bold text-gray-900">DocuMind</h1>
        <p className="text-sm text-gray-500 mt-1">Dashboard</p>
      </div>

      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {sidebarItems.map((item) => {
            const Icon = item.icon
            return (
              <li key={item.id}>
                <button
                  onClick={() => setActiveSection(item.id)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition ${
                    activeSection === item.id
                      ? 'bg-indigo-50 text-indigo-700'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <Icon size={20} />
                  <span className="font-medium">{item.label}</span>
                </button>
              </li>
            )
          })}
        </ul>
      </nav>

      <div className="p-4 border-t border-gray-200">
        <Link
          to="/"
          className="flex items-center space-x-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg transition"
        >
          <LogOut size={20} />
          <span className="font-medium">Logout</span>
        </Link>
      </div>
    </div>
  )
}

export default Sidebar
