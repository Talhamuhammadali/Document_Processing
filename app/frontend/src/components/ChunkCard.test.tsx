import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { makeChunk } from '../test/factories'
import ChunkCard from './ChunkCard'

describe('ChunkCard', () => {
  it('renders a text chunk body', () => {
    render(
      <ChunkCard item={{ chunk: makeChunk({ text: 'power rating' }) }} selected={false} onSelect={() => {}} />,
    )
    expect(screen.getByText('power rating')).toBeInTheDocument()
  })

  it('renders a table chunk as a grid of cells', () => {
    const chunk = makeChunk({
      kind: 'table',
      label: 'table',
      text: null,
      table: { num_rows: 1, num_cols: 2, grid: [['Model', '3508B']] },
    })
    render(<ChunkCard item={{ chunk }} selected={false} onSelect={() => {}} />)
    expect(screen.getByText('Model')).toBeInTheDocument()
    expect(screen.getByText('3508B')).toBeInTheDocument()
  })

  it('renders a picture chunk image and description', () => {
    const chunk = makeChunk({
      kind: 'picture',
      label: 'picture',
      text: null,
      image_ref: '/documents/d/chunks/pictures-0/image',
      description: 'a wiring diagram',
    })
    render(<ChunkCard item={{ chunk }} selected={false} onSelect={() => {}} />)
    const img = screen.getByRole('img')
    expect(img).toHaveAttribute('src', '/documents/d/chunks/pictures-0/image')
    expect(screen.getByText('a wiring diagram')).toBeInTheDocument()
  })

  it('shows a score badge in search mode', () => {
    render(<ChunkCard item={{ chunk: makeChunk(), score: 0.87 }} selected={false} onSelect={() => {}} />)
    expect(screen.getByText('0.87')).toBeInTheDocument()
  })

  it('calls onSelect when clicked', async () => {
    const onSelect = vi.fn()
    render(<ChunkCard item={{ chunk: makeChunk() }} selected={false} onSelect={onSelect} />)
    await userEvent.click(screen.getByRole('button'))
    expect(onSelect).toHaveBeenCalledOnce()
  })
})
