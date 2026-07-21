import { useState, useEffect } from 'react';
import { BarChart3, Send, Loader2, Bot, Database, TrendingUp, AlertCircle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { dashboardApi, agentApi } from './api';

// ── 统计卡片组件 ──────────────────────────────────
function StatCard({ title, value, subtitle, icon: Icon, color }) {
  const colorMap = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-emerald-50 text-emerald-600',
    purple: 'bg-purple-50 text-purple-600',
    orange: 'bg-orange-50 text-orange-600',
  };

  return (
    <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-medium text-gray-500">{title}</span>
        <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${colorMap[color]}`}>
          <Icon size={18} />
        </div>
      </div>
      <div className="text-2xl font-bold text-gray-900">{value}</div>
      {subtitle && <div className="text-xs text-gray-400 mt-1">{subtitle}</div>}
    </div>
  );
}

// ── Agent 对话响应展示组件 ────────────────────────
function AgentResponse({ result }) {
  // ReCharts 图表渲染
  function renderChart(config) {
    if (!config || !config.series || !config.series[0]) return null;

    const series = config.series[0];
    const chartType = series.type;

    // 饼图数据
    if (chartType === 'pie' && series.data) {
      const pieData = series.data.map((item, i) => ({
        name: item.name,
        value: item.value,
        color: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'][i % 5],
      }));
      return (
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={[]}>
            {/* Placeholder for PieChart re-render */}
          </LineChart>
        </ResponsiveContainer>
      );
    }

    // 折线图和柱状图需要 x 轴数据
    // 这里需要从原始数据结构推断...
    // 简化处理：使用索引作为 x 轴
    const chartData = (config._raw_data || []).map((row, i) => ({
      index: i + 1,
      value: Array.isArray(row) ? row[1] ?? row[0] : 0,
      category: Array.isArray(row) ? row[0] : '',
    }));

    if (chartType === 'line') {
      return (
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="index" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#4F46E5"
              strokeWidth={2}
              dot={{ fill: '#4F46E5' }}
              name={config.title?.text || '数值'}
            />
          </LineChart>
        </ResponsiveContainer>
      );
    }

    if (chartType === 'bar') {
      return (
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="index" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip formatter={(value) => `¥${Number(value).toLocaleString()}`} />
            <Bar dataKey="value" fill="#4F46E5" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      );
    }

    return <div className="text-gray-400 text-center py-12">图表类型暂不支持</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <div className="w-6 h-6 rounded-full bg-indigo-100 flex items-center justify-center">
          <Bot size={14} className="text-indigo-600" />
        </div>
        <span className="text-sm font-medium text-indigo-700">AI Agent 分析结果</span>
      </div>
      
      <h4 className="text-lg font-semibold text-gray-900">{result.chart_title}</h4>
      
      {result.explanation && (
        <p className="text-sm text-gray-500 bg-gray-50 rounded-lg p-3">{result.explanation}</p>
      )}

      <div className="rounded-xl border border-gray-200 p-4 bg-white">
        {renderChart({ ...result.chart_config, _raw_data: result.raw_data })}
      </div>

      {result.sql && (
        <details className="mt-2">
          <summary className="text-xs text-gray-400 cursor-pointer hover:text-gray-600">
            查看 SQL 查询语句
          </summary>
          <pre className="text-xs text-gray-600 bg-gray-50 rounded-lg p-3 mt-2 overflow-x-auto font-mono">
            {result.sql}
          </pre>
        </details>
      )}

      <div className="flex items-center gap-3 text-xs text-gray-400">
        <span>处理耗时: {result.elapsed_seconds}s</span>
        <span>•</span>
        <span>{result.agent_timeline?.sql || ''}</span>
      </div>
    </div>
  );
}

// ── 主应用组件 ──────────────────────────────────────
export default function App() {
  const [stats, setStats] = useState(null);
  const [trends, setTrends] = useState([]);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => Math.random().toString(36).slice(2, 10));

  // 加载初始看板数据
  useEffect(() => {
    dashboardApi.getStats().then(setStats).catch(console.error);
    dashboardApi.getMonthlyTrend().then(setTrends).catch(console.error);
  }, []);

  // 发送用户问题给 Agent
  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const result = await agentApi.chat(input, sessionId);
      setMessages(prev => [...prev, { role: 'agent', result }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'error',
        content: error?.detail || '请求失败，请检查后端服务是否运行'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* ── 顶部导航栏 ─────────────────────────────── */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <BarChart3 size={22} className="text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900">AI 智能数据分析看板</h1>
              <p className="text-xs text-gray-400">Multi-Agent Collaboration Dashboard</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <Database size={14} />
            <span>Mock Mode</span>
            <span className="w-2 h-2 rounded-full bg-green-400 inline-block"></span>
          </div>
        </div>
      </header>

      {/* ── 主内容区域 ─────────────────────────────── */}
      <main className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        
        {/* 统计卡片行 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard
            title="总销售额"
            value={stats ? `¥${(stats.total_revenue / 10000).toFixed(1)}万` : '---'}
            subtitle={`${stats?.total_orders || 0} 笔订单`}
            icon={TrendingUp}
            color="blue"
          />
          <StatCard
            title="平均客单价"
            value={stats ? `¥${Math.round(stats.avg_order_value).toLocaleString()}` : '---'}
            subtitle={stats ? `环比 ${stats.mom_change > 0 ? '+' : ''}${stats.mom_change}%` : ''}
            icon={BarChart3}
            color="green"
          />
          <StatCard
            title="本月销售额"
            value={stats ? `¥${(stats.this_month_revenue / 10000).toFixed(1)}万` : '---'}
            subtitle={stats ? `环比 ${stats.mom_change > 0 ? '+' : ''}${stats.mom_change}%` : ''}
            icon={TrendingUp}
            color="purple"
          />
          <StatCard
            title="在职员工"
            value={stats?.employee_count || '---'}
            subtitle="活跃员工数"
            icon={AlertCircle}
            color="orange"
          />
        </div>

        {/* 月度趋势图 */}
        {trends.length > 0 && (
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">📈 近6个月销售趋势</h3>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip formatter={(val) => `¥${Number(val).toLocaleString()}`} />
                <Line type="monotone" dataKey="revenue" stroke="#4F46E5" strokeWidth={2} dot={{ fill: '#4F46E5' }} name="销售额" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Agent 对话区域 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100 flex items-center gap-2">
            <Bot size={18} className="text-indigo-500" />
            <h3 className="font-semibold text-gray-800">AI 数据分析助手 — 用自然语言提问</h3>
          </div>

          {/* 消息列表 */}
          <div className="p-5 max-h-[500px] overflow-y-auto space-y-4">
            {messages.length === 0 && (
              <div className="text-center py-8 text-gray-400 space-y-4">
                <Bot size={48} className="mx-auto opacity-30" />
                <p className="text-sm">试试问这些问题：</p>
                <div className="space-y-2 text-sm">
                  <button onClick={() => setInput("华东区上个月的销售额是多少？")}
                    className="block w-full text-left px-4 py-2 rounded-lg bg-gray-50 hover:bg-indigo-50 hover:text-indigo-600 transition-colors text-gray-600">
                    "华东区上个月的销售额是多少？"
                  </button>
                  <button onClick={() => setInput("各产品类别的销售占比情况")}
                    className="block w-full text-left px-4 py-2 rounded-lg bg-gray-50 hover:bg-indigo-50 hover:text-indigo-600 transition-colors text-gray-600">
                    "各产品类别的销售占比情况"
                  </button>
                  <button onClick={() => setInput("最近三个月的收入趋势怎么样")}
                    className="block w-full text-left px-4 py-2 rounded-lg bg-gray-50 hover:bg-indigo-50 hover:text-indigo-600 transition-colors text-gray-600">
                    "最近三个月的收入趋势怎么样"
                  </button>
                </div>
              </div>
            )}

            {messages.map((msg, idx) => (
              msg.role === 'agent' ? (
                <AgentResponse key={idx} result={msg.result} />
              ) : msg.role === 'error' ? (
                <div key={idx} className="flex items-start gap-3 bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
                  <AlertCircle size={18} className="shrink-0 mt-0.5" />
                  {msg.content}
                </div>
              ) : (
                <div key={idx} className="flex justify-end">
                  <div className="max-w-[70%] bg-indigo-600 text-white rounded-2xl rounded-tr-md px-4 py-3 text-sm">
                    {msg.content}
                  </div>
                </div>
              )
            ))}
          </div>

          {/* 输入框 */}
          <div className="px-5 py-4 border-t border-gray-100 bg-gray-50/50">
            <div className="flex gap-3">
              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSend()}
                placeholder="输入您的问题，例如：'帮我看看华南区的销售趋势'..."
                className="flex-1 px-4 py-2.5 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white text-sm"
                disabled={loading}
              />
              <button
                onClick={handleSend}
                disabled={loading || !input.trim()}
                className="px-5 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 text-sm font-medium transition-colors"
              >
                {loading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                发送
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
