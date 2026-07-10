import DocumentList from '../components/DocumentList'
import UploadDropzone from '../components/UploadDropzone'

export default function HomePage() {
  return (
    <div className="min-h-full bg-slate-100">
      <div className="mx-auto max-w-5xl px-6 py-10">
        <h1 className="mb-6 text-2xl font-semibold text-slate-800">Document Viewer</h1>
        <UploadDropzone />
        <h2 className="mb-4 mt-10 text-lg font-medium text-slate-700">Your documents</h2>
        <DocumentList />
      </div>
    </div>
  )
}
