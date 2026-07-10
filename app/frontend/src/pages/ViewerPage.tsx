import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getChunks, getDocument, search as apiSearch } from '../api'
import ChunkPane from '../components/ChunkPane'
import PdfPane from '../components/PdfPane'
import type { Chunk, DocumentMeta, SearchHit } from '../types'
import { deriveItems } from '../viewerState'

type LoadState =
  | { status: 'loading' }
  | { status: 'error' }
  | { status: 'ready'; meta: DocumentMeta; chunks: Chunk[] }

export default function ViewerPage() {
  const { id = '' } = useParams<{ id: string }>()
  const [load, setLoad] = useState<LoadState>({ status: 'loading' })
  const [selectedChunkId, setSelectedChunkId] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [query, setQuery] = useState('')
  const [hits, setHits] = useState<SearchHit[] | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoad({ status: 'loading' })
    async function run() {
      try {
        const [meta, chunks] = await Promise.all([getDocument(id), getChunks(id)])
        if (!cancelled) setLoad({ status: 'ready', meta, chunks })
      } catch {
        if (!cancelled) setLoad({ status: 'error' })
      }
    }
    void run()
    return () => {
      cancelled = true
    }
  }, [id])

  const chunks = load.status === 'ready' ? load.chunks : []

  const selectChunk = useCallback(
    (chunkId: string) => {
      setSelectedChunkId(chunkId)
      const chunk = chunks.find((c) => c.id === chunkId)
      if (chunk) setCurrentPage(chunk.page_no)
    },
    [chunks],
  )

  async function runSearch(q: string) {
    try {
      const results = await apiSearch(q, { documentId: id, topK: 10 })
      setHits(results)
    } catch {
      setHits([])
    }
  }

  function onQueryChange(value: string) {
    setQuery(value)
    if (value.trim() === '') setHits(null)
  }

  const items = useMemo(() => deriveItems(chunks, hits), [hits, chunks])

  if (load.status === 'loading') {
    return <div className="p-6 text-slate-500">Loading document…</div>
  }
  if (load.status === 'error') {
    return (
      <div className="p-6">
        <p className="text-red-600">Document not found.</p>
        <Link to="/" className="mt-2 inline-block text-blue-600 hover:underline">
          ‹ Back to documents
        </Link>
      </div>
    )
  }

  return (
    <div className="flex h-full flex-col bg-slate-100">
      <header className="flex items-center gap-4 border-b border-slate-200 bg-white px-4 py-3">
        <Link to="/" className="text-sm text-blue-600 hover:underline">
          ‹ Back
        </Link>
        <span className="truncate font-medium text-slate-800" title={load.meta.filename}>
          {load.meta.filename}
        </span>
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
