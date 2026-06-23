<template>
  <div>
    <!-- Saludo -->
    <div class="mb-8">
      <h2 class="text-3xl font-black text-gray-800 tracking-tight">Hola, {{ nombre }}!</h2>
      <p class="text-gray-500 mt-1 capitalize">{{ fechaHoyTexto }}</p>
    </div>

    <!-- ── CLIENTE: Membresía + Plan ── -->
    <template v-if="isCliente">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-8">

        <!-- Tarjeta membresía -->
        <div class="rounded-2xl p-6 text-white shadow-lg" :class="cargandoPerfil ? 'bg-gradient-to-br from-gray-400 to-gray-600' : gradienteMembresia">
          <p class="text-xs font-bold uppercase tracking-widest opacity-80 mb-3">Estado de membresía</p>

          <!-- Cargando: spinner mientras llega /me -->
          <div v-if="cargandoPerfil" class="flex items-center gap-3 py-6">
            <svg class="animate-spin h-7 w-7 text-white/90" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span class="text-sm font-semibold opacity-90">Cargando tu membresía…</span>
          </div>

          <template v-else>
          <div class="flex items-end justify-between gap-4">
            <div>
              <p class="text-4xl font-black leading-none mb-1">
                {{ Math.abs(diasRestantes) }}
                <span class="text-lg font-semibold">{{ diasRestantes === 1 ? 'día' : 'días' }}</span>
              </p>
              <p class="text-sm font-semibold opacity-90 mt-1">{{ etiquetaMembresia }}</p>
              <p v-if="userData.fecha_vencimiento" class="text-xs opacity-70 mt-1">
                Vence el {{ formatFecha(userData.fecha_vencimiento) }}
              </p>
              <p v-if="userData.plan_actual" class="text-xs font-bold mt-2 opacity-90">
                Plan: {{ userData.plan_actual.nombre }}
              </p>
            </div>
            <div class="flex-shrink-0">
              <div class="w-16 h-16 rounded-full flex items-center justify-center bg-white/20">
                <svg v-if="diasRestantes > 7" xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <svg v-else-if="diasRestantes > 0" xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
            </div>
          </div>
          <router-link to="/planes"
            class="inline-block mt-5 px-4 py-2 rounded-lg bg-white/20 hover:bg-white/30 text-white text-sm font-bold transition-colors">
            {{ diasRestantes <= 7 ? 'Renovar membresía' : 'Ver planes' }} →
          </router-link>
          </template>
        </div>

        <!-- Tarjeta plan actual -->
        <div class="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
          <p class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">Mi plan</p>
          <div v-if="cargandoPerfil" class="flex items-center justify-center gap-3 py-8 text-gray-400">
            <svg class="animate-spin h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span class="text-sm font-semibold">Cargando…</span>
          </div>
          <template v-else-if="userData.plan_actual">
            <div class="flex items-start justify-between gap-3 mb-4">
              <div>
                <h3 class="text-xl font-black text-gray-800">{{ userData.plan_actual.nombre }}</h3>
                <p class="text-sm text-gray-500 mt-0.5">
                  {{ userData.plan_actual.duracion_dias }} días ·
                  ${{ userData.plan_actual.precio.toLocaleString('es-CO') }}
                </p>
              </div>
              <div v-if="userData.plan_actual.incluye_wods_personalizados"
                class="flex-shrink-0 px-2.5 py-1 bg-red-100 text-red-700 text-xs font-bold rounded-full">
                WODs pers.
              </div>
            </div>
            <ul v-if="beneficios.length > 0" class="space-y-1.5">
              <li v-for="b in beneficios" :key="b" class="flex items-center gap-2 text-sm text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-emerald-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
                </svg>
                {{ b }}
              </li>
            </ul>
          </template>
          <div v-else class="flex flex-col items-center justify-center py-6 text-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-gray-200 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="text-gray-400 font-medium text-sm">Sin plan activo</p>
            <router-link to="/planes" class="mt-3 text-red-600 font-bold text-sm hover:underline">
              Ver planes disponibles →
            </router-link>
          </div>
        </div>
      </div>
    </template>

    <!-- ── COACH: Tarjeta de staff ── -->
    <template v-if="isCoach">
      <div class="bg-gradient-to-br from-gray-800 to-black rounded-2xl p-6 text-white shadow-lg mb-8 flex items-center gap-5">
        <div class="w-14 h-14 rounded-xl bg-emerald-500 flex items-center justify-center flex-shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
          </svg>
        </div>
        <div>
          <p class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-1">Rol</p>
          <p class="text-2xl font-black">Coach</p>
          <p class="text-sm text-gray-400 mt-0.5">Jain Sport Box</p>
        </div>
      </div>
    </template>

    <!-- ── Historial de asistencias ── -->
    <div>
      <div class="flex items-center justify-between mb-5">
        <div>
          <h3 class="text-xl font-black text-gray-800">Mis Asistencias</h3>
          <p class="text-sm text-gray-500 mt-0.5">Último año</p>
        </div>
        <div v-if="!cargandoAsistencias" class="text-right">
          <p class="text-3xl font-black text-gray-800">{{ totalAsistencias }}</p>
          <p class="text-xs text-gray-400 font-semibold uppercase tracking-wide">días en el año</p>
        </div>
      </div>

      <!-- Spinner -->
      <div v-if="cargandoAsistencias" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600"></div>
      </div>

      <!-- Navegación de mes -->
      <div v-else>
        <div class="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm max-w-xs mx-auto">
          <!-- Cabecera con flechas -->
          <div class="flex items-center justify-between mb-4">
            <button
              @click="mesOffset--"
              :disabled="mesOffset <= MIN_OFFSET"
              class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div class="text-center">
              <p class="text-base font-black text-gray-800">{{ calendarioActual.nombre }}</p>
              <p class="text-xs text-gray-400 font-semibold mt-0.5">
                {{ calendarioActual.count }} día{{ calendarioActual.count !== 1 ? 's' : '' }} asistido{{ calendarioActual.count !== 1 ? 's' : '' }}
              </p>
            </div>
            <button
              @click="mesOffset++"
              :disabled="mesOffset >= 0"
              class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
          <!-- Cabeceras días de la semana -->
          <div class="grid grid-cols-7 mb-1">
            <div v-for="d in ['D','L','M','X','J','V','S']" :key="d"
              class="text-center text-xs font-bold text-gray-400 py-0.5">
              {{ d }}
            </div>
          </div>
          <!-- Celdas días -->
          <div class="grid grid-cols-7 gap-1">
            <template v-for="(cell, idx) in calendarioActual.cells" :key="idx">
              <div v-if="cell === null" />
              <div
                v-else
                class="aspect-square rounded-md flex items-center justify-center text-xs font-semibold transition-colors"
                :class="claseCelda(cell)"
                :title="cell.date"
              >
                {{ cell.day }}
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-if="!cargandoAsistencias && totalAsistencias === 0"
        class="mt-4 bg-gray-50 border-2 border-dashed border-gray-200 rounded-2xl p-8 text-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-300 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <p class="text-gray-400 font-medium">No hay asistencias registradas en el último año</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'
import { useAuth } from '../composables/useAuth'

const { nombre, isCliente, isCoach } = useAuth()

const userData = ref({})
const fechasAsistencia = ref([])
const cargandoAsistencias = ref(true)
const cargandoPerfil = ref(true)   // evita el flash de "-999 días" antes de que llegue /me

// ── Fecha de hoy ──────────────────────────────────────────────
const fechaHoyTexto = computed(() =>
  new Date().toLocaleDateString('es-CO', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
)

// ── Membresía ────────────────────────────────────────────────
const diasRestantes = computed(() => {
  const f = userData.value.fecha_vencimiento
  if (!f) return -999
  const hoy = new Date(); hoy.setHours(0, 0, 0, 0)
  const vence = new Date(f + 'T00:00:00')
  return Math.ceil((vence - hoy) / 86400000)
})

const gradienteMembresia = computed(() => {
  const d = diasRestantes.value
  if (d === -999) return 'bg-gradient-to-br from-gray-500 to-gray-700'
  if (d > 7) return 'bg-gradient-to-br from-emerald-600 to-emerald-800'
  if (d > 0) return 'bg-gradient-to-br from-amber-500 to-orange-600'
  return 'bg-gradient-to-br from-red-600 to-red-800'
})

const etiquetaMembresia = computed(() => {
  const d = diasRestantes.value
  if (d === -999) return 'Sin membresía activa'
  if (d > 1) return `${d} días restantes`
  if (d === 1) return 'Vence mañana'
  if (d === 0) return 'Vence hoy'
  return `Venció hace ${Math.abs(d)} día${Math.abs(d) !== 1 ? 's' : ''}`
})

const beneficios = computed(() => {
  try {
    return JSON.parse(userData.value.plan_actual?.beneficios || '[]')
  } catch {
    return []
  }
})

function formatFecha(f) {
  return new Date(f + 'T12:00:00').toLocaleDateString('es-CO', { day: 'numeric', month: 'long', year: 'numeric' })
}

// ── Calendario de asistencias ────────────────────────────────
const MESES_ATRAS = 11
const MIN_OFFSET = -MESES_ATRAS
const mesOffset = ref(0) // 0 = mes actual, -1 = mes anterior, etc.

const totalAsistencias = computed(() => fechasAsistencia.value.length)

const attendedSet = computed(() => new Set(fechasAsistencia.value))

function buildMonth(year, month) {
  const MESES = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
  const today = new Date()
  const firstDow = new Date(year, month, 1).getDay()
  const totalDays = new Date(year, month + 1, 0).getDate()

  const cells = []
  for (let i = 0; i < firstDow; i++) cells.push(null)
  for (let d = 1; d <= totalDays; d++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    const dayDate = new Date(year, month, d)
    cells.push({
      day: d,
      date: dateStr,
      attended: attendedSet.value.has(dateStr),
      isFuture: dayDate > today,
      isToday: d === today.getDate() && month === today.getMonth() && year === today.getFullYear(),
    })
  }

  return {
    nombre: `${MESES[month]} ${year}`,
    key: `${year}-${month}`,
    count: cells.filter(c => c?.attended).length,
    cells,
  }
}

const calendarioActual = computed(() => {
  const today = new Date()
  let y = today.getFullYear()
  let m = today.getMonth() + mesOffset.value
  while (m < 0) { m += 12; y-- }
  while (m > 11) { m -= 12; y++ }
  return buildMonth(y, m)
})

function claseCelda(cell) {
  if (cell.isFuture) return 'bg-gray-50 text-gray-300 cursor-default'
  if (cell.attended && cell.isToday) return 'bg-emerald-500 text-white ring-2 ring-emerald-300'
  if (cell.attended) return 'bg-emerald-500 text-white'
  if (cell.isToday) return 'bg-gray-800 text-white'
  return 'bg-transparent text-gray-400'
}

// ── Fetch ────────────────────────────────────────────────────
async function cargar() {
  try {
    const [meRes, asistRes] = await Promise.all([
      api.get('/me'),
      api.get('/asistencia/mi-historial?meses=12'),
    ])
    userData.value = meRes.data
    fechasAsistencia.value = asistRes.data.fechas || []
  } catch (e) {
    console.error(e)
  } finally {
    cargandoAsistencias.value = false
    cargandoPerfil.value = false
  }
}

onMounted(cargar)
</script>
