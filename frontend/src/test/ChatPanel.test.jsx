import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ChatPanel from '../components/ChatPanel'

// Mock the agentApi
vi.mock('../api', () => ({
  agentApi: {
    chat: vi.fn(),
  },
  dashboardApi: {},
}))

describe('ChatPanel Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders suggestion buttons', () => {
    render(<ChatPanel />)
    expect(screen.getByText('各地区销售额对比')).toBeTruthy()
    expect(screen.getByText('月度销售趋势')).toBeTruthy()
  })

  it('renders the input field with placeholder', () => {
    render(<ChatPanel />)
    const input = screen.getByPlaceholderText(/例如/)
    expect(input).toBeTruthy()
  })

  it('renders the send button', () => {
    render(<ChatPanel />)
    expect(screen.getByText('分析')).toBeTruthy()
  })

  it('shows empty state message when no messages', () => {
    render(<ChatPanel />)
    expect(screen.getByText(/输入问题或点击上方推荐/)).toBeTruthy()
  })

  it('allows typing in the input field', () => {
    render(<ChatPanel />)
    const input = screen.getByPlaceholderText(/例如/)
    fireEvent.change(input, { target: { value: '测试查询' } })
    expect(input.value).toBe('测试查询')
  })

  it('renders the header with title', () => {
    render(<ChatPanel />)
    expect(screen.getByText('AI 数据分析助手')).toBeTruthy()
  })
})
