import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Mock recharts - these components need a real DOM with dimensions
vi.mock('recharts', () => {
  const MockComponent = ({ children }) => <div data-testid="mock-chart">{children}</div>;
  return {
    ResponsiveContainer: ({ children }) => <div data-testid="responsive-container">{children}</div>,
    LineChart: MockComponent,
    Line: () => null,
    BarChart: MockComponent,
    Bar: () => null,
    PieChart: MockComponent,
    Pie: ({ children }) => <div>{children}</div>,
    Cell: () => null,
    ComposedChart: MockComponent,
    XAxis: () => null,
    YAxis: () => null,
    CartesianGrid: () => null,
    Tooltip: () => null,
    Legend: () => null,
  };
});

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  TrendingUp: () => <span data-testid="icon-trending-up">TrendingUp</span>,
  DollarSign: () => <span data-testid="icon-dollar-sign">DollarSign</span>,
  ShoppingCart: () => <span data-testid="icon-shopping-cart">ShoppingCart</span>,
  Users: () => <span data-testid="icon-users">Users</span>,
  BarChart3: () => <span data-testid="icon-bar-chart">BarChart3</span>,
  PieChart: () => <span data-testid="icon-pie-chart">PieChart</span>,
  Send: () => <span data-testid="icon-send">Send</span>,
}));

// Mock the api module
vi.mock('../api', () => ({
  dashboardApi: {
    getStats: vi.fn().mockResolvedValue({
      total_revenue: 1000000,
      avg_order_value: 500,
      this_month_revenue: 100000,
      mom_change: 5.2,
      employee_count: 150,
    }),
    getMonthlyTrend: vi.fn().mockResolvedValue([]),
    getByRegion: vi.fn().mockResolvedValue([]),
    getByCategory: vi.fn().mockResolvedValue([]),
  },
  agentApi: {
    chat: vi.fn().mockResolvedValue({
      success: true,
      chart_type: 'bar',
      raw_data: [],
      columns: [],
      explanation: 'Test result',
      elapsed_seconds: 1.5,
    }),
    status: vi.fn().mockResolvedValue({}),
  },
}));

import App from '../App';
import { dashboardApi } from '../api';

describe('App Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<App />);
    expect(screen.getByText('AI 智能数据分析看板')).toBeInTheDocument();
  });

  it('renders all StatCard titles', () => {
    render(<App />);
    expect(screen.getByText('总销售额')).toBeInTheDocument();
    expect(screen.getByText('平均客单价')).toBeInTheDocument();
    expect(screen.getByText('本月销售额')).toBeInTheDocument();
    expect(screen.getByText('员工总数')).toBeInTheDocument();
  });

  it('renders the chat input field', () => {
    render(<App />);
    const input = screen.getByPlaceholderText(/例如：各地区销售额对比/);
    expect(input).toBeInTheDocument();
    expect(input.tagName).toBe('INPUT');
  });

  it('renders the send button', () => {
    render(<App />);
    const sendButton = screen.getByRole('button', { name: /分析/ });
    expect(sendButton).toBeInTheDocument();
    expect(sendButton).not.toBeDisabled();
  });

  it('allows typing in the input field', async () => {
    const user = userEvent.setup();
    render(<App />);
    const input = screen.getByPlaceholderText(/例如：各地区销售额对比/);
    await user.type(input, '测试查询');
    expect(input).toHaveValue('测试查询');
  });

  it('renders suggestion buttons', () => {
    render(<App />);
    expect(screen.getByText('各地区销售额对比')).toBeInTheDocument();
    expect(screen.getByText('客户类型消费占比')).toBeInTheDocument();
    expect(screen.getByText('产品类别 TOP5 排名')).toBeInTheDocument();
  });

  it('loads dashboard data on mount', () => {
    render(<App />);
    expect(dashboardApi.getStats).toHaveBeenCalled();
    expect(dashboardApi.getMonthlyTrend).toHaveBeenCalled();
    expect(dashboardApi.getByRegion).toHaveBeenCalled();
    expect(dashboardApi.getByCategory).toHaveBeenCalled();
  });
});
