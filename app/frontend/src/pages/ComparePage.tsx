import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getChunks, getCompare, getDocument, reprocessCompare } from '../api'
import PdfPane from '../components/PdfPane'
import type { Chunk, CompareVariant } from '../types'

const MAX_SELECTED = 3

export default function ComparePage() {
  const { stem = '' } = useParams<{ stem: string }>()
  const [variants, setVariants] = useState<CompareVariant[] | null>(null)
  const [error, setError] = useState(false)
  const [selected, setSelected] = useState<string[]>([])
  const [focusId, setFocusId] = useState<string | null>(null)
  const [chunksBy, setChunksBy] = useState<Record<string, Chunk[]>>({})
  const [numPagesBy, setNumPagesBy] = useState<Record<string, number>>({})
  const [selectedChunkId, setSelectedChunkId] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [reload, setReload] = useState(0)
  const [rerunning, setRerunning] = useState(false)
  const requested = useRef<Set<string>>(new Set())

  useEffect(() => {
    let cancelled = false
    let timer: number | undefined
    async function tick() {
      try {
        const res = await getCompare(stem)
        if (cancelled) return
        setVariants(res.variants)
        if (res.variants.some((v) => v.status !== 'complete')) {
          timer = window.setTimeout(tick, 1500)
        }
      } catch {
        if (!cancelled) setError(true)
      }
    }
    void tick()
    return () => {
      cancelled = true
      if (timer) clearTimeout(timer)
    }
  }, [stem, reload])

  async function rerun() {
    setRerunning(true)
    try {
      await reprocessCompare(stem)
      requested.current.clear()
      setChunksBy({})
      setNumPagesBy({})
      setSelectedChunkId(null)
      setReload((r) => r + 1)
    } catch {
      setError(true)
    } finally {
      setRerunning(false)
    }
  }

  useEffect(() => {
    if (variants && selected.length === 0) {
      const init = variants.slice(0, 2).map((v) => v.id)
      setSelected(init)
      setFocusId(init[0] ?? null)
    }
  }, [variants, selected.length])

  useEffect(() => {
    if (!variants) return
    for (const v of variants) {
      if (!selected.includes(v.id) || v.status !== 'complete' || v.error) continue
      if (requested.current.has(v.id)) continue
      requested.current.add(v.id)
      void getChunks(v.id)
        .then((c) => setChunksBy((m) => ({ ...m, [v.id]: c })))
        .catch(() => requested.current.delete(v.id))
      void getDocument(v.id).then((d) => setNumPagesBy((m) => ({ ...m, [v.id]: d.num_pages }))).catch(() => {})
    }
  }, [variants, selected])

  function toggle(id: string) {
    setSelected((cur) => {
      if (cur.includes(id)) {
        const next = cur.filter((x) => x !== id)
        if (focusId === id) setFocusId(next[0] ?? null)
        return next
      }
      if (cur.length >= MAX_SELECTED) return cur
      if (focusId === null) setFocusId(id)
      return [...cur, id]
    })
  }

  function selectChunk(variantId: string, chunkId: string) {
    setFocusId(variantId)
    setSelectedChunkId(chunkId)
    const chunk = chunksBy[variantId]?.find((c) => c.id === chunkId)
    if (chunk) setCurrentPage(chunk.page_no)
  }

  if (error) {
    return (
      <div className="p-6">
        <p className="text-red-600">Could not load comparison.</p>
        <Link to="/" className="mt-2 inline-block text-blue-600 hover:underline">
          ‹ Back to documents
        </Link>
      </div>
    )
  }
  if (!variants) return <div className="p-6 text-slate-500">Loading comparison…</div>

  const shown = variants.filter((v) => selected.includes(v.id))
  const focus = shown.find((v) => v.id === focusId) ?? null

  return (
    <div className="flex h-full flex-col bg-slate-100">
      <header className="flex items-center gap-4 border-b border-slate-200 bg-white px-4 py-3">
        <Link to="/" className="text-sm text-blue-600 hover:underline">
          ‹ Back
        </Link>
        <span className="truncate font-medium text-slate-800">Compare configs · {stem}</span>
        <button
          type="button"
          onClick={() => void rerun()}
          disabled={rerunning}
          className="ml-auto rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-50"
        >
          {rerunning ? 'Re-running…' : 'Re-run all'}
        </button>
      </header>

      <div className="border-b border-slate-200 bg-white px-4 py-3">
        <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">
          Pick up to {MAX_SELECTED} configs
        </p>
        <div className="flex flex-wrap gap-2">
          {variants.map((v) => (
            <button
              key={v.id}
              type="button"
              onClick={() => toggle(v.id)}
              className={`rounded-lg border px-3 py-1.5 text-sm capitalize ${
                selected.includes(v.id)
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-slate-300 text-slate-600 hover:bg-slate-50'
              }`}
            >
              {v.mode} · {v.ocr}
              <span className="ml-2 text-xs text-slate-400">{summaryLabel(v)}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="flex min-h-0 flex-1">
        <div className="flex min-w-0 flex-1 flex-col border-r border-slate-200">
          <div className="flex items-center gap-2 border-b border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-500">
            <span className="uppercase tracking-wide">Overlay:</span>
            {shown.map((v) => (
              <button
                key={v.id}
                type="button"
                onClick={() => setFocusId(v.id)}
                className={`rounded-md px-2 py-0.5 capitalize ${
                  focusId === v.id ? 'bg-blue-500 text-white' : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                {v.mode}·{v.ocr}
              </button>
            ))}
          </div>
          {focus && focus.status === 'complete' && !focus.error ? (
            <div className="min-h-0 flex-1">
              <PdfPane
                docId={focus.id}
                chunks={chunksBy[focus.id] ?? []}
                numPages={numPagesBy[focus.id] ?? 1}
                currentPage={currentPage}
                selectedChunkId={selectedChunkId}
                onSelectChunk={(id) => selectChunk(focus.id, id)}
                onPageChange={setCurrentPage}
              />
            </div>
          ) : (
            <div className="flex flex-1 items-center justify-center text-sm text-slate-500">
              {focus ? 'Processing…' : 'Select a config to overlay on the PDF.'}
            </div>
          )}
        </div>

        <div className="flex min-h-0 shrink-0 gap-3 overflow-x-auto p-3">
          {shown.length === 0 ? (
            <p className="p-4 text-slate-500">Select configs above to compare.</p>
          ) : (
            shown.map((v) => (
              <VariantColumn
                key={v.id}
                variant={v}
                chunks={chunksBy[v.id] ?? null}
                selectedChunkId={selectedChunkId}
                focused={focusId === v.id}
                onSelectChunk={(chunkId) => selectChunk(v.id, chunkId)}
              />
            ))
          )}
        </div>
      </div>
    </div>
  )
}

function summaryLabel(v: CompareVariant): string {
  if (v.status !== 'complete') return v.status ?? '—'
  if (v.error) return 'failed'
  return `${v.summary?.num_chunks ?? 0} chunks`
}

function VariantColumn({
  variant,
  chunks,
  selectedChunkId,
  focused,
  onSelectChunk,
}: {
  variant: CompareVariant
  chunks: Chunk[] | null
  selectedChunkId: string | null
  focused: boolean
  onSelectChunk: (chunkId: string) => void
}) {
  const selectedRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    selectedRef.current?.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'smooth' })
  }, [selectedChunkId, chunks])

  return (
    <div
      className={`flex w-96 shrink-0 flex-col rounded-xl border bg-white ${
        focused ? 'border-blue-400 ring-1 ring-blue-200' : 'border-slate-200'
      }`}
    >
      <div className="border-b border-slate-100 px-3 py-2">
        <div className="font-medium capitalize text-slate-800">
          {variant.mode} · {variant.ocr}
        </div>
        <div className="text-xs text-slate-400">{summaryLabel(variant)}</div>
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto p-1">
        {variant.status !== 'complete' && <p className="p-2 text-sm text-slate-500">Processing…</p>}
        {variant.error && <p className="p-2 text-sm text-red-600">{variant.error}</p>}
        {chunks?.map((c) => (
          <div
            key={c.id}
            ref={selectedChunkId === c.id ? selectedRef : null}
            role="button"
            tabIndex={0}
            onClick={() => onSelectChunk(c.id)}
            onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && onSelectChunk(c.id)}
            className={`cursor-pointer border-b px-2 py-1.5 text-sm ${
              selectedChunkId === c.id
                ? 'border-blue-200 bg-blue-50 ring-1 ring-inset ring-blue-300'
                : 'border-slate-50 hover:bg-slate-50'
            }`}
          >
            <div className="mb-0.5 flex items-center gap-2">
              <span className="text-xs text-slate-400">#{c.order}</span>
              <span className="rounded bg-slate-100 px-1 text-xs text-slate-500">{c.kind}</span>
            </div>
            {c.kind === 'table' && c.table ? (
              <div className="overflow-x-auto">
                <table className="border-collapse text-xs">
                  <tbody>
                    {c.table.grid.map((row, i) => (
                      <tr key={i}>
                        {row.map((cell, j) => (
                          <td
                            key={j}
                            className="border border-slate-200 px-1 py-0.5 align-top text-slate-700"
                          >
                            {cell}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : c.kind === 'picture' ? (
              <span className="text-slate-500">[picture]</span>
            ) : (
              <span className="whitespace-pre-wrap break-words text-slate-700">{c.text}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
