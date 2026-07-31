import { useState, useEffect } from 'react'
import { BarChart3 } from 'lucide-react'
import StatCard from './components/StatCard'
import DashboardCharts from './components/DashboardCharts'
import ChatPanel from './components/ChatPanel'
import ErrorBoundary from './ErrorBoundary'
import { dashboardApi } from './api'

export default function App() {
  const [stats, setStats] = useState(null)
  const [trends, setTrends] = useState([])
  const [regionData, setRegionData] = useState([])
  const [categoryData, setCategoryData] = useState([])

  useEffect(() => {
    Promise.allSettled([
      dashboardApi.getStats(),
      dashboardApi.getMonthlyTrend(),
      dashboardApi.getByRegion(),
      dashboardApi.getByCategory(),
    ]).then(([s, t, r, c]) => {
      if (s.status === 'fulfilled') setStats(s.value)
      if (t.status === 'fulfilled') setTrends(t.value || [])
      if (r.status === 'fulfilled') setRegionData(r.value || [])
      if (c.status === 'fulfilled') setCategoryData(c.value || [])
    })
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <BarChart3 className="text-blue-600" size={24} />
            <h1 className="text-lg font-bold text-gray-800">AI 智能数据分析看板</h1>
          </div>
          <span className="px-3 py-1 bg-amber-100 text-amber-700 text-xs rounded-full font-medium">Powered by SenseNova AI</span>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        {/* 统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard title="总销售额" value={stats ? `¥${Number(stats.total_revenue || 0).toLocaleString()}` : '—'}
            subtitle="全部累计" icon="DollarSign" color="blue" />
          <StatCard title="平均客单价" value={stats ? `¥${Number(stats.avg_order_value || 0).toLocaleString()}` : '—'}
            subtitle="每笔订单" icon="ShoppingCart" color="green" />
          <StatCard title="本月销售额" value={stats ? `¥${Number(stats.this_month_revenue || 0).toLocaleString()}` : '—'}
            subtitle={stats?.mom_change ? `环比 ${stats.mom_change}%` : ''} icon="TrendingUp" color="purple" />
          <StatCard title="员工总数" value={stats ? stats.employee_count || '—' : '—'}
            subtitle="在职人员" icon="Users" color="orange" />
        </div>

        {/* 多图表区域 */}
        <ErrorBoundary>
          <DashboardCharts trends={trends} regionData={regionData} categoryData={categoryData} />
        </ErrorBoundary>

        {/* AI 对话区域 */}
        <ChatPanel />
      </main>
    </div>
  )
}
