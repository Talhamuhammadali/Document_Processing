import type { Mode, OcrEngine } from '../types'

interface Props {
  mode: Mode
  ocr: OcrEngine
  onMode: (mode: Mode) => void
  onOcr: (ocr: OcrEngine) => void
  disabled?: boolean
}

const MODES: Mode[] = ['fast', 'accurate']
const OCRS: OcrEngine[] = ['none', 'tesseract', 'rapidocr']

export default function ModeOcrSelector({ mode, ocr, onMode, onOcr, disabled }: Props) {
  return (
    <div className="flex flex-wrap items-center gap-4">
      <Segmented label="Mode" value={mode} options={MODES} onChange={onMode} disabled={disabled} />
      <Segmented label="OCR" value={ocr} options={OCRS} onChange={onOcr} disabled={disabled} />
    </div>
  )
}

function Segmented<T extends string>({
  label,
  value,
  options,
  onChange,
  disabled,
}: {
  label: string
  value: T
  options: T[]
  onChange: (value: T) => void
  disabled?: boolean
}) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</span>
      <div className="inline-flex rounded-lg border border-slate-300 bg-white p-0.5">
        {options.map((opt) => (
          <button
            key={opt}
            type="button"
            disabled={disabled}
            onClick={() => onChange(opt)}
            className={`rounded-md px-2.5 py-1 text-sm capitalize transition-colors disabled:opacity-50 ${
              value === opt ? 'bg-blue-500 text-white' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            {opt}
          </button>
        ))}
      </div>
    </div>
  )
}
