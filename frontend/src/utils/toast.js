export const showToast = (message, type = 'error') => {
  const toast = document.createElement('div')
  
  const types = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    warning: 'bg-yellow-500',
    info: 'bg-blue-500'
  }
  
  const icons = {
    success: '✓',
    error: '⚠️',
    warning: '⚡',
    info: 'ℹ️'
  }
  
  toast.className = `fixed top-4 right-4 ${types[type]} text-white px-6 py-4 rounded-xl shadow-2xl z-50 flex items-center gap-3 animate-slideIn`
  toast.innerHTML = `
    <span class="text-xl">${icons[type]}</span>
    <span class="font-medium">${message}</span>
  `
  
  document.body.appendChild(toast)
  
  setTimeout(() => {
    toast.style.opacity = '0'
    toast.style.transform = 'translateX(100%)'
    toast.style.transition = 'all 0.3s ease-out'
    setTimeout(() => toast.remove(), 300)
  }, 3000)
}
