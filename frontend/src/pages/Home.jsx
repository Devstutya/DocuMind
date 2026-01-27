import { Link } from 'react-router-dom'

function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-900 mb-4">
          DocuMind
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          AI-Powered Document Q&A Assistant
        </p>
        <div className="space-x-4">
          <Link
            to="/login"
            className="inline-block bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition"
          >
            Get Started
          </Link>
          <Link
            to="/dashboard"
            className="inline-block bg-white text-indigo-600 px-6 py-3 rounded-lg hover:bg-gray-50 transition border border-indigo-600"
          >
            Dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}

export default Home
