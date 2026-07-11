import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getChunks, getDocument, getStatus, reprocessDocument, search as apiSearch } from '../api'
import ChunkPane from '../components/ChunkPane'
import ModeOcrSelector from '../components/ModeOcrSelector'
import PdfPane from '../components/PdfPane'
import type { Chunk, DocumentMeta, JobStatus, Mode, OcrEngine, SearchHit } from '../types'
import { deriveItems } from '../viewerState'

type LoadState =
  | { status: 'processing'; job: JobStatus }
  | { status: 'error'; message: string }
  | { status: 'ready'; meta: DocumentMeta; chunks: Chunk[] }

export default function ViewerPage() {
  const { id = '' } = useParams<{ id: string }>()
  const [load, setLoad] = useState<LoadState>({ status: 'processing', job: 'queued' })
  const [reloadKey, setReloadKey] = useState(0)
  const [mode, setMode] = useState<Mode>('fast')
  const [ocr, setOcr] = useState<OcrEngine>('none')
  const [selectorTouched, setSelectorTouched] = useState(false)
  const [selectedChunkId, setSelectedChunkId] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [query, setQuery] = useState('')
  const [hits, setHits] = useState<SearchHit[] | null>(null)

  useEffect(() => {
    let cancelled = false
    let timer: number | undefined
    setLoad({ status: 'processing', job: 'queued' })

    async function tick() {
      try {
        const status = await getStatus(id)
        if (cancelled) return
        if (!selectorTouched) {
          setMode(status.mode)
          setOcr(status.ocr)
        }
        if (status.status !== 'complete') {
          setLoad({ status: 'processing', job: status.status })
          timer = window.setTimeout(tick, 1200)
          return
        }
        if (status.error) {
          setLoad({ status: 'error', message: status.error })
          return
        }
        const [meta, chunks] = await Promise.all([getDocument(id), getChunks(id)])
        if (!cancelled) setLoad({ status: 'ready', meta, chunks })
      } catch {
        if (!cancelled) setLoad({ status: 'error', message: 'Document not found.' })
      }
    }

    void tick()
    return () => {
      cancelled = true
      if (timer) clearTimeout(timer)
    }
    // selectorTouched is intentionally read as a ref-like guard, not a trigger
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, reloadKey])

  const chunks = load.status === 'ready' ? load.chunks : []

  const selectChunk = useCallback(
    (chunkId: string) => {
      setSelectedChunkId(chunkId)
      const chunk = chunks.find((c) => c.id === chunkId)
      if (chunk) setCurrentPage(chunk.page_no)
    },
    [chunks],
  )

  async function reprocess() {
    try {
      await reprocessDocument(id, mode, ocr)
      setSelectedChunkId(null)
      setHits(null)
      setReloadKey((k) => k + 1)
    } catch {
      setLoad({ status: 'error', message: 'Reprocess failed.' })
    }
  }

  async function runSearch(q: string) {
    try {
      setHits(await apiSearch(q, { documentId: id, topK: 10 }))
    } catch {
      setHits([])
    }
  }

  function onQueryChange(value: string) {
    setQuery(value)
    if (value.trim() === '') setHits(null)
  }

  const items = useMemo(() => deriveItems(chunks, hits), [hits, chunks])

  if (load.status === 'processing') {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3 bg-slate-100 text-slate-600">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-slate-300 border-t-blue-500" />
        <p>Processing document… ({load.job})</p>
        <Link to="/" className="text-sm text-blue-600 hover:underline">
          ‹ Back
        </Link>
      </div>
    )
  }
  if (load.status === 'error') {
    return (
      <div className="p-6">
        <p className="text-red-600">{load.message}</p>
        <Link to="/" className="mt-2 inline-block text-blue-600 hover:underline">
          ‹ Back to documents
        </Link>
      </div>
    )
  }

  return (
    <div className="flex h-full flex-col bg-slate-100">
      <header className="flex flex-wrap items-center gap-4 border-b border-slate-200 bg-white px-4 py-3">
        <Link to="/" className="text-sm text-blue-600 hover:underline">
          ‹ Back
        </Link>
        <span className="truncate font-medium text-slate-800" title={load.meta.filename}>
          {load.meta.filename}
        </span>
        <div className="flex items-center gap-3">
          <ModeOcrSelector
            mode={mode}
            ocr={ocr}
            onMode={(m) => {
              setSelectorTouched(true)
              setMode(m)
            }}
            onOcr={(o) => {
              setSelectorTouched(true)
              setOcr(o)
            }}
          />
          <button
            type="button"
            onClick={() => void reprocess()}
            className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-50"
          >
            Reprocess
          </button>
        </div>
        <form
          className="ml-auto"
          onSubmit={(e) => {
            e.preventDefault()
            if (query.trim() !== '') void runSearch(query)
          }}
        >
          <input
            type="search"
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            placeholder="Search chunks…"
            className="w-64 rounded-lg border border-slate-300 px-3 py-1.5 text-sm focus:border-blue-400 focus:outline-none"
          />
        </form>
      </header>

      <div className="flex min-h-0 flex-1">
        <div className="min-w-0 flex-1 border-r border-slate-200">
          <PdfPane
            docId={id}
            chunks={chunks}
            numPages={load.meta.num_pages}
            currentPage={currentPage}
            selectedChunkId={selectedChunkId}
            onSelectChunk={selectChunk}
            onPageChange={setCurrentPage}
          />
        </div>
        <div className="w-[420px] shrink-0 bg-white">
          <ChunkPane items={items} selectedChunkId={selectedChunkId} onSelectChunk={selectChunk} />
        </div>
      </div>
    </div>
  )
}
