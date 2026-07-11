import { useState } from 'react'
import DocumentList from '../components/DocumentList'
import ModeOcrSelector from '../components/ModeOcrSelector'
import SampleList from '../components/SampleList'
import UploadDropzone from '../components/UploadDropzone'
import type { Mode, OcrEngine } from '../types'

type Tab = 'samples' | 'processed'

export default function HomePage() {
  const [tab, setTab] = useState<Tab>('samples')
  const [mode, setMode] = useState<Mode>('fast')
  const [ocr, setOcr] = useState<OcrEngine>('none')

  return (
    <div className="min-h-full bg-slate-100">
      <div className="mx-auto max-w-5xl px-6 py-10">
        <h1 className="mb-6 text-2xl font-semibold text-slate-800">Document Viewer</h1>

        <div className="mb-4 rounded-xl border border-slate-200 bg-white p-4">
          <p className="mb-3 text-sm font-medium text-slate-600">Processing options</p>
          <ModeOcrSelector mode={mode} ocr={ocr} onMode={setMode} onOcr={setOcr} />
        </div>

        <UploadDropzone mode={mode} ocr={ocr} />

        <div className="mb-4 mt-10 flex gap-1 border-b border-slate-200">
          <TabButton active={tab === 'samples'} onClick={() => setTab('samples')}>
            Samples
          </TabButton>
          <TabButton active={tab === 'processed'} onClick={() => setTab('processed')}>
            Processed
          </TabButton>
        </div>

        {tab === 'samples' ? <SampleList mode={mode} ocr={ocr} /> : <DocumentList />}
      </div>
    </div>
  )
}

function TabButton({
  active,
  onClick,
  children,
}: {
  active: boolean
  onClick: () => void
  children: React.ReactNode
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`-mb-px border-b-2 px-4 py-2 text-sm font-medium transition-colors ${
        active
          ? 'border-blue-500 text-blue-600'
          : 'border-transparent text-slate-500 hover:text-slate-700'
      }`}
    >
      {children}
    </button>
  )
}
