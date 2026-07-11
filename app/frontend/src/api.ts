import type {
  AvailableDoc,
  Chunk,
  CompareResponse,
  DocumentMeta,
  EnqueueResult,
  Mode,
  OcrEngine,
  SearchHit,
  StatusResponse,
} from './types'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
    this.name = 'ApiError'
  }
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init)
  if (!res.ok) {
    const detail = await res.text().catch(() => '')
    throw new ApiError(res.status, detail || res.statusText)
  }
  return res.json() as Promise<T>
}

export function fileUrl(id: string): string {
  return `/documents/${encodeURIComponent(id)}/file`
}

export async function listDocuments(): Promise<string[]> {
  const data = await request<{ documents: string[] }>('/documents')
  return data.documents
}

export async function getDocument(id: string): Promise<DocumentMeta> {
  return request<DocumentMeta>(`/documents/${encodeURIComponent(id)}`)
}

export async function getChunks(id: string): Promise<Chunk[]> {
  const data = await request<{ document_id: string; chunks: Chunk[] }>(
    `/documents/${encodeURIComponent(id)}/chunks`,
  )
  return data.chunks
}

export async function uploadDocument(
  file: File,
  mode: Mode,
  ocr: OcrEngine,
): Promise<EnqueueResult> {
  const body = new FormData()
  body.append('file', file)
  body.append('mode', mode)
  body.append('ocr', ocr)
  return request<EnqueueResult>('/documents/upload', { method: 'POST', body })
}

export async function listAvailable(): Promise<AvailableDoc[]> {
  const data = await request<{ available: AvailableDoc[] }>('/documents/available')
  return data.available
}

export async function openDocument(
  filename: string,
  mode: Mode,
  ocr: OcrEngine,
): Promise<EnqueueResult> {
  return request<EnqueueResult>('/documents/open', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename, mode, ocr }),
  })
}

export async function getStatus(id: string): Promise<StatusResponse> {
  return request<StatusResponse>(`/documents/${encodeURIComponent(id)}/status`)
}

export async function reprocessDocument(
  id: string,
  mode: Mode,
  ocr: OcrEngine,
): Promise<EnqueueResult> {
  return request<EnqueueResult>(`/documents/${encodeURIComponent(id)}/reprocess`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mode, ocr }),
  })
}

export async function startCompare(filename: string): Promise<CompareResponse> {
  return request<CompareResponse>('/documents/compare', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename }),
  })
}

export async function getCompare(stem: string): Promise<CompareResponse> {
  return request<CompareResponse>(`/documents/compare/${encodeURIComponent(stem)}`)
}

export async function search(
  query: string,
  opts: { topK?: number; documentId?: string } = {},
): Promise<SearchHit[]> {
  const data = await request<{ query: string; hits: SearchHit[] }>('/documents/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      top_k: opts.topK ?? 5,
      document_id: opts.documentId ?? null,
    }),
  })
  return data.hits
}
