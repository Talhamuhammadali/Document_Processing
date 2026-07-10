import { useEffect, useRef, useState } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import workerSrc from 'pdfjs-dist/build/pdf.worker.min.mjs?url'
import { fileUrl } from '../api'
import BBoxOverlay from './BBoxOverlay'
import type { Chunk } from '../types'

pdfjs.GlobalWorkerOptions.workerSrc = workerSrc

interface Props {
  docId: string
  chunks: Chunk[]
  numPages: number
  currentPage: number
  selectedChunkId: string | null
  onSelectChunk: (chunkId: string) => void
  onPageChange: (page: number) => void
}

export default function PdfPane({
  docId,
  chunks,
  numPages,
  currentPage,
  selectedChunkId,
  onSelectChunk,
  onPageChange,
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const selectedRef = useRef<HTMLButtonElement>(null)
  const [width, setWidth] = useState<number>()

  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    const observer = new ResizeObserver((entries) => {
      setWidth(entries[0].contentRect.width - 32)
    })
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    selectedRef.current?.scrollIntoView({ block: 'center', behavior: 'smooth' })
  }, [selectedChunkId, currentPage, width])

  const pageChunks = chunks.filter((c) => c.page_no === currentPage)

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-center gap-3 border-b border-slate-200 bg-white px-4 py-2 text-sm text-slate-600">
        <button
          type="button"
          disabled={currentPage <= 1}
          onClick={() => onPageChange(currentPage - 1)}
          className="rounded px-2 py-1 hover:bg-slate-100 disabled:opacity-40"
        >
          ‹ Prev
        </button>
        <span>
          Page {currentPage} / {numPages}
        </span>
        <button
          type="button"
          disabled={currentPage >= numPages}
          onClick={() => onPageChange(currentPage + 1)}
          className="rounded px-2 py-1 hover:bg-slate-100 disabled:opacity-40"
        >
          Next ›
        </button>
      </div>

      <div ref={containerRef} className="flex-1 overflow-auto p-4">
        <Document
          file={fileUrl(docId)}
          loading={<p className="text-slate-500">Loading PDF…</p>}
          error={<p className="text-red-600">Failed to load PDF.</p>}
        >
          <div className="relative inline-block shadow-md">
            <Page
              pageNumber={currentPage}
              width={width}
              renderTextLayer={false}
              renderAnnotationLayer={false}
            />
            {pageChunks.map((chunk) => (
              <BBoxOverlay
                key={chunk.id}
                chunk={chunk}
                ref={chunk.id === selectedChunkId ? selectedRef : undefined}
                selected={chunk.id === selectedChunkId}
                onSelect={() => onSelectChunk(chunk.id)}
              />
            ))}
          </div>
        </Document>
      </div>
    </div>
  )
}
