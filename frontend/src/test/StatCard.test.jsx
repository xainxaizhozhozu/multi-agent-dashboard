import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import StatCard from '../components/StatCard'

describe('StatCard Component', () => {
  it('renders title and value', () => {
    render(<StatCard title="总销售额" value="¥100,000" icon="DollarSign" color="blue" />)
    expect(screen.getByText('总销售额')).toBeTruthy()
    expect(screen.getByText('¥100,000')).toBeTruthy()
  })

  it('renders subtitle when provided', () => {
    render(<StatCard title="本月" value="¥50,000" subtitle="环比 12%" icon="TrendingUp" color="purple" />)
    expect(screen.getByText('环比 12%')).toBeTruthy()
  })

  it('does not render subtitle when not provided', () => {
    const { container } = render(<StatCard title="员工" value="42" icon="Users" color="orange" />)
    expect(container.querySelectorAll('p').length).toBe(2) // title + value only
  })

  it('applies correct color classes', () => {
    const { container } = render(<StatCard title="Test" value="1" icon="DollarSign" color="green" />)
    const iconWrapper = container.querySelector('.bg-green-50')
    expect(iconWrapper).toBeTruthy()
  })
})
