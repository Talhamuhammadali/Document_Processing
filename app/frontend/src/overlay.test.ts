import { describe, expect, it } from 'vitest'
import { overlayPercent } from './overlay'

describe('overlayPercent', () => {
  it('positions left/top from the top-left corner', () => {
    const style = overlayPercent({ l: 0.25, t: 0.5, r: 0.75, b: 0.9 })
    expect(style.left).toBe('25%')
    expect(style.top).toBe('50%')
  })

  it('sizes width/height from the box extent', () => {
    const style = overlayPercent({ l: 0.1, t: 0.1, r: 0.6, b: 0.4 })
    expect(parseFloat(style.width)).toBeCloseTo(50)
    expect(parseFloat(style.height)).toBeCloseTo(30)
  })

  it('covers the full page for a unit box', () => {
    expect(overlayPercent({ l: 0, t: 0, r: 1, b: 1 })).toEqual({
      left: '0%',
      top: '0%',
      width: '100%',
      height: '100%',
    })
  })
})
