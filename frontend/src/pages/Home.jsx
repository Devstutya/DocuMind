import { Link } from 'react-router-dom'
import { Brain, ArrowRight, Upload, MessageSquare, BookOpen, Zap, Shield, BarChart2 } from 'lucide-react'

/* ── Feature card ── */
function FeatureCard({ icon: Icon, title, desc }) {
  return (
    <div className="group relative bg-navy-900/60 border border-navy-800 rounded-2xl p-6
                    hover:border-violet-700/60 hover:bg-navy-900/80 transition-all duration-200">
      <div className="w-10 h-10 rounded-xl bg-violet-600/15 border border-violet-500/20
                      flex items-center justify-center mb-4
                      group-hover:bg-violet-600/25 transition-colors duration-200">
        <Icon size={18} className="text-violet-400" />
      </div>
      <h3 className="text-sm font-semibold text-white mb-1.5">{title}</h3>
      <p className="text-xs text-navy-300 leading-relaxed">{desc}</p>
    </div>
  )
}

/* ── Step pill ── */
function Step({ n, label }) {
  return (
    <div className="flex items-center gap-3">
      <div className="w-8 h-8 rounded-full bg-violet-600/20 border border-violet-500/30
                      flex items-center justify-center shrink-0">
        <span className="text-xs font-bold text-violet-400">{n}</span>
      </div>
      <span className="text-sm text-gray-200">{label}</span>
    </div>
  )
}

const features = [
  {
    icon: Upload,
    title: 'Instant PDF ingestion',
    desc: 'Upload any PDF — DocuMind extracts and indexes the full text in seconds.',
  },
  {
    icon: MessageSquare,
    title: 'Conversational Q&A',
    desc: 'Ask natural-language questions and get precise answers with context memory.',
  },
  {
    icon: BookOpen,
    title: 'Page-level citations',
    desc: 'Every answer cites the exact page and document it was sourced from.',
  },
  {
    icon: Zap,
    title: 'Sub-second retrieval',
    desc: 'Semantic search across hundreds of documents in under 500 ms.',
  },
  {
    icon: Shield,
    title: 'Private by default',
    desc: 'Your documents are isolated to your account — never shared with other users.',
  },
  {
    icon: BarChart2,
    title: 'Usage insights',
    desc: 'Track which documents are queried most and how your knowledge base grows.',
  },
]

function Home() {
  return (
    <div className="min-h-screen bg-navy-950 text-white overflow-hidden">
      {/* ── Glow blobs ── */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden" aria-hidden="true">
        <div className="absolute top-[-20%] left-[40%] w-[600px] h-[600px]
                        rounded-full bg-violet-700/12 blur-3xl" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px]
                        rounded-full bg-navy-600/20 blur-3xl" />
      </div>

      {/* ── Nav ── */}
      <header className="relative z-10 border-b border-navy-800/60">
        <nav className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-violet-700
                            flex items-center justify-center shadow-lg">
              <Brain size={16} className="text-white" />
            </div>
            <span className="font-bold text-base tracking-tight">DocuMind</span>
          </div>
          <div className="flex items-center gap-3">
            <Link
              to="/demo"
              className="text-sm text-navy-300 hover:text-white px-3 py-1.5
                         transition-colors duration-150 font-medium"
            >
              Try demo
            </Link>
            <Link
              to="/login"
              className="text-sm font-semibold text-white bg-violet-600 hover:bg-violet-700
                         px-4 py-1.5 rounded-lg transition-colors duration-150"
            >
              Sign in
            </Link>
          </div>
        </nav>
      </header>

      {/* ── Hero ── */}
      <main>
        <section className="relative z-10 max-w-6xl mx-auto px-6 pt-24 pb-20 text-center">
          {/* Tag */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full
                          bg-violet-600/10 border border-violet-500/20 text-violet-400
                          text-xs font-semibold mb-8 tracking-wide">
            <Zap size={11} />
            Powered by GPT-4o &amp; Pinecone semantic search
          </div>

          <h1 className="text-5xl sm:text-6xl font-extrabold leading-[1.08] tracking-tight mb-6 text-balance">
            Ask questions.<br />
            <span className="gradient-text">Get answers from your PDFs.</span>
          </h1>

          <p className="text-lg text-navy-300 max-w-xl mx-auto mb-10 leading-relaxed">
            Upload any document. Ask anything. DocuMind retrieves the exact passages
            and gives you cited, confident answers — in seconds.
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mb-16">
            <Link
              to="/login"
              className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-700 text-white
                         font-semibold text-sm px-6 py-3 rounded-xl shadow-lg shadow-violet-900/30
                         transition-all duration-150 active:scale-[0.98]"
            >
              Get started free
              <ArrowRight size={16} />
            </Link>
            <Link
              to="/demo"
              className="inline-flex items-center gap-2 bg-navy-800 hover:bg-navy-700 text-navy-200
                         font-semibold text-sm px-6 py-3 rounded-xl border border-navy-700
                         hover:border-navy-600 transition-all duration-150"
            >
              Try without signing up
            </Link>
          </div>

          {/* How it works */}
          <div className="inline-flex flex-col sm:flex-row items-center gap-4 sm:gap-8
                          bg-navy-900/50 border border-navy-800 rounded-2xl px-8 py-5 mx-auto">
            <Step n="1" label="Upload your PDF" />
            <div className="hidden sm:block w-px h-8 bg-navy-700" aria-hidden="true" />
            <Step n="2" label="Ask any question" />
            <div className="hidden sm:block w-px h-8 bg-navy-700" aria-hidden="true" />
            <Step n="3" label="Get cited answers" />
          </div>
        </section>

        {/* ── Features grid ── */}
        <section className="relative z-10 max-w-6xl mx-auto px-6 pb-24">
          <div className="text-center mb-10">
            <h2 className="text-2xl font-bold text-white mb-2">Everything you need</h2>
            <p className="text-sm text-navy-300">Built for researchers, analysts, and teams who need answers fast.</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {features.map(f => <FeatureCard key={f.title} {...f} />)}
          </div>
        </section>

        {/* ── CTA strip ── */}
        <section className="relative z-10 border-t border-navy-800/60">
          <div className="max-w-6xl mx-auto px-6 py-16 text-center">
            <h2 className="text-2xl font-bold text-white mb-3">
              Ready to unlock your documents?
            </h2>
            <p className="text-sm text-navy-300 mb-8">
              Free to start. No credit card required.
            </p>
            <Link
              to="/login"
              className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-700
                         text-white font-semibold text-sm px-8 py-3.5 rounded-xl shadow-lg
                         shadow-violet-900/30 transition-all duration-150 active:scale-[0.98]"
            >
              Create your account
              <ArrowRight size={16} />
            </Link>
          </div>
        </section>
      </main>

      {/* ── Footer ── */}
      <footer className="relative z-10 border-t border-navy-800/60 py-6">
        <div className="max-w-6xl mx-auto px-6 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain size={14} className="text-navy-500" />
            <span className="text-xs text-navy-500 font-medium">DocuMind</span>
          </div>
          <p className="text-xs text-navy-500">AI-powered document Q&amp;A</p>
        </div>
      </footer>
    </div>
  )
}

export default Home
