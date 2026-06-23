<template>
  <div class="animate-fade-in-up">

    <!-- Header -->
    <div class="mb-6">
      <h2 class="text-3xl font-extrabold text-gray-900 tracking-tight">Sesiones</h2>
      <p class="text-gray-500 mt-1">Asistentes por bloque horario</p>
    </div>

    <!-- Selector de modo -->
    <div class="flex gap-2 mb-6">
      <button
        @click="setModo('semana')"
        class="px-5 py-2 rounded-xl font-bold text-sm transition-colors border"
        :class="modo === 'semana'
          ? 'bg-gray-900 text-white border-gray-900'
          : 'bg-white text-gray-600 border-gray-200 hover:border-gray-400'">
        Esta semana
      </button>
      <button
        @click="setModo('mes')"
        class="px-5 py-2 rounded-xl font-bold text-sm transition-colors border"
        :class="modo === 'mes'
          ? 'bg-gray-900 text-white border-gray-900'
          : 'bg-white text-gray-600 border-gray-200 hover:border-gray-400'">
        Este mes
      </button>
      <button
        @click="setModo('fecha')"
        class="px-5 py-2 rounded-xl font-bold text-sm transition-colors border"
        :class="modo === 'fecha'
          ? 'bg-gray-900 text-white border-gray-900'
          : 'bg-white text-gray-600 border-gray-200 hover:border-gray-400'">
        Fecha específica
      </button>
    </div>

    <!-- ── MODO SEMANA ── -->
    <template v-if="modo === 'semana'">

      <!-- Tabs de días -->
      <div class="flex gap-2 mb-6 overflow-x-auto pb-1">
        <button
          v-for="d in diasSemana" :key="d.fecha"
          @click="diaSeleccionado = d.fecha"
          class="flex-shrink-0 flex flex-col items-center px-4 py-3 rounded-2xl border font-semibold transition-all"
          :class="[
            diaSeleccionado === d.fecha
              ? 'bg-red-600 text-white border-red-600 shadow-md'
              : d.esHoy
                ? 'bg-gray-900 text-white border-gray-900'
                : 'bg-white text-gray-600 border-gray-200 hover:border-red-400',
            d.total === 0 ? 'opacity-40' : ''
          ]">
          <span class="text-xs uppercase tracking-widest mb-1">{{ d.nombreDia }}</span>
          <span class="text-lg font-extrabold leading-none">{{ d.numeroDia }}</span>
          <span
            v-if="d.total > 0"
            class="mt-1.5 text-xs font-bold px-2 py-0.5 rounded-full"
            :class="diaSeleccionado === d.fecha ? 'bg-red-500 text-white' : 'bg-red-100 text-red-600'">
            {{ d.total }}
          </span>
          <span v-else class="mt-1.5 text-xs text-gray-400">—</span>
        </button>
      </div>

      <!-- Búsqueda -->
      <div class="mb-4">
        <input
          type="text"
          v-model="busqueda"
          placeholder="Buscar por nombre…"
          class="w-full max-w-sm border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-400" />
      </div>

      <!-- Skeleton -->
      <div v-if="cargando" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="i in 3" :key="i" class="bg-gray-100 rounded-2xl h-16 animate-pulse"></div>
      </div>

      <!-- Bloques del día seleccionado -->
      <template v-else>
        <div v-if="bloquesDiaFiltrados.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <BloqueCard
            v-for="b in bloquesDiaFiltrados"
            :key="b.fecha + '-' + b.hora_inicio"
            :bloque="b"
            :busqueda="busqueda" />
        </div>
        <div v-else class="text-center py-16 text-gray-400">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mx-auto mb-3 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p class="font-semibold text-gray-500">
            {{ busqueda ? `Sin resultados para "${busqueda}"` : 'Sin asistencias este día' }}
          </p>
        </div>
      </template>
    </template>

    <!-- ── MODO MES ── -->
    <template v-else-if="modo === 'mes'">

      <!-- Navegación de mes -->
      <div class="flex items-center justify-between mb-5 max-w-md mx-auto">
        <button
          @click="cambiarMes(-1)"
          class="p-2 rounded-xl border border-gray-200 hover:border-gray-400 transition-colors bg-white">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <h3 class="text-lg font-extrabold text-gray-900 capitalize">{{ nombreMesActual }}</h3>
        <button
          @click="cambiarMes(1)"
          :disabled="mesOffset >= 0"
          class="p-2 rounded-xl border border-gray-200 hover:border-gray-400 transition-colors bg-white disabled:opacity-30 disabled:cursor-not-allowed">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>

      <!-- Skeleton mes -->
      <div v-if="cargandoMes" class="bg-white rounded-2xl border border-gray-100 p-4 animate-pulse max-w-md mx-auto">
        <div class="grid grid-cols-7 gap-1">
          <div v-for="i in 35" :key="i" class="h-12 bg-gray-100 rounded-xl"></div>
        </div>
      </div>

      <!-- Grilla calendario -->
      <div v-else class="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm mb-6 max-w-md mx-auto">
        <!-- Encabezados días -->
        <div class="grid grid-cols-7 gap-1 mb-2">
          <div
            v-for="h in ['Lun','Mar','Mié','Jue','Vie','Sáb','Dom']"
            :key="h"
            class="text-center text-xs font-bold text-gray-400 py-1 uppercase tracking-wide">
            {{ h }}
          </div>
        </div>
        <!-- Semanas -->
        <div v-for="(semana, si) in semanaMes" :key="si" class="grid grid-cols-7 gap-1 mb-1">
          <div
            v-for="(dia, di) in semana"
            :key="di"
            @click="dia && seleccionarDiaMes(dia.fecha)"
            class="relative flex flex-col items-center justify-center rounded-xl py-1.5 min-h-[52px] transition-all"
            :class="[
              !dia ? 'pointer-events-none' : 'cursor-pointer',
              dia && diaSeleccionadoMes === dia.fecha
                ? 'bg-red-600 text-white shadow-md'
                : dia && dia.esHoy
                  ? 'bg-gray-900 text-white'
                  : dia && dia.total > 0
                    ? 'bg-red-50 hover:bg-red-100 text-gray-800'
                    : dia
                      ? 'hover:bg-gray-50 text-gray-400'
                      : ''
            ]">
            <span v-if="dia" class="text-sm font-bold leading-none">{{ dia.numeroDia }}</span>
            <span
              v-if="dia && dia.total > 0"
              class="mt-1 text-xs font-semibold px-1.5 py-0.5 rounded-full leading-none"
              :class="diaSeleccionadoMes === dia.fecha
                ? 'bg-red-500 text-white'
                : dia.esHoy
                  ? 'bg-gray-700 text-white'
                  : 'bg-red-200 text-red-700'">
              {{ dia.total }}
            </span>
          </div>
        </div>
      </div>

      <!-- Bloques del día seleccionado -->
      <template v-if="diaSeleccionadoMes">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
          <h4 class="font-bold text-gray-700 text-sm uppercase tracking-wide">
            Sesiones del {{ diaSeleccionadoMes.split('-').reverse().join('/') }}
          </h4>
          <input
            type="text"
            v-model="busqueda"
            placeholder="Buscar por nombre…"
            class="border border-gray-200 rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400 w-full sm:w-96" />
        </div>
        <div v-if="bloquesDiaMesFiltrados.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <BloqueCard
            v-for="b in bloquesDiaMesFiltrados"
            :key="b.fecha + '-' + b.hora_inicio"
            :bloque="b"
            :busqueda="busqueda" />
        </div>
        <div v-else class="text-center py-12 text-gray-400">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mx-auto mb-3 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p class="font-semibold text-gray-500">
            {{ busqueda ? `Sin resultados para "${busqueda}"` : 'Sin asistencias este día' }}
          </p>
        </div>
      </template>
      <div v-else class="text-center py-8 text-gray-400 text-sm">
        Selecciona un día del calendario para ver sus sesiones
      </div>

    </template>

    <!-- ── MODO FECHA ESPECÍFICA ── -->
    <template v-else>
      <div class="flex flex-wrap items-end gap-3 mb-6">
        <div>
          <label class="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">Fecha</label>
          <input
            type="date"
            v-model="fechaEspecifica"
            class="border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-400" />
        </div>
        <button
          @click="consultarFecha"
          :disabled="!fechaEspecifica || cargando"
          class="px-5 py-2.5 bg-red-600 hover:bg-red-700 disabled:opacity-40 text-white font-bold rounded-xl text-sm transition-colors">
          Ver sesiones
        </button>
        <div class="flex-1 min-w-[180px]">
          <label class="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">Buscar persona</label>
          <input
            type="text"
            v-model="busqueda"
            placeholder="Nombre del asistente…"
            class="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-400" />
        </div>
      </div>

      <p v-if="error" class="mb-4 text-sm text-red-600 font-medium">{{ error }}</p>

      <div v-if="cargando" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="i in 3" :key="i" class="bg-gray-100 rounded-2xl h-16 animate-pulse"></div>
      </div>
      <template v-else-if="consultado">
        <div v-if="bloquesFechaFiltrados.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <BloqueCard
            v-for="b in bloquesFechaFiltrados"
            :key="b.fecha + '-' + b.hora_inicio"
            :bloque="b"
            :busqueda="busqueda" />
        </div>
        <div v-else class="text-center py-16 text-gray-400">
          <p class="font-semibold text-gray-500">
            {{ busqueda ? `Sin resultados para "${busqueda}"` : 'Sin asistencias en esta fecha' }}
          </p>
        </div>
      </template>
    </template>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'
import BloqueCard from '../components/BloqueCard.vue'

// ── Estado ──
const modo = ref('semana')
const bloques = ref([])        // todos los bloques traídos del backend
const bloquesDate = ref([])    // bloques para modo fecha específica
const busqueda = ref('')
const cargando = ref(false)
const error = ref('')
const consultado = ref(false)

// Semana
const diasSemana = ref([])
const diaSeleccionado = ref('')

// Fecha específica
const fechaEspecifica = ref('')

// Mes
const mesOffset = ref(0)       // 0 = mes actual, -1 = mes anterior, etc.
const bloquesMes = ref([])
const diaSeleccionadoMes = ref('')
const cargandoMes = ref(false)

// ── Helpers de fecha ──
const DIAS_CORTO  = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
const MESES_CORTO = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

function isoHoy() {
  return new Date().toISOString().slice(0, 10)
}

function calcularSemana() {
  const hoy = new Date()
  const dow = hoy.getDay()                         // 0=Dom
  const lunes = new Date(hoy)
  lunes.setDate(hoy.getDate() - (dow === 0 ? 6 : dow - 1))
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(lunes)
    d.setDate(lunes.getDate() + i)
    return d.toISOString().slice(0, 10)
  })
}

function buildDiasSemana(fechas, bloquesData) {
  const conteosPorFecha = {}
  for (const b of bloquesData) {
    conteosPorFecha[b.fecha] = (conteosPorFecha[b.fecha] || 0) + b.total
  }
  const hoy = isoHoy()
  return fechas.map(f => {
    const [y, m, d] = f.split('-').map(Number)
    const dt = new Date(y, m - 1, d)
    return {
      fecha:      f,
      nombreDia:  DIAS_CORTO[dt.getDay()],
      numeroDia:  d,
      mes:        MESES_CORTO[m - 1],
      esHoy:      f === hoy,
      total:      conteosPorFecha[f] || 0,
    }
  })
}

// ── Helpers mes ──
const MESES_LARGO = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

function getMesInfo(offset) {
  const hoy = new Date()
  const d = new Date(hoy.getFullYear(), hoy.getMonth() + offset, 1)
  return { year: d.getFullYear(), month: d.getMonth() }  // month: 0-indexed
}

const nombreMesActual = computed(() => {
  const { year, month } = getMesInfo(mesOffset.value)
  return `${MESES_LARGO[month]} ${year}`
})

const semanaMes = computed(() => {
  const { year, month } = getMesInfo(mesOffset.value)
  const ultimoDia = new Date(year, month + 1, 0).getDate()

  const totales = {}
  for (const b of bloquesMes.value) {
    totales[b.fecha] = (totales[b.fecha] || 0) + b.total
  }

  const hoy = isoHoy()

  // DOW del primer día (Mon=0 … Sun=6)
  let dow = new Date(year, month, 1).getDay()
  dow = dow === 0 ? 6 : dow - 1

  const semanas = []
  let semana = Array(dow).fill(null)

  for (let d = 1; d <= ultimoDia; d++) {
    const f = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    semana.push({ fecha: f, numeroDia: d, esHoy: f === hoy, total: totales[f] || 0 })
    if (semana.length === 7) { semanas.push(semana); semana = [] }
  }
  if (semana.length) {
    while (semana.length < 7) semana.push(null)
    semanas.push(semana)
  }
  return semanas
})

// ── Bloques filtrados del día seleccionado en mes ──
const bloquesDiaMesFiltrados = computed(() => {
  if (!diaSeleccionadoMes.value) return []
  const q = busqueda.value.trim().toLowerCase()
  return bloquesMes.value
    .filter(b => b.fecha === diaSeleccionadoMes.value)
    .map(b => ({
      ...b,
      asistentes: q ? b.asistentes.filter(a => a.nombre.toLowerCase().includes(q)) : b.asistentes,
    }))
    .filter(b => b.asistentes.length > 0)
})

// ── Bloques filtrados por día (modo semana) ──
const bloquesDiaFiltrados = computed(() => {
  const q = busqueda.value.trim().toLowerCase()
  return bloques.value
    .filter(b => b.fecha === diaSeleccionado.value)
    .map(b => ({
      ...b,
      asistentes: q
        ? b.asistentes.filter(a => a.nombre.toLowerCase().includes(q))
        : b.asistentes,
    }))
    .filter(b => b.asistentes.length > 0)
})

// ── Bloques filtrados para fecha específica ──
const bloquesFechaFiltrados = computed(() => {
  const q = busqueda.value.trim().toLowerCase()
  return bloquesDate.value
    .map(b => ({
      ...b,
      asistentes: q
        ? b.asistentes.filter(a => a.nombre.toLowerCase().includes(q))
        : b.asistentes,
    }))
    .filter(b => b.asistentes.length > 0)
})

// ── Fetch semana ──
async function cargarSemana() {
  const fechas = calcularSemana()
  const desde  = fechas[0]
  const hasta  = fechas[6]
  cargando.value = true
  error.value = ''
  try {
    const { data } = await api.get('/asistencia/sesiones-por-bloque', {
      params: { desde, hasta },
    })
    bloques.value = data.bloques
    diasSemana.value = buildDiasSemana(fechas, data.bloques)
    // Seleccionar hoy si está en la semana, si no el primer día con datos
    const hoy = isoHoy()
    const conDatos = diasSemana.value.find(d => d.total > 0 && d.fecha === hoy)
      || diasSemana.value.find(d => d.total > 0)
    diaSeleccionado.value = conDatos ? conDatos.fecha : fechas[0]
  } catch (e) {
    error.value = e.response?.data?.detail || 'Error al cargar la semana'
  } finally {
    cargando.value = false
  }
}

// ── Fetch mes ──
async function cargarMes() {
  const { year, month } = getMesInfo(mesOffset.value)
  const mm = String(month + 1).padStart(2, '0')
  const ultimoDia = new Date(year, month + 1, 0).getDate()
  const desde = `${year}-${mm}-01`
  const hasta = `${year}-${mm}-${String(ultimoDia).padStart(2, '0')}`

  cargandoMes.value = true
  error.value = ''
  try {
    const { data } = await api.get('/asistencia/sesiones-por-bloque', { params: { desde, hasta } })
    bloquesMes.value = data.bloques
    const hoy = isoHoy()
    const esMesActual = hoy.startsWith(`${year}-${mm}`)
    if (esMesActual && data.bloques.some(b => b.fecha === hoy)) {
      diaSeleccionadoMes.value = hoy
    } else {
      diaSeleccionadoMes.value = data.bloques[0]?.fecha || ''
    }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Error al cargar el mes'
    bloquesMes.value = []
  } finally {
    cargandoMes.value = false
  }
}

async function cambiarMes(delta) {
  mesOffset.value = Math.min(0, mesOffset.value + delta)
  diaSeleccionadoMes.value = ''
  busqueda.value = ''
  await cargarMes()
}

function seleccionarDiaMes(fecha) {
  diaSeleccionadoMes.value = diaSeleccionadoMes.value === fecha ? '' : fecha
  busqueda.value = ''
}

// ── Fetch fecha específica ──
async function consultarFecha() {
  if (!fechaEspecifica.value) return
  cargando.value = true
  error.value = ''
  busqueda.value = ''
  try {
    const { data } = await api.get('/asistencia/sesiones-por-bloque', {
      params: { desde: fechaEspecifica.value, hasta: fechaEspecifica.value },
    })
    bloquesDate.value = data.bloques
    consultado.value = true
  } catch (e) {
    error.value = e.response?.data?.detail || 'Error al consultar'
    bloquesDate.value = []
  } finally {
    cargando.value = false
  }
}

function setModo(m) {
  modo.value = m
  busqueda.value = ''
  error.value = ''
  consultado.value = false
  if (m === 'semana') cargarSemana()
  else if (m === 'mes') { mesOffset.value = 0; diaSeleccionadoMes.value = ''; cargarMes() }
}

onMounted(() => cargarSemana())
</script>
