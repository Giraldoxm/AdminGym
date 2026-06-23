<template>
  <div class="animate-fade-in-up">

    <!-- ── Header ── -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
      <div>
        <h2 class="text-3xl font-extrabold text-gray-900 tracking-tight">Módulo Financiero</h2>
        <p class="text-gray-500 mt-1">Flujo de caja · Ingresos y egresos del box</p>
      </div>
      <button @click="abrirModal()"
        class="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white font-bold py-2.5 px-5 rounded-lg shadow transition-colors">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Nuevo movimiento
      </button>
    </div>

    <!-- ── Selector de período ── -->
    <div class="flex flex-wrap gap-2 mb-6">
      <button v-for="p in periodos" :key="p.key" @click="seleccionarPeriodo(p.key)"
        class="px-4 py-1.5 rounded-full text-sm font-semibold transition-colors"
        :class="periodoActivo === p.key
          ? 'bg-red-600 text-white shadow'
          : 'bg-white text-gray-600 border border-gray-200 hover:border-red-300 hover:text-red-600'">
        {{ p.label }}
      </button>
      <!-- Rango personalizado -->
      <div v-if="periodoActivo === 'rango'" class="flex items-center gap-2 ml-2">
        <input v-model="rangoDesde" type="date" @change="cargarTodo"
          class="text-sm border border-gray-300 rounded-lg px-3 py-1.5 focus:ring-2 focus:ring-red-500 outline-none">
        <span class="text-gray-400 text-sm">→</span>
        <input v-model="rangoHasta" type="date" @change="cargarTodo"
          class="text-sm border border-gray-300 rounded-lg px-3 py-1.5 focus:ring-2 focus:ring-red-500 outline-none">
      </div>
    </div>

    <!-- ── Cards de resumen ── -->
    <div v-if="cargandoBalance" class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div v-for="i in 4" :key="i" class="bg-white rounded-2xl p-6 animate-pulse h-32 border border-gray-100"></div>
    </div>
    <div v-else class="space-y-4 mb-6">

      <!-- Fila 1: Ingresos separados -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

        <!-- Membresías -->
        <div class="bg-white rounded-2xl p-5 border border-red-100 shadow-sm">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold text-red-600 uppercase tracking-widest">Membresías</span>
            <div class="w-9 h-9 rounded-xl bg-red-100 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
            </div>
          </div>
          <p class="text-2xl font-black text-gray-900">{{ formatMoneda(balance.total_membresias) }}</p>
          <p class="text-xs text-red-400 mt-1">Pagos de planes y renovaciones</p>
          <div class="mt-3 pt-3 border-t border-red-50 flex items-center justify-between">
            <span class="text-xs text-gray-400">% del total ingresos</span>
            <span class="text-xs font-bold text-red-600">
              {{ balance.ingresos_total > 0 ? Math.round(balance.total_membresias / balance.ingresos_total * 100) : 0 }}%
            </span>
          </div>
        </div>

        <!-- Tienda -->
        <div class="bg-white rounded-2xl p-5 border border-violet-100 shadow-sm">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold text-violet-600 uppercase tracking-widest">Tienda</span>
            <div class="w-9 h-9 rounded-xl bg-violet-100 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-violet-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/>
              </svg>
            </div>
          </div>
          <p class="text-2xl font-black text-gray-900">{{ formatMoneda(balance.total_tienda) }}</p>
          <p class="text-xs text-violet-400 mt-1">Ventas de productos del box</p>
          <div class="mt-3 pt-3 border-t border-violet-50 flex items-center justify-between">
            <span class="text-xs text-gray-400">% del total ingresos</span>
            <span class="text-xs font-bold text-violet-600">
              {{ balance.ingresos_total > 0 ? Math.round(balance.total_tienda / balance.ingresos_total * 100) : 0 }}%
            </span>
          </div>
        </div>
      </div>

      <!-- Fila 2: Totales -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">

        <!-- Total Ingresos -->
        <div class="bg-white rounded-2xl p-5 border border-emerald-100 shadow-sm">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold text-emerald-600 uppercase tracking-widest">Total Ingresos</span>
            <div class="w-9 h-9 rounded-xl bg-emerald-100 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11l5-5m0 0l5 5m-5-5v12"/>
              </svg>
            </div>
          </div>
          <p class="text-2xl font-black text-gray-900">{{ formatMoneda(balance.ingresos_total) }}</p>
          <div class="flex flex-wrap gap-1.5 mt-3">
            <span v-for="(val, cat) in balance.ingresos_por_categoria" :key="cat"
              class="text-xs bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full font-medium">
              {{ labelCategoria(cat) }} · {{ formatMoneda(val) }}
            </span>
          </div>
        </div>

        <!-- Egresos -->
        <div class="bg-white rounded-2xl p-5 border border-red-100 shadow-sm">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold text-red-500 uppercase tracking-widest">Egresos</span>
            <div class="w-9 h-9 rounded-xl bg-red-100 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 13l-5 5m0 0l-5-5m5 5V6"/>
              </svg>
            </div>
          </div>
          <p class="text-2xl font-black text-gray-900">{{ formatMoneda(balance.egresos_total) }}</p>
          <div class="flex flex-wrap gap-1.5 mt-3">
            <span v-for="(val, cat) in balance.egresos_por_categoria" :key="cat"
              class="text-xs bg-red-50 text-red-600 px-2 py-0.5 rounded-full font-medium">
              {{ labelCategoria(cat) }} · {{ formatMoneda(val) }}
            </span>
            <span v-if="!Object.keys(balance.egresos_por_categoria || {}).length"
              class="text-xs text-gray-400 italic">Sin egresos en este período</span>
          </div>
        </div>

        <!-- Balance neto -->
        <div class="rounded-2xl p-5 shadow-sm"
          :class="balance.balance_neto >= 0
            ? 'bg-gradient-to-br from-red-600 to-red-700 border border-red-500'
            : 'bg-gradient-to-br from-red-600 to-red-700 border border-red-500'">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold text-white/70 uppercase tracking-widest">Balance Neto</span>
            <div class="w-9 h-9 rounded-xl bg-white/10 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3"/>
              </svg>
            </div>
          </div>
          <p class="text-2xl font-black text-white">
            {{ balance.balance_neto >= 0 ? '+' : '' }}{{ formatMoneda(balance.balance_neto) }}
          </p>
          <p class="text-sm text-white/70 mt-2">
            {{ balance.balance_neto >= 0 ? 'Flujo positivo' : 'Flujo negativo' }}
            · {{ labelPeriodo }}
          </p>
        </div>
      </div>
    </div>

    <!-- ── Historial ── -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-100 flex flex-wrap items-center justify-between gap-3">
        <h3 class="font-bold text-gray-800">Historial de movimientos</h3>
        <div class="flex flex-wrap items-center gap-2">
          <!-- Filtro tipo -->
          <div class="flex items-center gap-1 bg-gray-100 p-1 rounded-lg">
            <button @click="filtroTipo = null; cargarMovimientos()"
              class="text-xs px-3 py-1 rounded-md font-semibold transition-colors"
              :class="filtroTipo === null ? 'bg-white shadow text-gray-800' : 'text-gray-500 hover:text-gray-700'">
              Todos
            </button>
            <button @click="filtroTipo = 'ingreso'; cargarMovimientos()"
              class="text-xs px-3 py-1 rounded-md font-semibold transition-colors"
              :class="filtroTipo === 'ingreso' ? 'bg-white shadow text-emerald-600' : 'text-gray-500 hover:text-gray-700'">
              Ingresos
            </button>
            <button @click="filtroTipo = 'egreso'; cargarMovimientos()"
              class="text-xs px-3 py-1 rounded-md font-semibold transition-colors"
              :class="filtroTipo === 'egreso' ? 'bg-white shadow text-red-500' : 'text-gray-500 hover:text-gray-700'">
              Egresos
            </button>
          </div>
          <!-- Filtro método de pago -->
          <div class="flex items-center gap-1 bg-gray-100 p-1 rounded-lg">
            <button @click="filtroMetodo = null"
              class="text-xs px-3 py-1 rounded-md font-semibold transition-colors"
              :class="filtroMetodo === null ? 'bg-white shadow text-gray-800' : 'text-gray-500 hover:text-gray-700'">
              Todos
            </button>
            <button @click="filtroMetodo = 'efectivo'"
              class="text-xs px-3 py-1 rounded-md font-semibold transition-colors flex items-center gap-1"
              :class="filtroMetodo === 'efectivo' ? 'bg-white shadow text-amber-600' : 'text-gray-500 hover:text-gray-700'">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
              Efectivo
            </button>
            <button @click="filtroMetodo = 'transferencia'"
              class="text-xs px-3 py-1 rounded-md font-semibold transition-colors flex items-center gap-1"
              :class="filtroMetodo === 'transferencia' ? 'bg-white shadow text-blue-600' : 'text-gray-500 hover:text-gray-700'">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z"/></svg>
              Transferencia
            </button>
          </div>
        </div>
      </div>

      <div v-if="cargandoMovimientos" class="p-12 text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600 mx-auto"></div>
      </div>

      <div v-else-if="movimientosFiltrados.length === 0" class="p-12 text-center text-gray-400">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-200 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
        Sin movimientos en este período.
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-100">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-5 py-3 text-left text-xs font-bold text-gray-400 uppercase tracking-wider">Fecha</th>
              <th class="px-5 py-3 text-left text-xs font-bold text-gray-400 uppercase tracking-wider">Tipo</th>
              <th class="px-5 py-3 text-left text-xs font-bold text-gray-400 uppercase tracking-wider">Concepto</th>
              <th class="px-5 py-3 text-left text-xs font-bold text-gray-400 uppercase tracking-wider">Categoría</th>
              <th class="px-5 py-3 text-left text-xs font-bold text-gray-400 uppercase tracking-wider">Método</th>
              <th class="px-5 py-3 text-right text-xs font-bold text-gray-400 uppercase tracking-wider">Monto</th>
              <th class="px-5 py-3"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="m in movimientosFiltrados" :key="m.id" class="hover:bg-gray-50 transition-colors group">
              <td class="px-5 py-3.5 whitespace-nowrap text-sm text-gray-500">
                {{ formatFecha(m.fecha) }}
              </td>
              <td class="px-5 py-3.5 whitespace-nowrap">
                <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold"
                  :class="m.tipo === 'ingreso'
                    ? 'bg-emerald-100 text-emerald-700'
                    : 'bg-red-100 text-red-600'">
                  <span class="w-1.5 h-1.5 rounded-full"
                    :class="m.tipo === 'ingreso' ? 'bg-emerald-500' : 'bg-red-500'"></span>
                  {{ m.tipo === 'ingreso' ? 'Ingreso' : 'Egreso' }}
                </span>
              </td>
              <td class="px-5 py-3.5 text-sm text-gray-800 max-w-[260px]">
                <p class="font-medium truncate">{{ m.concepto }}</p>
                <p v-if="m.usuario_nombre" class="text-xs text-gray-400 truncate">{{ m.usuario_nombre }}</p>
              </td>
              <td class="px-5 py-3.5 whitespace-nowrap">
                <span class="text-xs px-2.5 py-1 rounded-full font-medium"
                  :class="colorCategoria(m.categoria)">
                  {{ labelCategoria(m.categoria) }}
                </span>
              </td>
              <td class="px-5 py-3.5 whitespace-nowrap text-sm text-gray-500 capitalize">
                {{ m.metodo_pago || '—' }}
              </td>
              <td class="px-5 py-3.5 whitespace-nowrap text-right font-bold text-sm"
                :class="m.tipo === 'ingreso' ? 'text-emerald-600' : 'text-red-500'">
                {{ m.tipo === 'ingreso' ? '+' : '−' }}{{ formatMoneda(m.monto) }}
              </td>
              <td class="px-5 py-3.5 whitespace-nowrap text-right">
                <button v-if="m.es_eliminable" @click="eliminarMovimiento(m)"
                  class="opacity-0 group-hover:opacity-100 p-1.5 text-gray-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ── Modal nuevo movimiento ── -->
    <div v-if="mostrarModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b border-gray-100 flex items-center justify-between">
          <h3 class="text-lg font-bold text-gray-800">Registrar egreso</h3>
          <button @click="cerrarModal" class="p-2 rounded-lg hover:bg-gray-100 text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="guardarMovimiento" class="p-6 space-y-4">

          <!-- Categoría -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">Categoría</label>
            <select v-model="form.categoria" required
              class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none">
              <option value="" disabled>Selecciona una categoría</option>
              <option value="renta">Renta del local</option>
              <option value="servicios">Servicios (luz, agua, internet)</option>
              <option value="equipamiento">Equipamiento</option>
              <option value="nomina">Nómina / Salarios</option>
              <option value="marketing">Marketing y publicidad</option>
              <option value="mantenimiento">Mantenimiento</option>
              <option value="otros">Otros gastos</option>
            </select>
          </div>

          <!-- Concepto -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">Concepto</label>
            <input v-model="form.concepto" type="text" required
              placeholder="Ej: Pago de renta mayo 2026"
              class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none">
          </div>

          <!-- Monto y Fecha -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1.5">Monto ($)</label>
              <input v-model.number="form.monto" type="number" min="1" step="any" required
                placeholder="Ej: 150000"
                class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none">
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1.5">Fecha</label>
              <input v-model="form.fecha" type="date" required
                class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none">
            </div>
          </div>

          <!-- Método de pago -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">Método de pago</label>
            <div class="grid grid-cols-3 gap-2">
              <label v-for="m in metodos" :key="m.value"
                class="flex items-center justify-center py-2 rounded-lg border-2 cursor-pointer transition-all text-sm font-semibold"
                :class="form.metodo_pago === m.value
                  ? 'border-red-500 bg-red-50 text-red-700'
                  : 'border-gray-200 text-gray-500 hover:border-gray-300'">
                <input type="radio" v-model="form.metodo_pago" :value="m.value" class="sr-only">
                {{ m.label }}
              </label>
            </div>
          </div>

          <!-- Notas -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">
              Notas <span class="text-gray-400 font-normal">(opcional)</span>
            </label>
            <textarea v-model="form.notas" rows="2"
              class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none resize-none text-sm"
              placeholder="Observaciones adicionales..."></textarea>
          </div>

          <div v-if="errorGuardar" class="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg p-3">
            {{ errorGuardar }}
          </div>

          <div class="flex gap-3 pt-2">
            <button type="button" @click="cerrarModal"
              class="flex-1 py-2.5 rounded-xl border border-gray-300 text-gray-600 font-semibold hover:bg-gray-50 transition-colors">
              Cancelar
            </button>
            <button type="submit" :disabled="guardando"
              class="flex-1 py-2.5 rounded-xl font-bold text-white transition-colors disabled:opacity-50 flex items-center justify-center gap-2 bg-red-500 hover:bg-red-600">
              <span v-if="guardando" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
              {{ guardando ? 'Guardando...' : 'Registrar egreso' }}
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../api'

// ── Estado ───────────────────────────────────────────────────
const balance = ref({ ingresos_total: 0, total_membresias: 0, total_tienda: 0, egresos_total: 0, balance_neto: 0, ingresos_por_categoria: {}, egresos_por_categoria: {} })
const movimientos = ref([])
const cargandoBalance = ref(true)
const cargandoMovimientos = ref(true)
const filtroTipo = ref(null)
const filtroMetodo = ref(null)
const mostrarModal = ref(false)
const guardando = ref(false)
const errorGuardar = ref('')

// ── Período ──────────────────────────────────────────────────
const periodoActivo = ref('mes')
const rangoDesde = ref('')
const rangoHasta = ref('')

const periodos = [
  { key: 'hoy', label: 'Hoy' },
  { key: 'semana', label: 'Esta semana' },
  { key: 'mes', label: 'Este mes' },
  { key: 'anio', label: 'Este año' },
  { key: 'todo', label: 'Todo' },
  { key: 'rango', label: 'Rango' },
]

const labelPeriodo = computed(() => {
  return periodos.find(p => p.key === periodoActivo.value)?.label || ''
})

function calcularFechas() {
  const hoy = new Date()
  const fmt = (d) => d.toISOString().slice(0, 10)
  switch (periodoActivo.value) {
    case 'hoy':
      return { desde: fmt(hoy), hasta: fmt(hoy) }
    case 'semana': {
      const lunes = new Date(hoy)
      lunes.setDate(hoy.getDate() - hoy.getDay() + 1)
      const domingo = new Date(lunes)
      domingo.setDate(lunes.getDate() + 6)
      return { desde: fmt(lunes), hasta: fmt(domingo) }
    }
    case 'mes':
      return {
        desde: fmt(new Date(hoy.getFullYear(), hoy.getMonth(), 1)),
        hasta: fmt(new Date(hoy.getFullYear(), hoy.getMonth() + 1, 0)),
      }
    case 'anio':
      return {
        desde: `${hoy.getFullYear()}-01-01`,
        hasta: `${hoy.getFullYear()}-12-31`,
      }
    case 'rango':
      return { desde: rangoDesde.value || null, hasta: rangoHasta.value || null }
    default:
      return { desde: null, hasta: null }
  }
}

function seleccionarPeriodo(key) {
  periodoActivo.value = key
  if (key !== 'rango') cargarTodo()
}

// ── Fetch ─────────────────────────────────────────────────────
async function cargarBalance() {
  cargandoBalance.value = true
  const { desde, hasta } = calcularFechas()
  const params = {}
  if (desde) params.fecha_desde = desde
  if (hasta) params.fecha_hasta = hasta
  try {
    const { data } = await api.get('/finanzas/balance', { params })
    balance.value = data
  } catch (e) {
    console.error(e)
  } finally {
    cargandoBalance.value = false
  }
}

async function cargarMovimientos() {
  cargandoMovimientos.value = true
  const { desde, hasta } = calcularFechas()
  const params = { limit: 200 }
  if (desde) params.fecha_desde = desde
  if (hasta) params.fecha_hasta = hasta
  if (filtroTipo.value) params.tipo = filtroTipo.value
  try {
    const { data } = await api.get('/finanzas/movimientos', { params })
    movimientos.value = data
  } catch (e) {
    console.error(e)
  } finally {
    cargandoMovimientos.value = false
  }
}

const movimientosFiltrados = computed(() => {
  return movimientos.value.filter(m => {
    if (filtroMetodo.value && m.metodo_pago !== filtroMetodo.value) return false
    return true
  })
})

function cargarTodo() {
  cargarBalance()
  cargarMovimientos()
}

// ── Formulario ────────────────────────────────────────────────
const metodos = [
  { value: 'efectivo', label: 'Efectivo' },
  { value: 'transferencia', label: 'Transferencia' },
]

const formVacio = () => ({
  tipo: 'egreso',
  concepto: '',
  categoria: '',
  monto: '',
  fecha: new Date().toISOString().slice(0, 10),
  metodo_pago: 'efectivo',
  notas: '',
})

const form = ref(formVacio())

function abrirModal() {
  form.value = formVacio()
  errorGuardar.value = ''
  mostrarModal.value = true
}

function cerrarModal() { mostrarModal.value = false }

async function guardarMovimiento() {
  guardando.value = true
  errorGuardar.value = ''
  try {
    await api.post('/finanzas/movimientos', {
      tipo: form.value.tipo,
      concepto: form.value.concepto,
      categoria: form.value.categoria,
      monto: form.value.monto,
      fecha: new Date(form.value.fecha).toISOString(),
      metodo_pago: form.value.metodo_pago || null,
      notas: form.value.notas || null,
    })
    cerrarModal()
    cargarTodo()
  } catch (e) {
    errorGuardar.value = e.response?.data?.detail || 'Error al guardar el movimiento.'
  } finally {
    guardando.value = false
  }
}

async function eliminarMovimiento(m) {
  const idNum = m.id.replace('mov_', '')
  if (!confirm(`¿Eliminar este movimiento?\n${m.concepto} · ${formatMoneda(m.monto)}`)) return
  try {
    await api.delete(`/finanzas/movimientos/${idNum}`)
    cargarTodo()
  } catch (e) {
    alert(e.response?.data?.detail || 'Error al eliminar.')
  }
}

// ── Helpers ───────────────────────────────────────────────────
const LABELS_CATEGORIA = {
  mensualidad: 'Membresía',
  venta_tienda: 'Tienda',
  ingreso_varios: 'Varios',
  renta: 'Renta',
  servicios: 'Servicios',
  equipamiento: 'Equipamiento',
  nomina: 'Nómina',
  marketing: 'Marketing',
  mantenimiento: 'Mantenimiento',
  otros: 'Otros',
}

const COLORES_CATEGORIA = {
  mensualidad: 'bg-red-100 text-red-700',
  venta_tienda: 'bg-blue-100 text-blue-700',
  ingreso_varios: 'bg-teal-100 text-teal-700',
  renta: 'bg-orange-100 text-orange-700',
  servicios: 'bg-yellow-100 text-yellow-700',
  equipamiento: 'bg-purple-100 text-purple-700',
  nomina: 'bg-pink-100 text-pink-700',
  marketing: 'bg-cyan-100 text-cyan-700',
  mantenimiento: 'bg-amber-100 text-amber-700',
  otros: 'bg-gray-100 text-gray-600',
}

const labelCategoria = (cat) => LABELS_CATEGORIA[cat] || cat
const colorCategoria = (cat) => COLORES_CATEGORIA[cat] || 'bg-gray-100 text-gray-600'

const formatMoneda = (v) =>
  new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(v || 0)

const formatFecha = (f) =>
  new Date(f).toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })

onMounted(cargarTodo)
</script>

<style>
.animate-fade-in-up {
  animation: fadeInUp 0.4s ease-out;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
