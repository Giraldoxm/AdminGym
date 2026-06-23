import { ref, computed } from 'vue'

const STORAGE_KEY = 'jain_sesion_marca'

// Module-level shared state — persists across component mounts
const sesion = ref(null)

function _load() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    sesion.value = stored ? JSON.parse(stored) : null
  } catch {
    sesion.value = null
  }
}

function _save() {
  try {
    if (sesion.value) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(sesion.value))
    } else {
      localStorage.removeItem(STORAGE_KEY)
    }
  } catch { /* silencioso */ }
}

_load()

export function useSessionMarca() {
  const tieneSession = computed(() => !!sesion.value)

  function iniciarSesion(ejercicio, tipo, unidad, pesoCorporal, fecha) {
    sesion.value = {
      ejercicio,
      tipo,
      unidad: unidad || 'kg',
      pesoCorporal: pesoCorporal || null,
      series: [],
      fecha: fecha || new Date().toISOString().slice(0, 10),
      notas: '',
      iniciada: new Date().toISOString(),
    }
    _save()
  }

  // serie: { peso (en unidad de sesión), reps, rm_calculado }
  function agregarSerie(peso, reps, rm_calculado) {
    if (!sesion.value) return
    sesion.value = {
      ...sesion.value,
      series: [...sesion.value.series, { peso, reps, rm_calculado }],
    }
    _save()
  }

  function eliminarSerie(index) {
    if (!sesion.value) return
    const series = [...sesion.value.series]
    series.splice(index, 1)
    sesion.value = { ...sesion.value, series }
    _save()
  }

  function actualizarSerie(index, peso, reps, rm_calculado) {
    if (!sesion.value) return
    const series = [...sesion.value.series]
    series[index] = { peso, reps, rm_calculado }
    sesion.value = { ...sesion.value, series }
    _save()
  }

  function actualizarCampo(campo, valor) {
    if (!sesion.value) return
    sesion.value = { ...sesion.value, [campo]: valor }
    _save()
  }

  function cancelarSesion() {
    sesion.value = null
    _save()
  }

  function buildPayload() {
    if (!sesion.value) return null
    return {
      ejercicio: sesion.value.ejercicio,
      fecha: sesion.value.fecha,
      notas: sesion.value.notas || null,
      unidad: sesion.value.unidad,
      series: sesion.value.series.map(s => ({ peso: s.peso, repeticiones: s.reps })),
    }
  }

  return {
    sesion,
    tieneSession,
    iniciarSesion,
    agregarSerie,
    eliminarSerie,
    actualizarSerie,
    actualizarCampo,
    cancelarSesion,
    buildPayload,
  }
}
