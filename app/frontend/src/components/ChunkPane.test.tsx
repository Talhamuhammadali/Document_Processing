import { render, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { makeChunk } from '../test/factories'
import ChunkPane from './ChunkPane'

describe('ChunkPane grouping', () => {
  it('folds consecutive same-group chunks into one labeled block', () => {
    const items = [
      { chunk: makeChunk({ id: 'texts-5', text: 'item one', group_id: 'groups-0', group_label: 'list' }) },
      { chunk: makeChunk({ id: 'texts-6', text: 'item two', group_id: 'groups-0', group_label: 'list' }) },
    ]
    render(<ChunkPane items={items} selectedChunkId={null} onSelectChunk={() => {}} />)
    expect(screen.getByText('list')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
    expect(screen.getByText('item one')).toBeInTheDocument()
    expect(screen.getByText('item two')).toBeInTheDocument()
  })

  it('keeps distinct groups in separate blocks', () => {
    const items = [
      { chunk: makeChunk({ id: 'texts-5', text: 'a', group_id: 'groups-0', group_label: 'list' }) },
      { chunk: makeChunk({ id: 'texts-15', text: 'b', group_id: 'groups-1', group_label: 'list' }) },
    ]
    render(<ChunkPane items={items} selectedChunkId={null} onSelectChunk={() => {}} />)
    expect(screen.getAllByText('list')).toHaveLength(2)
    expect(screen.getAllByText('1')).toHaveLength(2)
  })

  it('renders ungrouped chunks as standalone cards', () => {
    const items = [{ chunk: makeChunk({ id: 'texts-4', text: 'a heading', label: 'section_header' }) }]
    render(<ChunkPane items={items} selectedChunkId={null} onSelectChunk={() => {}} />)
    expect(screen.getByText('a heading')).toBeInTheDocument()
    expect(screen.queryByText('list')).not.toBeInTheDocument()
  })

  it('does not group while searching, even for same-group chunks', () => {
    const items = [
      { chunk: makeChunk({ id: 'texts-5', text: 'x', group_id: 'groups-0', group_label: 'list' }), score: 0.9 },
      { chunk: makeChunk({ id: 'texts-6', text: 'y', group_id: 'groups-0', group_label: 'list' }), score: 0.8 },
    ]
    render(<ChunkPane items={items} selectedChunkId={null} onSelectChunk={() => {}} />)
    expect(screen.queryByText('list')).not.toBeInTheDocument()
    expect(screen.getByText('0.90')).toBeInTheDocument()
  })

  it('marks the group block active when a member is selected', () => {
    const items = [
      { chunk: makeChunk({ id: 'texts-5', text: 'one', group_id: 'groups-0', group_label: 'list' }) },
    ]
    render(<ChunkPane items={items} selectedChunkId="texts-5" onSelectChunk={() => {}} />)
    const cell = screen.getByText('one')
    const block = cell.closest('div.rounded-lg') as HTMLElement
    expect(within(block).getByText('one')).toBeInTheDocument()
  })
})
