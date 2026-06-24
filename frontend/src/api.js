import axios from 'axios'

// Base del backend por entorno. Local (default): backend en 127.0.0.1:8000.
// Producción: VITE_API_URL=https://api.tudominio.com (ver .env.production).
// Tolerante: si el valor viene sin esquema (ej. "foo.up.railway.app") se le
// antepone https:// para que axios no lo tome como ruta relativa.
const _rawBase = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').trim().replace(/\/$/, '')
export const API_BASE = /^https?:\/\//i.test(_rawBase) ? _rawBase : `https://${_rawBase}`

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

// Sesión inválida (token expirado o gimnasio desactivado por el SuperAdmin) → el
// backend responde 401 en get_current_user. Cerramos sesión y volvemos al login.
// OJO: solo 401. Los 403 (módulo no contratado vía require_modulo) NO deben
// cerrar la sesión — el usuario sigue logueado, solo no tiene ese módulo.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const url = error.config?.url || ''
    const enLogin = url.includes('/login')
    if (status === 401 && localStorage.getItem('token') && !enLogin) {
      localStorage.removeItem('token')
      localStorage.removeItem('userRol')
      localStorage.removeItem('userName')
      localStorage.removeItem('fechaVencimiento')
      localStorage.removeItem('tieneWodsPersonalizados')
      localStorage.removeItem('userGenero')
      localStorage.removeItem('modulosActivos')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
