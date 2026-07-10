import { describe, expect, it } from 'vitest'
import { makeChunk } from './test/factories'
import type { SearchHit } from './types'
import { deriveItems } from './viewerState'

describe('deriveItems', () => {
  const chunks = [makeChunk({ id: 'a', order: 0 }), makeChunk({ id: 'b', order: 1 })]

  it('returns reading-order chunks with no scores when not searching', () => {
    const items = deriveItems(chunks, null)
    expect(items.map((i) => i.chunk.id)).toEqual(['a', 'b'])
    expect(items[0].score).toBeUndefined()
  })

  it('returns ranked hits with scores in search mode', () => {
    const hits: SearchHit[] = [
      { doc_id: 'd', chunk_id: 'b', score: 0.9, chunk: makeChunk({ id: 'b', order: 1 }) },
    ]
    const items = deriveItems(chunks, hits)
    expect(items.map((i) => i.chunk.id)).toEqual(['b'])
    expect(items[0].score).toBe(0.9)
  })

  it('returns an empty list when search finds nothing', () => {
    expect(deriveItems(chunks, [])).toEqual([])
  })
})
