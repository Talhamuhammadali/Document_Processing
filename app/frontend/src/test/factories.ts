import type { Chunk } from '../types'

export function makeChunk(overrides: Partial<Chunk> = {}): Chunk {
  return {
    id: 'texts-0',
    order: 0,
    kind: 'text',
    label: 'text',
    content_layer: 'body',
    group_id: null,
    group_label: null,
    page_no: 1,
    bbox: { l: 0, t: 0, r: 100, b: 100 },
    bbox_norm: { l: 0, t: 0, r: 1, b: 1 },
    text: 'hello world',
    table: null,
    image_ref: null,
    description: null,
    ...overrides,
  }
}
