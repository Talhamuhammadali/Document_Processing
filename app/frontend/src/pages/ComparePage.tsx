import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getChunks, getCompare } from '../api'
import type { Chunk, CompareVariant } from '../types'

const MAX_SELECTED = 3

export default function ComparePage() {
  const { stem = '' } = useParams<{ stem: string }>()
  const [variants, setVariants] = useState<CompareVariant[] | null>(null)
  const [error, setError] = useState(false)
  const [selected, setSelected] = useState<string[]>([])

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
  }, [stem])

  useEffect(() => {
    if (variants && selected.length === 0) {
      setSelected(variants.slice(0, 2).map((v) => v.id))
    }
  }, [variants, selected.length])

  function toggle(id: string) {
    setSelected((cur) =>
      cur.includes(id)
        ? cur.filter((x) => x !== id)
        : cur.length < MAX_SELECTED
          ? [...cur, id]
          : cur,
    )
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

  return (
    <div className="flex h-full flex-col bg-slate-100">
      <header className="flex items-center gap-4 border-b border-slate-200 bg-white px-4 py-3">
        <Link to="/" className="text-sm text-blue-600 hover:underline">
          ‹ Back
        </Link>
        <span className="truncate font-medium text-slate-800">Compare configs · {stem}</span>
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

      <div className="flex min-h-0 flex-1 gap-3 overflow-x-auto p-3">
        {shown.length === 0 ? (
          <p className="p-4 text-slate-500">Select configs above to compare.</p>
        ) : (
          shown.map((v) => <VariantColumn key={v.id} variant={v} />)
        )}
      </div>
    </div>
  )
}

function summaryLabel(v: CompareVariant): string {
  if (v.status !== 'complete') return v.status ?? '—'
  if (v.error) return 'failed'
  return `${v.summary?.num_chunks ?? 0} chunks`
}

function VariantColumn({ variant }: { variant: CompareVariant }) {
  const [chunks, setChunks] = useState<Chunk[] | null>(null)

  useEffect(() => {
    let cancelled = false
    if (variant.status === 'complete' && !variant.error) {
      getChunks(variant.id)
        .then((c) => !cancelled && setChunks(c))
        .catch(() => {})
    }
    return () => {
      cancelled = true
    }
  }, [variant.id, variant.status, variant.error])

  return (
    <div className="flex w-80 shrink-0 flex-col rounded-xl border border-slate-200 bg-white">
      <div className="border-b border-slate-100 px-3 py-2">
        <div className="font-medium capitalize text-slate-800">
          {variant.mode} · {variant.ocr}
        </div>
        <div className="text-xs text-slate-400">{summaryLabel(variant)}</div>
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto p-1">
        {variant.status !== 'complete' && (
          <p className="p-2 text-sm text-slate-500">Processing…</p>
        )}
        {variant.error && <p className="p-2 text-sm text-red-600">{variant.error}</p>}
        {chunks?.map((c) => (
          <div key={c.id} className="border-b border-slate-50 px-2 py-1.5 text-sm">
            <span className="mr-2 text-xs text-slate-400">#{c.order}</span>
            <span className="mr-2 rounded bg-slate-100 px-1 text-xs text-slate-500">{c.kind}</span>
            <span className="text-slate-700">{snippet(c)}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function snippet(c: Chunk): string {
  if (c.text) return c.text.slice(0, 80)
  if (c.table) return `table ${c.table.num_rows}×${c.table.num_cols}`
  if (c.kind === 'picture') return '[picture]'
  return c.label
}
