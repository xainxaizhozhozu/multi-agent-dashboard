import { DollarSign, ShoppingCart, TrendingUp, Users } from 'lucide-react'

const ICONS = { DollarSign, ShoppingCart, TrendingUp, Users }

const COLOR_MAP = {
  blue: 'bg-blue-50 text-blue-600',
  green: 'bg-green-50 text-green-600',
  purple: 'bg-purple-50 text-purple-600',
  orange: 'bg-orange-50 text-orange-600',
}

export default function StatCard({ title, value, subtitle, icon, color }) {
  const Icon = typeof icon === 'string' ? ICONS[icon] : icon
  return (
    <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-2xl font-bold text-gray-800 mt-1">{value}</p>
          {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-lg ${COLOR_MAP[color]}`}>
          <Icon size={22} />
        </div>
      </div>
    </div>
  )
}
