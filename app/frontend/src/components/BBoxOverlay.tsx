import { forwardRef } from 'react'
import { kindColor } from '../chunkStyles'
import { overlayPercent } from '../overlay'
import type { Chunk } from '../types'

export type OverlayState = 'idle' | 'group' | 'selected'

interface Props {
  chunk: Chunk
  state: OverlayState
  onSelect: () => void
}

const BBoxOverlay = forwardRef<HTMLButtonElement, Props>(function BBoxOverlay(
  { chunk, state, onSelect },
  ref,
) {
  const color = kindColor[chunk.kind]
  const dimmed = chunk.content_layer === 'furniture'
  const selected = state === 'selected'
  const grouped = state === 'group'

  return (
    <button
      ref={ref}
      type="button"
      title={`#${chunk.order} · ${chunk.label}`}
      onClick={(e) => {
        e.stopPropagation()
        onSelect()
      }}
      style={{
        ...overlayPercent(chunk.bbox_norm),
        borderColor: color,
        borderStyle: dimmed && !selected ? 'dashed' : 'solid',
        borderWidth: selected ? 2 : grouped ? 1.5 : 1,
        backgroundColor: selected ? `${color}33` : grouped ? `${color}1f` : 'transparent',
        boxShadow: selected ? `0 0 0 3px ${color}40, 0 2px 8px ${color}55` : 'none',
        opacity: dimmed && state === 'idle' ? 0.5 : 1,
        zIndex: selected ? 20 : grouped ? 10 : 1,
      }}
      className="group absolute cursor-pointer rounded-sm transition-all duration-150 hover:bg-black/5"
    >
      {selected && (
        <span
          style={{ backgroundColor: color }}
          className="pointer-events-none absolute -top-5 left-0 whitespace-nowrap rounded px-1.5 py-0.5 text-[10px] font-medium leading-none text-white shadow-sm"
        >
          #{chunk.order} · {chunk.label}
        </span>
      )}
    </button>
  )
})

export default BBoxOverlay
