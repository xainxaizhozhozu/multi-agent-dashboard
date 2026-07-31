import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts'

const COLORS = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452']
const fmt = (val) => `¥${Number(val).toLocaleString()}`

export default function DashboardCharts({ trends, regionData, categoryData }) {
  const maxAmount = regionData.length > 0
    ? Math.max(...regionData.map(r => r.total_amount))
    : 1

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* 月度趋势折线图 */}
      <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">月度销售趋势</h3>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={trends}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" fontSize={11} />
            <YAxis fontSize={11} />
            <Tooltip formatter={fmt} />
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
            <Tooltip formatter={fmt} />
            <Bar dataKey="total_revenue" name="销售额" fill="#91cc75" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* 品类饼图 */}
      <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">产品品类占比</h3>
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie data={categoryData} dataKey="total_revenue" nameKey="product_category"
              cx="50%" cy="50%" outerRadius={80}
              label={({ product_category, percent }) => `${product_category} ${(percent * 100).toFixed(0)}%`}>
              {categoryData.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={fmt} />
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
                  <div className="h-full rounded-full"
                    style={{ width: `${(item.total_amount / maxAmount) * 100}%`, backgroundColor: COLORS[i % COLORS.length] }} />
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
  )
}
