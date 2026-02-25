import { useState } from 'react'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

export const useApi = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  const request = async (endpoint, method = 'GET', data = null) => {
    setLoading(true)
    setError(null)
    
    try {
      const config = {
        method,
        url: `${API_BASE_URL}${endpoint}`,
        ...(data && { data })
      }
      
      const response = await axios(config)
      setLoading(false)
      return { data: response.data, error: null }
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'An error occurred'
      setError(errorMessage)
      setLoading(false)
      return { data: null, error: errorMessage }
    }
  }
  
  return { request, loading, error }
}
