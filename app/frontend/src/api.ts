import type { AvailableDoc, Chunk, DocumentMeta, SearchHit, UploadResult } from './types'

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

export async function uploadDocument(file: File): Promise<UploadResult> {
  const body = new FormData()
  body.append('file', file)
  return request<UploadResult>('/documents/upload', { method: 'POST', body })
}

export async function listAvailable(): Promise<AvailableDoc[]> {
  const data = await request<{ available: AvailableDoc[] }>('/documents/available')
  return data.available
}

export async function openDocument(filename: string): Promise<UploadResult> {
  return request<UploadResult>('/documents/open', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename }),
  })
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
