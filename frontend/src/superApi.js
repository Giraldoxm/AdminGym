import axios from 'axios'
import { API_BASE } from './api'

// Instancia axios dedicada al panel SuperAdmin. Usa su propio token
// (`superToken`) separado del token de usuario de gym, porque los dos scopes JWT
// son mutuamente excluyentes en el backend (un token de gym no pasa como
// superadmin y viceversa).
const superApi = axios.create({ baseURL: API_BASE })

superApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('superToken')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export default superApi
