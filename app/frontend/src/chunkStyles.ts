import type { Kind } from './types'

export const kindColor: Record<Kind, string> = {
  text: '#3b82f6',
  table: '#10b981',
  picture: '#f59e0b',
}

export const kindGlyph: Record<Kind, string> = {
  text: '¶',
  table: '▦',
  picture: '🖼',
}
