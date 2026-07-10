import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getDocument, listDocuments } from '../api'
import type { DocumentMeta } from '../types'

type State =
  | { status: 'loading' }
  | { status: 'error' }
  | { status: 'ready'; docs: DocumentMeta[] }

export default function DocumentList() {
  const [state, setState] = useState<State>({ status: 'loading' })

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const ids = await listDocuments()
        const docs = await Promise.all(ids.map((id) => getDocument(id)))
        if (!cancelled) setState({ status: 'ready', docs })
      } catch {
        if (!cancelled) setState({ status: 'error' })
      }
    }
    void load()
    return () => {
      cancelled = true
    }
  }, [])

  if (state.status === 'loading') {
    return <p className="text-slate-500">Loading documents…</p>
  }
  if (state.status === 'error') {
    return <p className="text-red-600">Could not load documents. Is the backend running?</p>
  }
  if (state.docs.length === 0) {
    return <p className="text-slate-500">No documents yet. Upload one above to get started.</p>
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {state.docs.map((doc) => (
        <Link
          key={doc.id}
          to={`/doc/${encodeURIComponent(doc.id)}`}
          className="flex flex-col gap-2 rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md"
        >
          <span className="text-2xl">📄</span>
          <span className="truncate font-medium text-slate-800" title={doc.filename}>
            {doc.filename}
          </span>
          <span className="text-sm text-slate-500">
            {doc.num_pages} pages · {doc.num_chunks} chunks
          </span>
        </Link>
      ))}
    </div>
  )
}
