<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-3xl font-black text-gray-800 tracking-tight">WOD</h2>
        <p class="text-gray-500 mt-1">Workout of the Day</p>
      </div>
      <button
        v-if="puedeEditar"
        @click="router.push('/wods/nuevo')"
        class="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white font-bold py-2.5 px-5 rounded-lg shadow transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Nuevo WOD
      </button>
    </div>

    <!-- WODs Activos -->
    <div class="mb-10">
      <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-widest mb-3">WODs Activos</h3>

      <div v-if="wodsActivos.length > 0" class="space-y-4">
        <div
          v-for="wod in wodsActivos"
          :key="wod.id"
          class="rounded-2xl p-6 text-white shadow-lg bg-gray-900"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-1">
                <span class="text-xs font-bold uppercase tracking-widest bg-red-600 text-white px-2 py-0.5 rounded-md">
                  WOD Activo
                </span>
                <span v-if="wod.tipo" class="text-xs font-bold bg-white/15 text-white px-2 py-0.5 rounded-md">
                  {{ wod.tipo }}
                </span>
              </div>
              <h3 class="text-2xl font-black mt-2 mb-1">{{ wod.titulo }}</h3>
              <p v-if="wod.descripcion" class="whitespace-pre-line leading-relaxed text-gray-300 text-sm mb-2">
                {{ wod.descripcion }}
              </p>
              <button
                v-if="wod.ejercicios && wod.ejercicios.length"
                @click.stop="toggleExpandido(wod.id)"
                class="mt-2 flex items-center gap-1.5 text-xs font-semibold text-gray-400 hover:text-white transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 transition-transform duration-200" :class="expandidos[wod.id] ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7" />
                </svg>
                {{ expandidos[wod.id] ? 'Ocultar ejercicios' : `Ver ${wod.ejercicios.length} ejercicio${wod.ejercicios.length !== 1 ? 's' : ''}` }}
              </button>
              <div v-show="expandidos[wod.id]" class="mt-3">
                <WodEjerciciosLista :ejercicios="wod.ejercicios" dark />
              </div>
            </div>
            <div v-if="puedeEditar" class="flex gap-2 ml-4 flex-shrink-0">
              <button
                @click="toggleWod(wod)"
                title="Mover al historial"
                class="p-2 rounded-lg bg-white/10 hover:bg-yellow-500/40 transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
              </button>
              <button @click="router.push({ name: 'WodEditar', params: { id: wod.id }, state: { wod } })" class="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
              </button>
              <button @click="eliminarWod(wod)" class="p-2 rounded-lg bg-white/10 hover:bg-red-500/60 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="!cargando" class="bg-gray-50 border-2 border-dashed border-gray-200 rounded-2xl p-10 text-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-300 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        <p class="text-gray-400 font-medium">No hay WODs activos</p>
        <button v-if="puedeEditar" @click="router.push('/wods/nuevo')" class="mt-4 text-red-600 font-semibold hover:underline text-sm">
          + Crear nuevo WOD
        </button>
      </div>
    </div>

    <!-- Historial de WODs (solo staff) -->
    <div v-if="puedeEditar">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-widest">Historial de WODs</h3>
      </div>

      <!-- Buscador -->
      <div class="relative mb-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M17 11A6 6 0 115 11a6 6 0 0112 0z" />
        </svg>
        <input
          v-model="busquedaHistorial"
          type="text"
          placeholder="Buscar en el historial..."
          class="w-full pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-red-500/30 focus:border-red-400"
        />
      </div>

      <!-- Filtro por tipo -->
      <div class="flex flex-wrap gap-1.5 mb-4">
        <button
          v-for="t in ['', 'For Time', 'AMRAP', 'EMOM', 'Por Rondas', 'Fuerza', 'Otro']"
          :key="t"
          @click="tipoFiltroHistorial = t"
          class="text-xs font-semibold px-2.5 py-1 rounded-full border transition-colors"
          :class="tipoFiltroHistorial === t
            ? 'bg-gray-800 text-white border-gray-800'
            : 'bg-white text-gray-400 border-gray-200 hover:border-gray-400'"
        >
          {{ t || 'Todos' }}
        </button>
      </div>

      <div v-if="historialFiltrado.length > 0" class="space-y-2">
        <div
          v-for="wod in historialFiltrado"
          :key="wod.id"
          class="bg-white rounded-xl border border-gray-200 p-4 flex items-start gap-4 hover:shadow-sm transition-shadow opacity-60"
        >
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <p class="font-bold text-gray-800 truncate">{{ wod.titulo }}</p>
              <span v-if="wod.tipo" class="text-xs font-bold bg-gray-200 text-gray-600 px-2 py-0.5 rounded-md flex-shrink-0">{{ wod.tipo }}</span>
            </div>
            <p class="text-xs text-gray-400 mt-0.5">Última fecha: {{ formatFecha(wod.fecha) }}</p>
            <p v-if="wod.descripcion" class="text-sm text-gray-500 line-clamp-2 mt-1">{{ wod.descripcion }}</p>
            <button
              v-if="wod.ejercicios && wod.ejercicios.length"
              @click.stop="toggleExpandido(wod.id)"
              class="mt-1.5 flex items-center gap-1 text-xs font-semibold text-gray-400 hover:text-red-600 transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 transition-transform duration-200" :class="expandidos[wod.id] ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7" />
              </svg>
              {{ expandidos[wod.id] ? 'Ocultar' : `${wod.ejercicios.length} ejercicio${wod.ejercicios.length !== 1 ? 's' : ''}` }}
            </button>
            <div v-show="expandidos[wod.id]" class="mt-2">
              <WodEjerciciosLista :ejercicios="wod.ejercicios" class="mt-1" />
            </div>
          </div>
          <div class="flex gap-1 flex-shrink-0">
            <button
              @click="toggleWod(wod)"
              title="Restaurar a activos"
              class="p-1.5 rounded-lg text-gray-400 hover:bg-green-50 hover:text-green-600 transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </button>
            <button @click="router.push({ name: 'WodEditar', params: { id: wod.id }, state: { wod } })" class="p-1.5 rounded-lg text-gray-400 hover:bg-gray-100 hover:text-red-600 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
            </button>
            <button @click="eliminarWod(wod)" class="p-1.5 rounded-lg text-gray-400 hover:bg-red-50 hover:text-red-600 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div v-else-if="!cargando && !cargandoHistorial" class="bg-gray-50 rounded-xl border border-gray-200 p-6 text-center">
        <p class="text-gray-400 text-sm">
          {{ (busquedaHistorial || tipoFiltroHistorial) ? 'Sin resultados para ese filtro' : 'El historial está vacío' }}
        </p>
      </div>

      <!-- Cargar más -->
      <div v-if="hayMasHistorial && !busquedaHistorial && !tipoFiltroHistorial" class="mt-5 text-center">
        <button
          @click="cargarMasHistorial"
          :disabled="cargandoHistorial"
          class="text-sm font-semibold text-gray-500 hover:text-red-600 transition-colors disabled:opacity-40"
        >
          {{ cargandoHistorial ? 'Cargando...' : 'Cargar más' }}
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import WodEjerciciosLista from '../components/WodEjerciciosLista.vue'

const router = useRouter()

const wodsActivos       = ref([])
const wodsHistorial     = ref([])
const cargando          = ref(true)
const cargandoHistorial = ref(false)
const hayMasHistorial   = ref(false)
const historialSkip     = ref(0)
const HISTORIAL_LIMIT   = 30
const expandidos        = ref({})

function toggleExpandido(id) {
  expandidos.value[id] = !expandidos.value[id]
}

const userRol     = computed(() => localStorage.getItem('userRol') || 'cliente')
const puedeEditar = computed(() => ['admin', 'coach'].includes(userRol.value))

const busquedaHistorial  = ref('')
const tipoFiltroHistorial = ref('')

const historialFiltrado = computed(() => {
  let result = wodsHistorial.value
  const q = busquedaHistorial.value.trim().toLowerCase()
  if (q) result = result.filter(w => w.titulo.toLowerCase().includes(q))
  if (tipoFiltroHistorial.value) result = result.filter(w => w.tipo === tipoFiltroHistorial.value)
  return result
})

function formatFecha(fecha) {
  return new Date(fecha + 'T12:00:00').toLocaleDateString('es-CO', { day: 'numeric', month: 'long', year: 'numeric' })
}

async function cargarActivos() {
  const { data } = await api.get('/wods/', { params: { activo: true, limit: 50 } })
  wodsActivos.value = data
}

async function _fetchHistorial(skip) {
  const { data } = await api.get('/wods/', { params: { activo: false, limit: HISTORIAL_LIMIT, skip } })
  return data
}

async function cargarHistorial() {
  historialSkip.value = 0
  wodsHistorial.value = []
  cargandoHistorial.value = true
  try {
    const data = await _fetchHistorial(0)
    wodsHistorial.value = data
    hayMasHistorial.value = data.length === HISTORIAL_LIMIT
  } finally {
    cargandoHistorial.value = false
  }
}

async function cargarMasHistorial() {
  historialSkip.value += HISTORIAL_LIMIT
  cargandoHistorial.value = true
  try {
    const data = await _fetchHistorial(historialSkip.value)
    wodsHistorial.value.push(...data)
    hayMasHistorial.value = data.length === HISTORIAL_LIMIT
  } finally {
    cargandoHistorial.value = false
  }
}

async function cargar() {
  cargando.value = true
  try {
    const promises = [cargarActivos()]
    if (puedeEditar.value) promises.push(cargarHistorial())
    await Promise.all(promises)
  } finally {
    cargando.value = false
  }
}

async function toggleWod(wod) {
  try {
    const { data } = await api.patch(`/wods/${wod.id}/toggle`)
    if (data.activo) {
      wodsHistorial.value = wodsHistorial.value.filter(w => w.id !== wod.id)
      wodsActivos.value.unshift(data)
    } else {
      wodsActivos.value = wodsActivos.value.filter(w => w.id !== wod.id)
      wodsHistorial.value.unshift(data)
    }
  } catch (e) {
    alert(e.response?.data?.detail || 'Error al cambiar estado del WOD.')
  }
}

async function eliminarWod(wod) {
  if (!confirm(`¿Eliminar el WOD "${wod.titulo}"?`)) return
  try {
    await api.delete(`/wods/${wod.id}`)
    wodsActivos.value   = wodsActivos.value.filter(w => w.id !== wod.id)
    wodsHistorial.value = wodsHistorial.value.filter(w => w.id !== wod.id)
  } catch (e) {
    alert(e.response?.data?.detail || 'Error al eliminar.')
  }
}

onMounted(cargar)
</script>
