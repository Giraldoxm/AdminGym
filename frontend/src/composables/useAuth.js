import { computed, ref } from 'vue'

// Ref reactivo para que cambios en fecha de vencimiento (p.ej. tras renovación)
// se reflejen en sidebar y guards sin recargar la página.
const fechaVencimientoRef = ref(localStorage.getItem('fechaVencimiento') || '')

export function setFechaVencimiento(fecha) {
  fechaVencimientoRef.value = fecha || ''
  localStorage.setItem('fechaVencimiento', fecha || '')
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

  const isAdmin = computed(() => rol.value === 'admin')
  const isCoach = computed(() => rol.value === 'coach')
  const isCliente = computed(() => rol.value === 'cliente')
  const isPendiente = computed(() => rol.value === 'pendiente')
  const canManage = computed(() => rol.value === 'admin' || rol.value === 'coach')

  // Solo aplica a clientes. Admin/coach nunca están "vencidos".
  const membresiaVencida = computed(() =>
    isCliente.value && membresiaVencidaFor(fechaVencimientoRef.value)
  )

  return { rol, nombre, isAdmin, isCoach, isCliente, isPendiente, canManage, membresiaVencida }
}
