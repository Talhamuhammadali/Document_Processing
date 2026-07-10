import { useEffect, useRef } from 'react'
import { kindColor, kindGlyph } from '../chunkStyles'
import type { ChunkListItem } from '../types'

interface Props {
  item: ChunkListItem
  selected: boolean
  onSelect: () => void
}

export default function ChunkCard({ item, selected, onSelect }: Props) {
  const { chunk, score } = item
  const ref = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    if (selected) ref.current?.scrollIntoView({ block: 'nearest' })
  }, [selected])

  const dimmed = chunk.content_layer === 'furniture'

  return (
    <button
      ref={ref}
      type="button"
      onClick={onSelect}
      style={{ borderLeftColor: kindColor[chunk.kind] }}
      className={`w-full border-l-4 px-4 py-3 text-left transition-colors ${
        selected ? 'bg-blue-50' : 'bg-white hover:bg-slate-50'
      } ${dimmed ? 'opacity-60' : ''}`}
    >
      <div className="mb-1.5 flex items-center gap-2 text-xs text-slate-500">
        <span>{kindGlyph[chunk.kind]}</span>
        <span className="font-medium">#{chunk.order}</span>
        <span className="rounded bg-slate-100 px-1.5 py-0.5">{chunk.label}</span>
        {dimmed && <span className="rounded bg-amber-100 px-1.5 py-0.5 text-amber-700">furniture</span>}
        {score !== undefined && (
          <span className="ml-auto rounded bg-emerald-100 px-1.5 py-0.5 text-emerald-700">
            {score.toFixed(2)}
          </span>
        )}
      </div>
      <ChunkBody item={item} />
    </button>
  )
}

function ChunkBody({ item }: { item: ChunkListItem }) {
  const { chunk } = item

  if (chunk.kind === 'table' && chunk.table) {
    return (
      <div className="overflow-x-auto">
        <table className="border-collapse text-xs">
          <tbody>
            {chunk.table.grid.map((row, r) => (
              <tr key={r}>
                {row.map((cell, c) => (
                  <td key={c} className="border border-slate-200 px-2 py-1 text-slate-700">
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        {chunk.description && <p className="mt-2 text-xs italic text-slate-500">{chunk.description}</p>}
      </div>
    )
  }

  if (chunk.kind === 'picture') {
    return (
      <div>
        {chunk.image_ref && (
          <img
            src={chunk.image_ref}
            alt={chunk.description ?? 'figure'}
            className="max-h-40 rounded border border-slate-200"
          />
        )}
        {chunk.description && <p className="mt-2 text-sm text-slate-600">{chunk.description}</p>}
      </div>
    )
  }

  return <p className="whitespace-pre-wrap text-sm text-slate-700">{chunk.text}</p>
}
