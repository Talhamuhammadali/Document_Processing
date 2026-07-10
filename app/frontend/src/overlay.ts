import type { BBox } from './types'

export interface OverlayStyle {
  left: string
  top: string
  width: string
  height: string
}

export function overlayPercent(b: BBox): OverlayStyle {
  return {
    left: `${b.l * 100}%`,
    top: `${b.t * 100}%`,
    width: `${(b.r - b.l) * 100}%`,
    height: `${(b.b - b.t) * 100}%`,
  }
}
