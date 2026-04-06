import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Brain, AlertCircle, Loader, ArrowLeft } from 'lucide-react'
import api from '../services/api'

const inputClass =
  'w-full px-4 py-2.5 text-sm bg-navy-900 border border-navy-600 rounded-xl ' +
  'text-gray-100 placeholder:text-navy-500 ' +
  'focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-violet-500 ' +
  'transition-all duration-150'

function Login() {
  const [isLogin, setIsLogin] = useState(true)
  const [formData, setFormData] = useState({ email: '', username: '', password: '' })
  const [error, setError]   = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleChange = (field) => (e) =>
    setFormData(prev => ({ ...prev, [field]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (isLogin) {
        await api.login(formData.username, formData.password)
      } else {
        await api.register(formData.email, formData.username, formData.password)
        await api.login(formData.username, formData.password)
      }
      navigate('/dashboard')
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const switchMode = () => {
    setIsLogin(v => !v)
    setError('')
  }

  return (
    <div className="min-h-screen bg-navy-950 flex items-center justify-center p-4">
      {/* Background texture */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden="true">
        <div className="absolute -top-40 -right-40 w-96 h-96 rounded-full
                        bg-violet-600/10 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 rounded-full
                        bg-navy-600/20 blur-3xl" />
      </div>

      <div className="relative w-full max-w-sm">
        {/* Back link */}
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-navy-400 hover:text-navy-200
                     text-xs font-medium mb-8 transition-colors duration-150"
        >
          <ArrowLeft size={14} />
          Back to home
        </Link>

        {/* Card */}
        <div className="bg-navy-900 rounded-3xl shadow-2xl overflow-hidden border border-navy-700">
          {/* Header stripe */}
          <div className="px-8 pt-8 pb-6 border-b border-navy-700">
            <div className="flex items-center gap-3 mb-5">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-violet-700
                              flex items-center justify-center shadow-lg">
                <Brain size={18} className="text-white" />
              </div>
              <span className="font-bold text-white text-base tracking-tight">DocuMind</span>
            </div>

            {/* Tabs */}
            <div className="flex bg-navy-800 rounded-xl p-1 gap-1">
              {['Login', 'Sign Up'].map((tab, i) => {
                const active = isLogin === (i === 0)
                return (
                  <button
                    key={tab}
                    onClick={() => { setIsLogin(i === 0); setError('') }}
                    className={[
                      'flex-1 py-2 text-xs font-semibold rounded-lg transition-all duration-200',
                      active
                        ? 'bg-navy-700 text-white shadow-sm'
                        : 'text-navy-400 hover:text-navy-200',
                    ].join(' ')}
                  >
                    {tab}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Form */}
          <div className="px-8 py-6">
            {error && (
              <div className="flex items-center gap-2 bg-red-900/30 border border-red-700/50 text-red-300
                              px-3 py-2.5 rounded-xl text-xs mb-5 animate-fade-in" role="alert">
                <AlertCircle size={14} className="shrink-0" />
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4" noValidate>
              {!isLogin && (
                <div className="animate-fade-up">
                  <label htmlFor="email" className="block text-xs font-semibold text-navy-300 mb-1.5 uppercase tracking-wide">
                    Email
                  </label>
                  <input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={handleChange('email')}
                    placeholder="you@example.com"
                    autoComplete="email"
                    required
                    className={inputClass}
                  />
                </div>
              )}

              <div>
                <label htmlFor="username" className="block text-xs font-semibold text-navy-300 mb-1.5 uppercase tracking-wide">
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  value={formData.username}
                  onChange={handleChange('username')}
                  placeholder={isLogin ? 'Your username' : 'Choose a username'}
                  autoComplete={isLogin ? 'username' : 'username'}
                  required
                  className={inputClass}
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-xs font-semibold text-navy-300 mb-1.5 uppercase tracking-wide">
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  value={formData.password}
                  onChange={handleChange('password')}
                  placeholder={isLogin ? 'Your password' : 'Choose a strong password'}
                  autoComplete={isLogin ? 'current-password' : 'new-password'}
                  required
                  className={inputClass}
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-2 py-2.5 px-4 bg-violet-600 hover:bg-violet-700
                           text-white text-sm font-semibold rounded-xl shadow-sm
                           flex items-center justify-center gap-2
                           active:scale-[0.99] disabled:opacity-60 disabled:cursor-not-allowed
                           transition-all duration-150"
              >
                {loading && <Loader size={15} className="animate-spin" />}
                {loading ? 'Please wait…' : isLogin ? 'Sign in' : 'Create account'}
              </button>
            </form>

            <p className="text-center text-xs text-navy-400 mt-5">
              {isLogin ? "Don't have an account? " : 'Already have an account? '}
              <button
                onClick={switchMode}
                className="text-violet-400 font-semibold hover:text-violet-300 transition-colors duration-150"
              >
                {isLogin ? 'Sign up free' : 'Sign in'}
              </button>
            </p>
          </div>
        </div>

        <p className="text-center text-xs text-navy-400 mt-6">
          Want to explore first?{' '}
          <Link to="/demo" className="text-navy-300 hover:text-white underline transition-colors duration-150">
            Try the demo
          </Link>
        </p>
      </div>
    </div>
  )
}

export default Login
