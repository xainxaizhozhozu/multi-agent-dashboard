import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ComposedChart
} from 'recharts'

const COLORS = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452']

const fmt = (val) => `¥${Number(val).toLocaleString()}`

function buildChartData(raw_data, columns) {
  if (!raw_data || raw_data.length === 0) return []
  const labelKey = columns?.[0] || 'name'
  const valueKey = columns?.[1] || 'value'
  return raw_data.map(row => {
    if (Array.isArray(row)) {
      return { name: row[0], value: Number(row[1]) || 0, extra: row[2] ? Number(row[2]) : undefined }
    }
    return { name: row[labelKey], value: Number(row[valueKey]) || 0 }
  })
}

function PieView({ data, title }) {
  return (
    <div className="mt-4">
      <h4 className="text-sm font-semibold text-gray-700 mb-2">{title}</h4>
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`} labelLine>
            {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
          </Pie>
          <Tooltip formatter={fmt} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}

function LineView({ data, title }) {
  return (
    <div className="mt-4">
      <h4 className="text-sm font-semibold text-gray-700 mb-2">{title}</h4>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" fontSize={12} />
          <YAxis fontSize={12} />
          <Tooltip formatter={fmt} />
          <Legend />
          <Line type="monotone" dataKey="value" name="销售额" stroke="#5470c6" strokeWidth={2} dot={{ r: 4 }} />
          {data[0]?.extra !== undefined && (
            <Line type="monotone" dataKey="extra" name="订单数" stroke="#91cc75" strokeWidth={2} dot={{ r: 4 }} />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

function ComboView({ data, title }) {
  return (
    <div className="mt-4">
      <h4 className="text-sm font-semibold text-gray-700 mb-2">{title}</h4>
      <ResponsiveContainer width="100%" height={280}>
        <ComposedChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" fontSize={12} />
          <YAxis fontSize={12} />
          <Tooltip formatter={fmt} />
          <Legend />
          <Bar dataKey="value" name="金额" fill="#5470c6" radius={[4, 4, 0, 0]} />
          <Line type="monotone" dataKey="extra" name="趋势" stroke="#ee6666" strokeWidth={2} dot={{ r: 4 }} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}

function BarView({ data, title }) {
  return (
    <div className="mt-4">
      <h4 className="text-sm font-semibold text-gray-700 mb-2">{title}</h4>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} layout={data.length > 6 ? 'vertical' : 'horizontal'}>
          <CartesianGrid strokeDasharray="3 3" />
          {data.length > 6 ? (
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
          <Tooltip formatter={fmt} />
          <Legend />
          <Bar dataKey="value" name="金额" fill="#5470c6" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export default function AgentChart({ result }) {
  const { chart_type, raw_data, columns, chart_title } = result
  const data = buildChartData(raw_data, columns)
  if (data.length === 0) return null

  switch (chart_type) {
    case 'pie':   return <PieView data={data} title={chart_title} />
    case 'line':  return <LineView data={data} title={chart_title} />
    case 'combo': return <ComboView data={data} title={chart_title} />
    default:      return <BarView data={data} title={chart_title} />
  }
}
