<template>
  <div v-if="tipo" class="animate-fade-in-up">

    <!-- Header -->
    <div class="flex items-center gap-3 mb-6">
      <RouterLink to="/salud"
        class="flex items-center gap-1.5 text-sm font-semibold text-gray-400 hover:text-gray-700 transition-colors">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
        Mi Salud
      </RouterLink>
      <span class="text-gray-200">/</span>
      <h2 class="text-2xl font-extrabold text-gray-900">{{ tipo.label }}</h2>
    </div>

    <!-- Skeleton de carga -->
    <div v-if="cargando" class="space-y-5">
      <div class="bg-gray-100 rounded-2xl h-28 animate-pulse"></div>
      <div class="bg-gray-100 rounded-2xl h-72 animate-pulse"></div>
      <div class="bg-gray-100 rounded-2xl h-48 animate-pulse"></div>
    </div>

    <template v-else>

      <!-- Resumen + botón registrar -->
      <div class="bg-white rounded-2xl border shadow-sm p-5 mb-5 flex items-center justify-between gap-4"
        :class="tipo.colorBorder">
        <div>
          <p class="text-xs font-bold uppercase tracking-widest mb-1" :class="tipo.colorText">Última medida</p>
          <p class="text-4xl font-black leading-none"
            :class="ultimoValor !== null ? 'text-gray-900' : 'text-gray-300'">
            <template v-if="ultimoValor !== null">
              {{ ultimoValor }}<span class="text-lg font-semibold text-gray-400 ml-1">{{ tipo.unidad }}</span>
            </template>
            <template v-else>—</template>
          </p>
          <p v-if="delta !== null" class="text-sm font-semibold mt-1.5">
            <template v-if="delta > 0">
              <span class="text-red-500">↑ {{ Math.abs(delta) }} {{ tipo.unidad }} vs anterior</span>
            </template>
            <template v-else-if="delta < 0">
              <span class="text-emerald-600">↓ {{ Math.abs(delta) }} {{ tipo.unidad }} vs anterior</span>
            </template>
            <template v-else>
              <span class="text-gray-400">Sin cambio</span>
            </template>
          </p>
          <p class="text-xs text-gray-400 mt-1">{{ registros.length }} registro{{ registros.length !== 1 ? 's' : '' }}</p>
        </div>
        <button @click="mostrarModal = true"
          class="shrink-0 flex items-center gap-2 text-white font-bold py-3 px-5 rounded-xl shadow-sm transition-colors"
          :class="tipo.colorBtn">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4"/>
          </svg>
          Registrar
        </button>
      </div>

      <!-- Gráfica -->
      <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 mb-5">
        <h3 class="font-bold text-gray-800 mb-4 flex items-center gap-2">
          <span class="w-3 h-3 rounded-full inline-block" :style="{ backgroundColor: tipo.hex }"></span>
          Evolución de {{ tipo.label }}
        </h3>
        <div v-if="registros.length >= 2" class="relative h-64">
          <canvas ref="chartCanvas"></canvas>
        </div>
        <div v-else class="h-32 flex flex-col items-center justify-center text-gray-400 text-sm gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-gray-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
          </svg>
          <span>Agrega al menos 2 registros para ver la gráfica</span>
        </div>
      </div>

      <!-- Historial -->
      <div class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h3 class="font-bold text-gray-800">Historial</h3>
          <span class="text-xs text-gray-400">{{ registros.length }} registros</span>
        </div>

        <div v-if="registros.length === 0" class="px-6 py-14 text-center">
          <p class="text-gray-400 text-sm">Sin registros aún. Presiona <strong>Registrar</strong> para empezar.</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-100">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-5 py-3 text-left text-xs font-bold text-gray-400 uppercase tracking-wider">Fecha</th>
                <th class="px-5 py-3 text-left text-xs font-bold text-gray-400 uppercase tracking-wider">
                  {{ tipo.label }} ({{ tipo.unidad }})
                </th>
                <th class="px-5 py-3 text-left text-xs font-bold text-gray-400 uppercase tracking-wider">Notas</th>
                <th class="px-5 py-3"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="r in [...registros].reverse()" :key="r.id"
                class="hover:bg-gray-50 transition-colors group">
                <td class="px-5 py-3.5 text-sm font-medium text-gray-700 whitespace-nowrap">
                  {{ formatFecha(r.fecha) }}
                </td>
                <td class="px-5 py-3.5 whitespace-nowrap">
                  <span class="text-sm font-black text-gray-900">{{ r[tipo.key] }}</span>
                  <span class="text-xs text-gray-400 ml-1">{{ tipo.unidad }}</span>
                </td>
                <td class="px-5 py-3.5 text-sm text-gray-400 max-w-[200px] truncate">
                  {{ r.notas || '—' }}
                </td>
                <td class="px-5 py-3.5 text-right whitespace-nowrap">
                  <button @click="eliminar(r)"
                    class="opacity-0 group-hover:opacity-100 p-1.5 text-gray-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </template>

    <!-- Modal: registrar medida -->
    <div v-if="mostrarModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm">
        <div class="p-5 border-b border-gray-100 flex items-center justify-between">
          <h3 class="text-lg font-bold text-gray-800">Registrar {{ tipo.label }}</h3>
          <button @click="cerrarModal" class="p-2 rounded-lg hover:bg-gray-100 text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <form @submit.prevent="guardar" class="p-5 space-y-4">
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">Fecha</label>
            <input v-model="formFecha" type="date" required
              class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none">
          </div>
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">
              {{ tipo.label }} ({{ tipo.unidad }})
            </label>
            <input v-model.number="formValor" type="number"
              :step="tipo.step" :min="tipo.min" :max="tipo.max"
              :placeholder="tipo.placeholder"
              required autofocus
              class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none text-xl font-black">
          </div>
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">
              Notas <span class="text-gray-400 font-normal">(opcional)</span>
            </label>
            <textarea v-model="formNotas" rows="2" placeholder="Ej: Después del entrenamiento..."
              class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none resize-none text-sm">
            </textarea>
          </div>
          <div v-if="errorForm" class="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg p-3">
            {{ errorForm }}
          </div>
          <div class="flex gap-3 pt-1">
            <button type="button" @click="cerrarModal"
              class="flex-1 py-2.5 rounded-xl border border-gray-300 text-gray-600 font-semibold hover:bg-gray-50 transition-colors">
              Cancelar
            </button>
            <button type="submit" :disabled="guardando"
              class="flex-1 py-2.5 rounded-xl text-white font-bold transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
              :class="tipo.colorBtn">
              <span v-if="guardando" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
              {{ guardando ? 'Guardando...' : 'Guardar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { Chart } from 'chart.js/auto'
import api from '../api'
import { TIPOS_SALUD } from '../data/saludTipos'

const route  = useRoute()
const router = useRouter()

// ── Config del tipo activo ─────────────────────────────────────
const tipo = computed(() => TIPOS_SALUD.find(t => t.param === route.params.tipo) ?? null)

// ── Estado ─────────────────────────────────────────────────────
const registros    = ref([])
const cargando     = ref(true)
const mostrarModal = ref(false)
const guardando    = ref(false)
const errorForm    = ref('')
const formFecha    = ref(new Date().toISOString().slice(0, 10))
const formValor    = ref('')
const formNotas    = ref('')

// ── Chart ──────────────────────────────────────────────────────
const chartCanvas = ref(null)
let instanciaChart = null

function destruirChart() {
  if (instanciaChart) { instanciaChart.destroy(); instanciaChart = null }
}

function renderChart() {
  if (!chartCanvas.value || registros.value.length < 2 || !tipo.value) return
  destruirChart()
  const labels  = registros.value.map(r => formatFecha(r.fecha))
  const valores = registros.value.map(r => r[tipo.value.key])
  const hex     = tipo.value.hex
  instanciaChart = new Chart(chartCanvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: `${tipo.value.label} (${tipo.value.unidad})`,
        data: valores,
        borderColor: hex,
        backgroundColor: hex + '18',
        borderWidth: 2.5,
        pointBackgroundColor: hex,
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 5,
        pointHoverRadius: 7,
        fill: true,
        tension: 0.35,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 600 },
      plugins: {
        legend: { display: false },
        tooltip: { mode: 'index', intersect: false },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { size: 11 }, maxTicksLimit: 8, maxRotation: 30 },
        },
        y: {
          grid: { color: '#f3f4f6' },
          ticks: { font: { size: 11 } },
          suggestedMin: Math.max(0, Math.min(...valores) - 5),
          suggestedMax: Math.max(...valores) + 5,
        },
      },
    },
  })
}

watch(registros, async (val) => {
  if (val.length < 2) { destruirChart(); return }
  await nextTick()
  await nextTick()
  renderChart()
})

// ── Helpers ────────────────────────────────────────────────────
const formatFecha = (f) =>
  new Date(f + 'T12:00:00').toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })

const ultimoValor = computed(() =>
  registros.value.length ? registros.value[registros.value.length - 1][tipo.value.key] : null
)

const delta = computed(() => {
  if (registros.value.length < 2) return null
  const key  = tipo.value.key
  const prev = registros.value[registros.value.length - 2][key]
  const curr = registros.value[registros.value.length - 1][key]
  return Math.round((curr - prev) * 10) / 10
})

// ── API ────────────────────────────────────────────────────────
async function cargar() {
  if (!tipo.value) return
  cargando.value = true
  try {
    const { data } = await api.get(`/salud/${tipo.value.param}`)
    registros.value = data
  } finally {
    cargando.value = false
  }
}

function cerrarModal() {
  mostrarModal.value = false
  formValor.value = ''
  formNotas.value = ''
  errorForm.value = ''
}

async function guardar() {
  guardando.value = true
  errorForm.value = ''
  try {
    await api.post(`/salud/${tipo.value.param}`, {
      fecha: formFecha.value,
      valor: formValor.value,
      notas: formNotas.value || null,
    })
    cerrarModal()
    await cargar()
  } catch (e) {
    const d = e.response?.data?.detail
    errorForm.value = Array.isArray(d) ? d[0].msg : (d || 'Error al guardar.')
  } finally {
    guardando.value = false
  }
}

async function eliminar(r) {
  if (!confirm(`¿Eliminar el registro del ${formatFecha(r.fecha)}?`)) return
  try {
    await api.delete(`/salud/${r.id}`)
    await cargar()
  } catch (e) {
    alert(e.response?.data?.detail || 'Error al eliminar.')
  }
}

// ── Ciclo de vida ──────────────────────────────────────────────
onMounted(() => {
  if (!tipo.value) { router.replace('/salud'); return }
  cargar()
})

// Recarga si el usuario navega de /salud/peso a /salud/altura
watch(
  () => route.params.tipo,
  () => {
    if (!tipo.value) { router.replace('/salud'); return }
    destruirChart()
    registros.value = []
    formFecha.value = new Date().toISOString().slice(0, 10)
    cargar()
  }
)

onUnmounted(destruirChart)
</script>

<style scoped>
.animate-fade-in-up {
  animation: fadeInUp 0.35s ease-out;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
