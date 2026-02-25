export const StatCard = ({ label, value, icon, trend, color = 'blue' }) => {
  const colors = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    red: 'from-red-500 to-red-600',
    purple: 'from-purple-500 to-purple-600',
    yellow: 'from-yellow-500 to-yellow-600'
  }
  
  return (
    <div className={`bg-gradient-to-br ${colors[color]} rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium opacity-90">{label}</span>
        {icon && <span className="text-2xl">{icon}</span>}
      </div>
      <div className="text-3xl font-bold mb-1">{value}</div>
      {trend && (
        <div className={`text-xs font-medium ${trend > 0 ? 'text-green-200' : 'text-red-200'}`}>
          {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
        </div>
      )}
    </div>
  )
}

export const StatRow = ({ label, value, icon, highlight = false }) => (
  <div className={`flex justify-between items-center py-3 border-b border-gray-100 last:border-b-0 ${highlight ? 'bg-blue-50 -mx-4 px-4 rounded-lg' : ''}`}>
    <span className="text-gray-700 flex items-center gap-2">
      {icon && <span className="text-gray-400">{icon}</span>}
      {label}
    </span>
    <span className={`font-bold ${highlight ? 'text-blue-600 text-lg' : 'text-gray-900'}`}>
      {value}
    </span>
  </div>
)
