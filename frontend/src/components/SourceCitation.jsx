import { FileText } from 'lucide-react'

function SourceCitation({ source }) {
  return (
    <div className="bg-white border border-gray-200 rounded p-3 text-sm">
      <div className="flex items-start space-x-2">
        <FileText className="h-4 w-4 text-indigo-600 mt-0.5 flex-shrink-0" />
        <div className="flex-1">
          <div className="flex items-center justify-between mb-1">
            <span className="font-medium text-gray-900">{source.filename}</span>
            <span className="text-xs text-gray-500">
              Page {source.page_number}
            </span>
          </div>
          <p className="text-gray-600 text-xs line-clamp-2">
            {source.chunk_text}
          </p>
          <div className="mt-1">
            <span className="text-xs text-indigo-600">
              Relevance: {(source.relevance_score * 100).toFixed(0)}%
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SourceCitation
