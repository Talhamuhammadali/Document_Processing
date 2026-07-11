export type Kind = 'text' | 'table' | 'picture'

export type ContentLayer = 'body' | 'furniture' | 'notes'

export interface BBox {
  l: number
  t: number
  r: number
  b: number
}

export interface Page {
  page_no: number
  width: number
  height: number
}

export interface TableData {
  num_rows: number
  num_cols: number
  grid: string[][]
}

export interface Chunk {
  id: string
  order: number
  kind: Kind
  label: string
  content_layer: ContentLayer
  group_id: string | null
  group_label: string | null
  page_no: number
  bbox: BBox
  bbox_norm: BBox
  text: string | null
  table: TableData | null
  image_ref: string | null
  description: string | null
}

export interface SearchHit {
  doc_id: string
  chunk_id: string
  score: number
  chunk: Chunk
}

export interface DocumentMeta {
  id: string
  filename: string
  num_pages: number
  num_chunks: number
  pages: Page[]
}

export interface UploadResult {
  document_id: string
  filename: string
  num_pages: number
  num_chunks: number
}

export interface ChunkListItem {
  chunk: Chunk
  score?: number
}

export interface AvailableDoc {
  id: string
  filename: string
  processed: boolean
}
