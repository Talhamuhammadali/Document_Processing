import ChunkCard from './ChunkCard'
import type { ChunkListItem } from '../types'

interface Props {
  items: ChunkListItem[]
  selectedChunkId: string | null
  onSelectChunk: (chunkId: string) => void
}

export default function ChunkPane({ items, selectedChunkId, onSelectChunk }: Props) {
  if (items.length === 0) {
    return <div className="p-4 text-sm text-slate-500">No matching chunks.</div>
  }

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
