import ChunkCard from './ChunkCard'
import { kindColor } from '../chunkStyles'
import type { ChunkListItem } from '../types'

interface Props {
  items: ChunkListItem[]
  selectedChunkId: string | null
  onSelectChunk: (chunkId: string) => void
}

type Row =
  | { kind: 'single'; item: ChunkListItem }
  | { kind: 'group'; groupId: string; label: string; items: ChunkListItem[] }

function toRows(items: ChunkListItem[]): Row[] {
  const rows: Row[] = []
  for (const item of items) {
    const gid = item.chunk.group_id
    const last = rows[rows.length - 1]
    if (gid && last && last.kind === 'group' && last.groupId === gid) {
      last.items.push(item)
    } else if (gid) {
      rows.push({ kind: 'group', groupId: gid, label: item.chunk.group_label ?? 'group', items: [item] })
    } else {
      rows.push({ kind: 'single', item })
    }
  }
  return rows
}

export default function ChunkPane({ items, selectedChunkId, onSelectChunk }: Props) {
  if (items.length === 0) {
    return <div className="p-4 text-sm text-slate-500">No matching chunks.</div>
  }

  const searching = items.some((i) => i.score !== undefined)

  if (searching) {
    return (
      <div className="h-full divide-y divide-slate-100 overflow-y-auto">
        {items.map((item) => (
          <ChunkCard
            key={item.chunk.id}
            item={item}
            selected={item.chunk.id === selectedChunkId}
            onSelect={() => onSelectChunk(item.chunk.id)}
          />
        ))}
      </div>
    )
  }

  const rows = toRows(items)

  return (
    <div className="h-full space-y-2 overflow-y-auto p-2">
      {rows.map((row) =>
        row.kind === 'single' ? (
          <ChunkCard
            key={row.item.chunk.id}
            item={row.item}
            selected={row.item.chunk.id === selectedChunkId}
            onSelect={() => onSelectChunk(row.item.chunk.id)}
          />
        ) : (
          <GroupBlock
            key={row.groupId}
            row={row}
            selectedChunkId={selectedChunkId}
            onSelectChunk={onSelectChunk}
          />
        ),
      )}
    </div>
  )
}

function GroupBlock({
  row,
  selectedChunkId,
  onSelectChunk,
}: {
  row: Extract<Row, { kind: 'group' }>
  selectedChunkId: string | null
  onSelectChunk: (chunkId: string) => void
}) {
  const color = kindColor[row.items[0].chunk.kind]
  const active = row.items.some((i) => i.chunk.id === selectedChunkId)

  return (
    <div
      style={{ borderLeftColor: color }}
      className={`overflow-hidden rounded-lg border border-l-4 bg-white transition-colors ${
        active ? 'border-blue-300 shadow-sm' : 'border-slate-200'
      }`}
    >
      <div className="flex items-center gap-2 border-b border-slate-100 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-500">
        <span className="uppercase tracking-wide">{row.label}</span>
        <span className="rounded-full bg-slate-200 px-1.5 py-0.5 text-slate-600">{row.items.length}</span>
      </div>
      <div className="divide-y divide-slate-50 p-1">
        {row.items.map((item) => (
          <ChunkCard
            key={item.chunk.id}
            item={item}
            compact
            selected={item.chunk.id === selectedChunkId}
            onSelect={() => onSelectChunk(item.chunk.id)}
          />
        ))}
      </div>
    </div>
  )
}
