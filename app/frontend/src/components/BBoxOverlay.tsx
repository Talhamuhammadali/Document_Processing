import { forwardRef } from 'react'
import { kindColor } from '../chunkStyles'
import { overlayPercent } from '../overlay'
import type { Chunk } from '../types'

interface Props {
  chunk: Chunk
  selected: boolean
  onSelect: () => void
}

const BBoxOverlay = forwardRef<HTMLButtonElement, Props>(function BBoxOverlay(
  { chunk, selected, onSelect },
  ref,
) {
  const color = kindColor[chunk.kind]
  const dimmed = chunk.content_layer === 'furniture'

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
        borderStyle: dimmed ? 'dashed' : 'solid',
        borderWidth: selected ? 2 : 1,
        backgroundColor: selected ? `${color}33` : 'transparent',
        opacity: dimmed ? 0.55 : 1,
      }}
      className="absolute cursor-pointer rounded-sm hover:bg-black/5"
    />
  )
})

export default BBoxOverlay
