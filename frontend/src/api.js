import axios from 'axios'

// Base del backend por entorno. Local (default): backend en 127.0.0.1:8000.
// Producción: VITE_API_URL=https://api.tudominio.com (ver .env.production).
export const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

// Resuelve la URL de un archivo subido (foto de perfil/producto).
// Las fotos en object storage (R2/S3) ya vienen como URL absoluta → se usan
// tal cual. Las locales son rutas relativas "/uploads/..." → se les antepone
// la base del backend.
export function mediaUrl(path) {
  if (!path) return ''
  return /^https?:\/\//i.test(path) ? path : `${API_BASE}${path}`
}

const api = axios.create({
  baseURL: API_BASE,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
