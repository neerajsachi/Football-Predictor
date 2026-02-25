import { useState } from 'react'

export const Input = ({ 
  label, 
  value, 
  onChange, 
  placeholder = '', 
  suggestions = [], 
  onSelect,
  icon,
  error,
  className = ''
}) => {
  const [showSuggestions, setShowSuggestions] = useState(false)
  
  return (
    <div className={`relative ${className}`}>
      {label && (
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          {label}
        </label>
      )}
      <div className="relative">
        {icon && (
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
            {icon}
          </div>
        )}
        <input
          type="text"
          value={value}
          onChange={(e) => {
            onChange(e.target.value)
            setShowSuggestions(true)
          }}
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          placeholder={placeholder}
          className={`w-full ${icon ? 'pl-12' : 'pl-6'} pr-6 py-4 text-lg border-2 rounded-xl 
            focus:outline-none focus:ring-2 transition-all duration-200
            ${error ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-gray-300 focus:border-blue-500 focus:ring-blue-200'}
          `}
        />
      </div>
      
      {error && (
        <p className="mt-2 text-sm text-red-600 flex items-center gap-1">
          <span>⚠️</span> {error}
        </p>
      )}
      
      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute z-50 w-full mt-2 bg-white border-2 border-gray-200 rounded-xl shadow-2xl max-h-64 overflow-y-auto">
          {suggestions.map((item, idx) => (
            <div
              key={idx}
              onClick={() => {
                onSelect(item)
                setShowSuggestions(false)
              }}
              className="px-4 py-3 hover:bg-blue-50 cursor-pointer transition-colors duration-150 
                border-b border-gray-100 last:border-b-0 flex items-center gap-3"
            >
              <span className="text-blue-600">⚽</span>
              <span className="text-gray-800">{item}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
