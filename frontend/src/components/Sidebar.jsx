import { Link } from 'react-router-dom'
import { FileText, MessageSquare, Settings, User, LogOut, Upload, History, Brain } from 'lucide-react'

const navItems = [
  { id: 'chat',      icon: MessageSquare, label: 'Chat'        },
  { id: 'documents', icon: FileText,      label: 'My Documents'},
  { id: 'history',   icon: History,       label: 'Chat History'},
  { id: 'upload',    icon: Upload,        label: 'Upload'      },
  { id: 'settings',  icon: Settings,      label: 'Settings'   },
  { id: 'profile',   icon: User,          label: 'Profile'    },
]

function Sidebar({ activeSection, setActiveSection }) {
  return (
    <aside
      className="w-60 shrink-0 bg-navy-950 flex flex-col border-r border-navy-800"
      style={{ minHeight: '100vh' }}
      aria-label="Main navigation"
    >
      {/* Logo */}
      <div className="px-5 py-6 border-b border-navy-800">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-violet-700 flex items-center justify-center shadow-lg">
            <Brain size={16} className="text-white" />
          </div>
          <div>
            <span className="text-white font-bold text-base tracking-tight">DocuMind</span>
            <p className="text-navy-400 text-2xs leading-none mt-0.5 font-medium uppercase tracking-widest">
              AI Assistant
            </p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4">
        <p className="px-3 mb-2 text-2xs font-semibold uppercase tracking-widest text-navy-500">
          Workspace
        </p>
        <ul className="space-y-0.5" role="list">
          {navItems.map(({ id, icon: Icon, label }) => {
            const isActive = activeSection === id
            return (
              <li key={id}>
                <button
                  onClick={() => setActiveSection(id)}
                  aria-current={isActive ? 'page' : undefined}
                  className={[
                    'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium',
                    'transition-all duration-150 cursor-pointer',
                    isActive
                      ? 'bg-violet-600/20 text-violet-300 shadow-sm'
                      : 'text-navy-400 hover:bg-navy-800 hover:text-navy-100',
                  ].join(' ')}
                >
                  <Icon
                    size={17}
                    className={[
                      'shrink-0 transition-colors duration-150',
                      isActive ? 'text-violet-400' : 'text-navy-500 group-hover:text-navy-300',
                    ].join(' ')}
                    strokeWidth={isActive ? 2.5 : 2}
                  />
                  {label}
                  {isActive && (
                    <span className="ml-auto w-1 h-1 rounded-full bg-violet-400" aria-hidden="true" />
                  )}
                </button>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* Footer */}
      <div className="px-3 py-4 border-t border-navy-800">
        <Link
          to="/"
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                     text-navy-400 hover:bg-navy-800 hover:text-red-400 transition-all duration-150"
        >
          <LogOut size={17} className="shrink-0" />
          Sign out
        </Link>
      </div>
    </aside>
  )
}

export default Sidebar
