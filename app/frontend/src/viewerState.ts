import type { Chunk, ChunkListItem, SearchHit } from './types'

export function deriveItems(chunks: Chunk[], hits: SearchHit[] | null): ChunkListItem[] {
  if (hits !== null) return hits.map((h) => ({ chunk: h.chunk, score: h.score }))
  return chunks.map((c) => ({ chunk: c }))
}
