export const Card = ({ children, className = '', gradient = false, hover = false }) => {
  const baseStyles = 'rounded-2xl shadow-lg transition-all duration-300'
  const gradientStyles = gradient ? 'bg-gradient-to-br from-white to-gray-50' : 'bg-white'
  const hoverStyles = hover ? 'hover:shadow-2xl hover:scale-[1.02]' : ''
  
  return (
    <div className={`${baseStyles} ${gradientStyles} ${hoverStyles} ${className}`}>
      {children}
    </div>
  )
}

export const CardHeader = ({ children, className = '' }) => (
  <div className={`p-6 border-b border-gray-100 ${className}`}>
    {children}
  </div>
)

export const CardBody = ({ children, className = '' }) => (
  <div className={`p-6 ${className}`}>
    {children}
  </div>
)

export const CardFooter = ({ children, className = '' }) => (
  <div className={`p-6 border-t border-gray-100 ${className}`}>
    {children}
  </div>
)
