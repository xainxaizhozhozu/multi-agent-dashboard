import { useState, useEffect } from 'react'
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { TrendingUp, DollarSign, ShoppingCart, Users, BarChart3, PieChart as PieIcon, Send } from 'lucide-react'
import { dashboardApi, agentApi } from './api'

const COLORS = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452']

// ── 统计卡片组件 ──────────────────────────────────────────
function StatCard({ title, value, subtitle, icon: Icon, color }) {
  const colorMap = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    orange: 'bg-orange-50 text-orange-600',
  }
  return (
    <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-2xl font-bold text-gray-800 mt-1">{value}</p>
          {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-lg ${colorMap[color]}`}>
          <Icon size={22} />
        </div>
      </div>
    </div>
  )
}

// ── AI 回复中的图表渲染 ──────────────────────────────────
function AgentChart({ result }) {
  const { chart_type, raw_data, columns, chart_title } = result

  if (!raw_data || raw_data.length === 0) return null

  const labelKey = columns?.[0] || 'name'
  const valueKey = columns?.[1] || 'value'

  const chartData = raw_data.map(row => {
    if (Array.isArray(row)) {
      return { name: row[0], value: Number(row[1]) || 0, extra: row[2] ? Number(row[2]) : undefined }
    }
    return { name: row[labelKey], value: Number(row[valueKey]) || 0 }
  })

  if (chart_type === 'pie') {
    return (
      <div className="mt-4">
        <h4 className="text-sm font-semibold text-gray-700 mb-2">{chart_title}</h4>
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie
              data={chartData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={100}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
              labelLine={true}
            >
              {chartData.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(val) => `¥${Number(val).toLocaleString()}`} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    )
  }

  if (chart_type === 'line') {
    return (
      <div className="mt-4">
        <h4 className="text-sm font-semibold text-gray-700 mb-2">{chart_title}</h4>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" fontSize={12} />
            <YAxis fontSize={12} />
            <Tooltip formatter={(val) => `¥${Number(val).toLocaleString()}`} />
            <Legend />
            <Line type="monotone" dataKey="value" name="销售额" stroke="#5470c6" strokeWidth={2} dot={{ r: 4 }} />
            {chartData[0]?.extra !== undefined && (
              <Line type="monotone" dataKey="extra" name="订单数" stroke="#91cc75" strokeWidth={2} dot={{ r: 4 }} />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
    )
  }

  // 默认 bar
  return (
    <div className="mt-4">
      <h4 className="text-sm font-semibold text-gray-700 mb-2">{chart_title}</h4>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={chartData} layout={chartData.length > 6 ? "vertical" : "horizontal"}>
          <CartesianGrid strokeDasharray="3 3" />
          {chartData.length > 6 ? (
            <>
              <XAxis type="number" fontSize={12} />
              <YAxis type="category" dataKey="name" fontSize={12} width={80} />
            </>
          ) : (
            <>
              <XAxis dataKey="name" fontSize={12} />
              <YAxis fontSize={12} />
            </>
          )}
          <Tooltip formatter={(val) => `¥${Number(val).toLocaleString()}`} />
          <Legend />
          <Bar dataKey="value" name="金额" fill="#5470c6" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

// ── AI 回复组件 ──────────────────────────────────────────
function AgentResponse({ result }) {
  const [showSql, setShowSql] = useState(false)

  if (!result.success) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">
        {result.response_text || '分析失败，请重试'}
      </div>
    )
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
      <div className="flex items-center gap-2 mb-3">
        <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full font-medium">
          {result.chart_type?.toUpperCase()}
        </span>
        <span className="text-xs text-gray-400">耗时 {result.elapsed_seconds}s</span>
        {result.review_passed && (
          <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">✓ 审查通过</span>
        )}
      </div>

      <p className="text-sm text-gray-600 mb-2">{result.explanation}</p>

      <AgentChart result={result} />

      {/* 数据表格 */}
      {result.raw_data && result.raw_data.length > 0 && (
        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-xs border-collapse">
            <thead>
              <tr className="bg-gray-50">
                {result.columns?.map((col, i) => (
                  <th key={i} className="px-3 py-2 text-left font-medium text-gray-600 border-b">{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {result.raw_data.slice(0, 8).map((row, i) => (
                <tr key={i} className="hover:bg-gray-50">
                  {(Array.isArray(row) ? row : result.columns.map(c => row[c])).map((cell, j) => (
                    <td key={j} className="px-3 py-1.5 border-b border-gray-100 text-gray-700">
                      {typeof cell === 'number' ? cell.toLocaleString() : cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* SQL 展开 */}
      {result.sql && (
        <div className="mt-3">
          <button onClick={() => setShowSql(!showSql)} className="text-xs text-blue-500 hover:underline">
            {showSql ? '隐藏 SQL' : '查看 SQL'}
          </button>
          {showSql && (
            <pre className="mt-2 bg-gray-900 text-green-400 text-xs p-3 rounded-lg overflow-x-auto">{result.sql}</pre>
          )}
        </div>
      )}

      {/* Agent 时间线 */}
      {result.agent_timeline && (
        <div className="mt-3 flex gap-3 text-xs text-gray-400 flex-wrap">
          {Object.entries(result.agent_timeline).map(([agent, status]) => (
            <span key={agent} className="bg-gray-100 px-2 py-1 rounded">{agent}: {status}</span>
          ))}
        </div>
      )}
    </div>
  )
}

// ── 主应用 ──────────────────────────────────────────────
export default function App() {
  const [stats, setStats] = useState(null)
  const [trends, setTrends] = useState([])
  const [regionData, setRegionData] = useState([])
  const [categoryData, setCategoryData] = useState([])
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [statsRes, trendsRes, regionRes, categoryRes] = await Promise.allSettled([
        dashboardApi.getStats(),
        dashboardApi.getMonthlyTrend(),
        dashboardApi.getByRegion(),
        dashboardApi.getByCategory(),
      ])
      if (statsRes.status === 'fulfilled') setStats(statsRes.value)
      if (trendsRes.status === 'fulfilled') setTrends(trendsRes.value || [])
      if (regionRes.status === 'fulfilled') setRegionData(regionRes.value || [])
      if (categoryRes.status === 'fulfilled') setCategoryData(categoryRes.value || [])
    } catch (e) {
      console.error('Dashboard data load failed', e)
    }
  }

  const handleSend = async () => {
    const query = input.trim()
    if (!query || loading) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: query }])
    setLoading(true)
    try {
      const result = await agentApi.chat(query)
      setMessages(prev => [...prev, { role: 'agent', result }])
    } catch (err) {
      setMessages(prev => [...prev, { role: 'agent', result: { success: false, response_text: err.message || '请求失败' } }])
    } finally {
      setLoading(false)
    }
  }

  const suggestions = [
    '各地区销售额对比',
    '客户类型消费占比',
    '产品类别 TOP5 排名',
    '月度销售趋势',
    '各部门平均薪资',
  ]

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
          <StatCard title="总销售额" value={stats ? `¥${Number(stats.total_revenue || 0).toLocaleString()}` : '—'} subtitle="全部累计" icon={DollarSign} color="blue" />
          <StatCard title="平均客单价" value={stats ? `¥${Number(stats.avg_order_value || 0).toLocaleString()}` : '—'} subtitle="每笔订单" icon={ShoppingCart} color="green" />
          <StatCard title="本月销售额" value={stats ? `¥${Number(stats.month_revenue || 0).toLocaleString()}` : '—'} subtitle={stats?.mom_change ? `环比 ${stats.mom_change}` : ''} icon={TrendingUp} color="purple" />
          <StatCard title="员工总数" value={stats ? stats.employee_count || '—' : '—'} subtitle="在职人员" icon={Users} color="orange" />
        </div>

        {/* 多图表区域 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 月度趋势折线图 */}
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">月度销售趋势</h3>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" fontSize={11} />
                <YAxis fontSize={11} />
                <Tooltip formatter={(val) => `¥${Number(val).toLocaleString()}`} />
                <Line type="monotone" dataKey="revenue" name="销售额" stroke="#5470c6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* 地区柱状图 */}
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">各地区销售对比</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={regionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="region" fontSize={11} />
                <YAxis fontSize={11} />
                <Tooltip formatter={(val) => `¥${Number(val).toLocaleString()}`} />
                <Bar dataKey="total_revenue" name="销售额" fill="#91cc75" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* 品类饼图 */}
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">产品品类占比</h3>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={categoryData} dataKey="total_revenue" nameKey="product_category" cx="50%" cy="50%" outerRadius={80} label={({ product_category, percent }) => `${product_category} ${(percent * 100).toFixed(0)}%`}>
                  {categoryData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(val) => `¥${Number(val).toLocaleString()}`} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* 快捷指标 */}
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">数据概览</h3>
            <div className="space-y-3">
              {regionData.length > 0 ? regionData.slice(0, 5).map((item, i) => (
                <div key={i} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{item.region}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-32 h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div className="h-full rounded-full" style={{ width: `${(item.total_amount / Math.max(...regionData.map(r => r.total_amount))) * 100}%`, backgroundColor: COLORS[i % COLORS.length] }} />
                    </div>
                    <span className="text-xs text-gray-500 w-16 text-right">¥{(item.total_amount / 10000).toFixed(1)}万</span>
                  </div>
                </div>
              )) : (
                <p className="text-sm text-gray-400">暂无数据</p>
              )}
            </div>
          </div>
        </div>

        {/* AI 对话区域 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100 flex items-center gap-2">
            <PieIcon size={18} className="text-blue-600" />
            <h3 className="text-sm font-semibold text-gray-700">AI 数据分析助手</h3>
            <span className="text-xs text-gray-400 ml-2">支持自然语言查询，自动生成图表</span>
          </div>

          {/* 推荐问题 */}
          <div className="px-5 py-3 flex flex-wrap gap-2 border-b border-gray-50">
            {suggestions.map((s, i) => (
              <button key={i} onClick={() => { setInput(s) }} className="px-3 py-1.5 bg-gray-100 hover:bg-blue-50 hover:text-blue-600 text-xs text-gray-600 rounded-full transition">
                {s}
              </button>
            ))}
          </div>

          {/* 消息列表 */}
          <div className="px-5 py-4 space-y-4 max-h-[500px] overflow-y-auto">
            {messages.length === 0 && (
              <p className="text-center text-gray-400 text-sm py-8">输入问题或点击上方推荐，AI 将自动分析并生成图表</p>
            )}
            {messages.map((msg, i) => (
              <div key={i}>
                {msg.role === 'user' ? (
                  <div className="flex justify-end">
                    <div className="bg-blue-600 text-white px-4 py-2 rounded-xl rounded-br-sm text-sm max-w-[70%]">{msg.content}</div>
                  </div>
                ) : (
                  <AgentResponse result={msg.result} />
                )}
              </div>
            ))}
            {loading && (
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full" />
                Agent 协作分析中...
              </div>
            )}
          </div>

          {/* 输入框 */}
          <div className="px-5 py-4 border-t border-gray-100">
            <div className="flex gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="例如：各地区销售额对比、客户类型占比、月度趋势..."
                className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
              />
              <button onClick={handleSend} disabled={loading} className="px-5 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2">
                <Send size={16} />
                分析
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
