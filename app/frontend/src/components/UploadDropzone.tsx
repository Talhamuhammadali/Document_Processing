import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { uploadDocument } from '../api'
import type { Mode, OcrEngine } from '../types'

interface Props {
  mode: Mode
  ocr: OcrEngine
}

export default function UploadDropzone({ mode, ocr }: Props) {
  const navigate = useNavigate()
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleFile(file: File) {
    setBusy(true)
    setError(null)
    try {
      const result = await uploadDocument(file, mode, ocr)
      navigate(`/doc/${encodeURIComponent(result.document_id)}`)
    } catch {
      setError('Upload failed. Is the backend running?')
    } finally {
      setBusy(false)
    }
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files?.[0]
    if (file) void handleFile(file)
  }

  return (
    <div>
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={`flex w-full flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed px-6 py-10 text-center transition-colors ${
          dragging
            ? 'border-blue-400 bg-blue-50'
            : 'border-slate-300 bg-slate-50 hover:border-slate-400 hover:bg-slate-100'
        }`}
      >
        <span className="text-3xl">⬆</span>
        <span className="font-medium text-slate-700">
          {busy ? 'Uploading…' : 'Drop a PDF here or click to upload'}
        </span>
        <span className="text-sm text-slate-500">Processed with the selected mode and OCR engine</span>
      </button>
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0]
          if (file) void handleFile(file)
          e.target.value = ''
        }}
      />
      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
    </div>
  )
}
