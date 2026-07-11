import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { listAvailable, openDocument, startCompare } from '../api'
import type { AvailableDoc, Mode, OcrEngine } from '../types'

interface Props {
  mode: Mode
  ocr: OcrEngine
}

type State =
  | { status: 'loading' }
  | { status: 'error' }
  | { status: 'ready'; docs: AvailableDoc[] }

export default function SampleList({ mode, ocr }: Props) {
  const navigate = useNavigate()
  const [state, setState] = useState<State>({ status: 'loading' })
  const [busy, setBusy] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    listAvailable()
      .then((docs) => !cancelled && setState({ status: 'ready', docs }))
      .catch(() => !cancelled && setState({ status: 'error' }))
    return () => {
      cancelled = true
    }
  }, [])

  async function open(doc: AvailableDoc) {
    setBusy(doc.id)
    try {
      const result = await openDocument(doc.filename, mode, ocr)
      navigate(`/doc/${encodeURIComponent(result.document_id)}`)
    } catch {
      setBusy(null)
    }
  }

  async function compare(doc: AvailableDoc) {
    setBusy(doc.id)
    try {
      await startCompare(doc.filename)
      navigate(`/compare/${encodeURIComponent(doc.id)}`)
    } catch {
      setBusy(null)
    }
  }

  if (state.status === 'loading') return <p className="text-slate-500">Loading samples…</p>
  if (state.status === 'error') {
    return <p className="text-red-600">Could not load samples. Is the backend running?</p>
  }
  if (state.docs.length === 0) return <p className="text-slate-500">No PDFs found under the data folder.</p>

  return (
    <div className="space-y-6">
      {groupByFolder(state.docs).map(([folder, docs]) => (
        <div key={folder}>
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-400">{folder}</h2>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {docs.map((doc) => (
              <div
                key={doc.id}
                className="flex flex-col gap-2 rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
              >
                <div className="flex items-center justify-between">
                  <span className="text-2xl">📄</span>
                  {doc.processed && (
                    <span className="rounded bg-emerald-100 px-1.5 py-0.5 text-xs text-emerald-700">
                      processed
                    </span>
                  )}
                </div>
                <span className="truncate font-medium text-slate-800" title={doc.name}>
                  {doc.name}
                </span>
                <div className="mt-1 flex gap-2">
                  <button
                    type="button"
                    disabled={busy !== null}
                    onClick={() => void open(doc)}
                    className="flex-1 rounded-lg bg-blue-500 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-600 disabled:opacity-50"
                  >
                    {busy === doc.id ? '…' : 'Open'}
                  </button>
                  <button
                    type="button"
                    disabled={busy !== null}
                    onClick={() => void compare(doc)}
                    className="flex-1 rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-50"
                  >
                    Compare
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

function groupByFolder(docs: AvailableDoc[]): [string, AvailableDoc[]][] {
  const map = new Map<string, AvailableDoc[]>()
  for (const doc of docs) {
    const arr = map.get(doc.folder) ?? []
    arr.push(doc)
    map.set(doc.folder, arr)
  }
  return [...map.entries()].sort(([a], [b]) => a.localeCompare(b))
}
