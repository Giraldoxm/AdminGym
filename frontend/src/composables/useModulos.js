import { computed, ref } from 'vue'

// Módulos (feature flags) activos del gimnasio del usuario actual. Se cargan en
// el login desde GET /me (campo `modulos_activos`) y se guardan en localStorage
// para que sidebar y guards reaccionen sin recargar la página. Patrón espejo de
// useAuth/fechaVencimientoRef.
//
// IMPORTANTE: ausencia de la clave en localStorage (instalación vieja, login que
// no la guardó) se trata como "todos los módulos activos" para no romper gimnasios
// de un solo tenant que aún no pasaron por el nuevo login. Solo cuando la lista
// existe y NO contiene la clave se oculta la funcionalidad.

function _leer() {
  const raw = localStorage.getItem('modulosActivos')
  if (raw === null) return null
  try {
    const arr = JSON.parse(raw)
    return Array.isArray(arr) ? arr : null
  } catch {
    return null
  }
}

const modulosRef = ref(_leer())

export function setModulos(modulos) {
  if (Array.isArray(modulos)) {
    modulosRef.value = modulos
    localStorage.setItem('modulosActivos', JSON.stringify(modulos))
  } else {
    modulosRef.value = null
    localStorage.removeItem('modulosActivos')
  }
}

export function clearModulos() {
  modulosRef.value = null
  localStorage.removeItem('modulosActivos')
}

export function tieneModuloFor(clave) {
  // Sin lista conocida → permitir (compatibilidad hacia atrás).
  if (modulosRef.value === null) return true
  return modulosRef.value.includes(clave)
}

export function useModulos() {
  const modulos = computed(() => modulosRef.value)
  const tieneModulo = (clave) => {
    if (modulos.value === null) return true
    return modulos.value.includes(clave)
  }
  const tieneWods = computed(() => tieneModulo('wods'))
  const tieneBiometria = computed(() => tieneModulo('biometria'))
  return { modulos, tieneModulo, tieneWods, tieneBiometria }
}
