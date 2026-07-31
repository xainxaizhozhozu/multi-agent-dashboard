import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import AgentResponse from '../components/AgentResponse'

describe('AgentResponse Component', () => {
  it('renders error state when success is false', () => {
    render(<AgentResponse result={{ success: false, response_text: '出错了' }} />)
    expect(screen.getByText('出错了')).toBeTruthy()
  })

  it('renders default error text when no response_text', () => {
    render(<AgentResponse result={{ success: false }} />)
    expect(screen.getByText('分析失败，请重试')).toBeTruthy()
  })

  it('renders chart type badge on success', () => {
    render(<AgentResponse result={{ success: true, chart_type: 'bar', elapsed_seconds: 1.2, explanation: '按地区统计', raw_data: [], columns: [] }} />)
    expect(screen.getByText('BAR')).toBeTruthy()
  })

  it('renders elapsed time', () => {
    render(<AgentResponse result={{ success: true, chart_type: 'bar', elapsed_seconds: 2.5, explanation: 'test', raw_data: [], columns: [] }} />)
    expect(screen.getByText(/耗时 2.5s/)).toBeTruthy()
  })

  it('renders review passed badge', () => {
    render(<AgentResponse result={{ success: true, chart_type: 'line', elapsed_seconds: 1, review_passed: true, explanation: 'ok', raw_data: [], columns: [] }} />)
    expect(screen.getByText('✓ 审查通过')).toBeTruthy()
  })

  it('renders explanation text', () => {
    render(<AgentResponse result={{ success: true, chart_type: 'bar', elapsed_seconds: 1, explanation: '按地区聚合销售总额', raw_data: [], columns: [] }} />)
    expect(screen.getByText('按地区聚合销售总额')).toBeTruthy()
  })

  it('renders data table when raw_data is present', () => {
    render(<AgentResponse result={{
      success: true, chart_type: 'bar', elapsed_seconds: 1, explanation: 'test',
      raw_data: [['华东', 12345], ['华南', 9876]],
      columns: ['地区', '金额'],
    }} />)
    expect(screen.getByText('地区')).toBeTruthy()
    expect(screen.getByText('金额')).toBeTruthy()
  })

  it('toggles SQL visibility on button click', () => {
    render(<AgentResponse result={{
      success: true, chart_type: 'bar', elapsed_seconds: 1, explanation: 'test',
      raw_data: [], columns: [], sql: 'SELECT region, SUM(amount) FROM sales',
    }} />)
    expect(screen.queryByText('SELECT region, SUM(amount) FROM sales')).toBeNull()
    fireEvent.click(screen.getByText('查看 SQL'))
    expect(screen.getByText('SELECT region, SUM(amount) FROM sales')).toBeTruthy()
  })

  it('renders agent timeline', () => {
    render(<AgentResponse result={{
      success: true, chart_type: 'bar', elapsed_seconds: 1, explanation: 'test',
      raw_data: [], columns: [],
      agent_timeline: { router: 'parsed', sql: '5 rows' },
    }} />)
    expect(screen.getByText('router: parsed')).toBeTruthy()
    expect(screen.getByText('sql: 5 rows')).toBeTruthy()
  })
})
