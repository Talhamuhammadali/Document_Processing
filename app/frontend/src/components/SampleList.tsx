import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { listAvailable, openDocument } from '../api'
import type { AvailableDoc } from '../types'

type State =
  | { status: 'loading' }
  | { status: 'error' }
  | { status: 'ready'; docs: AvailableDoc[] }

export default function SampleList() {
  const navigate = useNavigate()
  const [state, setState] = useState<State>({ status: 'loading' })
  const [opening, setOpening] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const docs = await listAvailable()
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

  async function open(doc: AvailableDoc) {
    setOpening(doc.id)
    try {
      const result = await openDocument(doc.filename)
      navigate(`/doc/${encodeURIComponent(result.document_id)}`)
    } catch {
      setOpening(null)
    }
  }

  if (state.status === 'loading') {
    return <p className="text-slate-500">Loading samples…</p>
  }
  if (state.status === 'error') {
    return <p className="text-red-600">Could not load samples. Is the backend running?</p>
  }
  if (state.docs.length === 0) {
    return <p className="text-slate-500">No samples found in the data folder.</p>
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {state.docs.map((doc) => (
        <button
          key={doc.id}
          type="button"
          onClick={() => void open(doc)}
          disabled={opening !== null}
          className="flex flex-col gap-2 rounded-xl border border-slate-200 bg-white p-4 text-left shadow-sm transition-shadow hover:shadow-md disabled:opacity-60"
        >
          <div className="flex items-center justify-between">
            <span className="text-2xl">📄</span>
            {doc.processed && (
              <span className="rounded bg-emerald-100 px-1.5 py-0.5 text-xs text-emerald-700">
                processed
              </span>
            )}
          </div>
          <span className="truncate font-medium text-slate-800" title={doc.filename}>
            {doc.filename}
          </span>
          <span className="text-sm text-blue-600">
            {opening === doc.id ? 'Opening…' : 'Open →'}
          </span>
        </button>
      ))}
    </div>
  )
}
