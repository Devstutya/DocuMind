import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, AlertCircle, MessageSquare } from 'lucide-react'
import api from '../services/api'
import SourceCitation from './SourceCitation'

/* ── Typing indicator ── */
function TypingIndicator() {
  return (
    <div className="flex items-end gap-2.5 animate-fade-in">
      <div className="w-8 h-8 rounded-full bg-violet-600/20 flex items-center justify-center shrink-0">
        <Bot size={15} className="text-violet-400" />
      </div>
      <div className="bg-navy-800 border border-navy-700 rounded-2xl rounded-bl-sm px-4 py-3">
        <div className="flex gap-1.5 items-center h-4">
          {[0, 1, 2].map(i => (
            <span
              key={i}
              className="w-1.5 h-1.5 rounded-full bg-navy-400 inline-block"
              style={{
                animation: 'bounce-dot 1.2s ease-in-out infinite',
                animationDelay: `${i * 180}ms`,
              }}
              aria-hidden="true"
            />
          ))}
        </div>
      </div>
    </div>
  )
}

/* ── Empty state ── */
function EmptyState({ onPromptClick }) {
  const prompts = [
    'What are the key findings in this document?',
    'Summarize the main arguments made.',
    'What methodology was used in this study?',
  ]
  return (
    <div className="flex flex-col items-center justify-center h-full px-6 text-center animate-fade-in">
      <div className="w-14 h-14 rounded-2xl bg-violet-600/15 border border-violet-500/20 flex items-center justify-center mb-4">
        <MessageSquare size={24} className="text-violet-400" />
      </div>
      <p className="text-sm font-semibold text-gray-100 mb-1">Ask anything about your documents</p>
      <p className="text-xs text-navy-400 mb-6 max-w-xs">
        Upload a PDF and ask questions — DocuMind will cite the exact pages where it found the answer.
      </p>
      <div className="flex flex-col gap-2 w-full max-w-sm">
        {prompts.map(p => (
          <button
            key={p}
            onClick={() => onPromptClick(p)}
            className="text-xs text-navy-300 bg-navy-800 border border-navy-700 rounded-lg px-3 py-2
                       text-left hover:bg-navy-700 hover:border-violet-600/40 hover:text-white
                       transition-all duration-150 cursor-pointer"
          >
            {p}
          </button>
        ))}
      </div>
    </div>
  )
}

/* ── Message bubble ── */
function Message({ message }) {
  const isUser = message.role === 'user'
  const isError = message.role === 'error'

  if (isUser) {
    return (
      <div className="flex justify-end gap-2.5 animate-fade-up">
        <div className="max-w-[72%]">
          <div className="bg-violet-600 text-white rounded-2xl rounded-br-sm px-4 py-3 shadow-sm">
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
          </div>
          <p className="text-2xs text-navy-400 mt-1 text-right px-1">
            {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </p>
        </div>
        <div className="w-8 h-8 rounded-full bg-violet-600/20 flex items-center justify-center shrink-0 mt-0.5">
          <User size={15} className="text-violet-400" />
        </div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="flex items-start gap-2.5 animate-fade-up">
        <div className="w-8 h-8 rounded-full bg-red-900/40 flex items-center justify-center shrink-0">
          <AlertCircle size={15} className="text-red-400" />
        </div>
        <div className="max-w-[72%] bg-red-900/30 border border-red-700/50 rounded-2xl rounded-bl-sm px-4 py-3">
          <p className="text-sm text-red-300 leading-relaxed">{message.content}</p>
        </div>
      </div>
    )
  }

  // Assistant
  return (
    <div className="flex items-start gap-2.5 animate-fade-up">
      <div className="w-8 h-8 rounded-full bg-violet-600/20 flex items-center justify-center shrink-0 mt-0.5">
        <Bot size={15} className="text-violet-400" />
      </div>
      <div className="max-w-[80%]">
        <div className="bg-navy-800 border border-navy-700 rounded-2xl rounded-bl-sm px-4 py-3 shadow-card">
          <p className="text-sm text-gray-100 leading-relaxed whitespace-pre-wrap">{message.content}</p>

          {message.sources && message.sources.length > 0 && (
            <div className="mt-4 pt-3 border-t border-navy-700">
              <p className="text-2xs font-semibold uppercase tracking-widest text-navy-400 mb-2">
                Sources
              </p>
              <div className="space-y-1.5">
                {message.sources.map((source, idx) => (
                  <SourceCitation key={idx} source={source} />
                ))}
              </div>
            </div>
          )}
        </div>
        <p className="text-2xs text-navy-400 mt-1 px-1">
          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </div>
  )
}

/* ── Main component ── */
function ChatInterface({ selectedDocuments }) {
  const [messages, setMessages]         = useState([])
  const [input, setInput]               = useState('')
  const [loading, setLoading]           = useState(false)
  const [conversationId, setConversationId] = useState(null)
  const messagesEndRef = useRef(null)
  const inputRef       = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => { scrollToBottom() }, [messages, loading])

  const submitQuery = async (text) => {
    if (!text.trim() || loading) return

    setMessages(prev => [...prev, {
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    }])
    setInput('')
    setLoading(true)

    try {
      const response = await api.query(
        text,
        selectedDocuments.length > 0 ? selectedDocuments : null,
        conversationId
      )
      setConversationId(response.conversation_id)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        timestamp: new Date().toISOString(),
      }])
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'error',
        content: err.message || 'Failed to get a response. Please try again.',
        timestamp: new Date().toISOString(),
      }])
    } finally {
      setLoading(false)
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    submitQuery(input)
  }

  return (
    <div className="bg-navy-900 rounded-2xl border border-navy-700 shadow-card flex flex-col h-[calc(100vh-10rem)]">
      {/* Header */}
      <div className="px-5 py-4 border-b border-navy-700 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-violet-600 flex items-center justify-center">
          <Bot size={16} className="text-white" />
        </div>
        <div>
          <h2 className="text-sm font-semibold text-white">DocuMind Chat</h2>
          <p className="text-2xs text-navy-400">
            {selectedDocuments.length > 0
              ? `Searching across ${selectedDocuments.length} document${selectedDocuments.length > 1 ? 's' : ''}`
              : 'No documents selected'}
          </p>
        </div>
        {messages.length > 0 && (
          <button
            onClick={() => { setMessages([]); setConversationId(null) }}
            className="ml-auto text-2xs text-navy-400 hover:text-navy-200 transition-colors
                       px-2.5 py-1 rounded-md hover:bg-navy-700"
          >
            Clear chat
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-5 py-5 space-y-4">
        {messages.length === 0 && !loading && (
          <EmptyState onPromptClick={prompt => submitQuery(prompt)} />
        )}
        {messages.map((msg, i) => <Message key={i} message={msg} />)}
        {loading && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="px-4 py-4 border-t border-navy-700">
        <form onSubmit={handleSubmit} className="flex gap-2 items-end">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              rows={1}
              value={input}
              onChange={e => {
                setInput(e.target.value)
                // Auto-grow
                e.target.style.height = 'auto'
                e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px'
              }}
              onKeyDown={e => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSubmit(e)
                }
              }}
              placeholder="Ask a question about your documents…"
              disabled={loading}
              aria-label="Chat message input"
              className="w-full resize-none px-4 py-2.5 text-sm bg-navy-800 border border-navy-600 rounded-xl
                         text-gray-100 placeholder:text-navy-500
                         focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-violet-500
                         disabled:opacity-50 disabled:cursor-not-allowed
                         transition-all duration-150 leading-relaxed overflow-hidden"
              style={{ minHeight: '42px' }}
            />
          </div>
          <button
            type="submit"
            disabled={loading || !input.trim()}
            aria-label="Send message"
            className="shrink-0 w-10 h-10 rounded-xl bg-violet-600 text-white
                       flex items-center justify-center shadow-sm
                       hover:bg-violet-700 active:scale-95
                       disabled:opacity-40 disabled:cursor-not-allowed disabled:active:scale-100
                       transition-all duration-150"
          >
            <Send size={16} />
          </button>
        </form>
        <p className="text-2xs text-navy-500 mt-2 px-1">
          Press Enter to send · Shift+Enter for new line
        </p>
      </div>
    </div>
  )
}

export default ChatInterface
