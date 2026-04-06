import { FileText, Hash } from 'lucide-react'

function SourceCitation({ source }) {
  const score = source.relevance_score ?? 0
  const pct   = Math.round(score * 100)

  // Color the relevance bar by score tier
  const barColor =
    pct >= 80 ? 'bg-emerald-500' :
    pct >= 55 ? 'bg-violet-500'  :
                'bg-navy-500'

  const badgeBg =
    pct >= 80 ? 'bg-emerald-900/40 text-emerald-300 ring-1 ring-emerald-700/50' :
    pct >= 55 ? 'bg-violet-900/40  text-violet-300  ring-1 ring-violet-700/50'  :
                'bg-navy-700 text-navy-300 ring-1 ring-navy-600'

  return (
    <article className="group bg-navy-900 border border-navy-700 rounded-xl p-3
                        hover:border-violet-600/40 hover:bg-navy-800 transition-all duration-200">
      {/* Header row */}
      <div className="flex items-start gap-2.5">
        <div className="mt-0.5 w-7 h-7 rounded-lg bg-navy-700 flex items-center justify-center shrink-0
                        group-hover:bg-violet-600/20 transition-colors duration-200">
          <FileText size={13} className="text-navy-400 group-hover:text-violet-400 transition-colors duration-200" />
        </div>

        <div className="flex-1 min-w-0">
          {/* Filename + page */}
          <div className="flex items-center justify-between gap-2 mb-1.5">
            <p className="text-xs font-semibold text-gray-100 truncate leading-snug">
              {source.filename ?? 'Unknown document'}
            </p>
            <span className="flex items-center gap-1 shrink-0 text-2xs font-medium text-navy-400">
              <Hash size={9} />
              p.{source.page_number ?? '—'}
            </span>
          </div>

          {/* Chunk text */}
          {source.chunk_text && (
            <p className="text-xs text-navy-300 leading-relaxed line-clamp-2 mb-2">
              {source.chunk_text}
            </p>
          )}

          {/* Relevance bar + badge */}
          <div className="flex items-center gap-2">
            <div className="flex-1 h-1 rounded-full bg-navy-700 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${barColor}`}
                style={{ width: `${pct}%` }}
                role="progressbar"
                aria-valuenow={pct}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-label={`Relevance score: ${pct}%`}
              />
            </div>
            <span className={`text-2xs font-semibold px-1.5 py-0.5 rounded-md ${badgeBg}`}>
              {pct}%
            </span>
          </div>
        </div>
      </div>
    </article>
  )
}

export default SourceCitation
