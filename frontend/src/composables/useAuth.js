import { computed, ref } from 'vue'

// Ref reactivo para que cambios en fecha de vencimiento (p.ej. tras renovación)
// se reflejen en sidebar y guards sin recargar la página.
const fechaVencimientoRef = ref(localStorage.getItem('fechaVencimiento') || '')

export function setFechaVencimiento(fecha) {
  fechaVencimientoRef.value = fecha || ''
  localStorage.setItem('fechaVencimiento', fecha || '')
}

// Nombre del gimnasio del usuario (multi-tenant): se muestra dentro de la app
// (sidebar, home, mensajes), mientras que el /login usa el nombre de la plataforma.
const gymNombreRef = ref(localStorage.getItem('gymNombre') || '')

export function setGymNombre(nombre) {
  gymNombreRef.value = nombre || ''
  localStorage.setItem('gymNombre', nombre || '')
}

export function membresiaVencidaFor(fecha) {
  if (!fecha) return true
  const hoy = new Date()
  hoy.setHours(0, 0, 0, 0)
  const venc = new Date(fecha + 'T00:00:00')
  return venc < hoy
}

export function useAuth() {
  const rol = computed(() => localStorage.getItem('userRol') || 'cliente')
  const nombre = computed(() => localStorage.getItem('userName') || '')
  const gymNombre = computed(() => gymNombreRef.value || 'AdminGym')

  const isAdmin = computed(() => rol.value === 'admin')
  const isCoach = computed(() => rol.value === 'coach')
  const isCliente = computed(() => rol.value === 'cliente')
  const isPendiente = computed(() => rol.value === 'pendiente')
  const canManage = computed(() => rol.value === 'admin' || rol.value === 'coach')

  // Solo aplica a clientes. Admin/coach nunca están "vencidos".
  const membresiaVencida = computed(() =>
    isCliente.value && membresiaVencidaFor(fechaVencimientoRef.value)
  )

  return { rol, nombre, gymNombre, isAdmin, isCoach, isCliente, isPendiente, canManage, membresiaVencida }
}
