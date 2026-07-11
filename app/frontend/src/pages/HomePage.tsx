import { useState } from 'react'
import DocumentList from '../components/DocumentList'
import SampleList from '../components/SampleList'
import UploadDropzone from '../components/UploadDropzone'

type Tab = 'samples' | 'processed'

export default function HomePage() {
  const [tab, setTab] = useState<Tab>('samples')

  return (
    <div className="min-h-full bg-slate-100">
      <div className="mx-auto max-w-5xl px-6 py-10">
        <h1 className="mb-6 text-2xl font-semibold text-slate-800">Document Viewer</h1>
        <UploadDropzone />

        <div className="mb-4 mt-10 flex gap-1 border-b border-slate-200">
          <TabButton active={tab === 'samples'} onClick={() => setTab('samples')}>
            Samples
          </TabButton>
          <TabButton active={tab === 'processed'} onClick={() => setTab('processed')}>
            Processed
          </TabButton>
        </div>

        {tab === 'samples' ? <SampleList /> : <DocumentList />}
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
