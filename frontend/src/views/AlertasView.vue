<template>
  <div class="animate-fade-in-up">

    <!-- Header -->
    <div class="mb-6">
      <h2 class="text-3xl font-extrabold text-gray-900 tracking-tight">Alertas WhatsApp</h2>
      <p class="text-gray-500 mt-1">Recordatorios de vencimiento de membresía</p>
    </div>

    <!-- Toast -->
    <Transition enter-from-class="opacity-0 translate-y-4" enter-active-class="transition-all duration-300" leave-to-class="opacity-0 translate-y-4" leave-active-class="transition-all duration-300">
      <div v-if="toast" class="fixed bottom-6 right-6 bg-gray-900 text-white px-5 py-3 rounded-xl shadow-2xl flex items-center gap-3 z-50">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-emerald-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
        </svg>
        <span class="text-sm font-semibold">{{ toast }}</span>
      </div>
    </Transition>

    <!-- Filtro tabs -->
    <div class="flex gap-1 bg-gray-100 p-1 rounded-xl w-fit mb-6">
      <button @click="filtro = 'pendientes'; cargar()"
        class="px-5 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2"
        :class="filtro === 'pendientes' ? 'bg-white shadow text-gray-900' : 'text-gray-500 hover:text-gray-700'">
        Pendientes
        <span v-if="pendientesCount > 0" class="bg-red-500 text-white text-xs font-black px-1.5 py-0.5 rounded-full">{{ pendientesCount }}</span>
      </button>
      <button @click="filtro = 'todas'; cargar()"
        class="px-5 py-2 rounded-lg text-sm font-bold transition-all"
        :class="filtro === 'todas' ? 'bg-white shadow text-gray-900' : 'text-gray-500 hover:text-gray-700'">
        Historial
      </button>
    </div>

    <!-- Loading -->
    <div v-if="cargando" class="grid gap-4">
      <div v-for="i in 3" :key="i" class="bg-white rounded-2xl h-24 animate-pulse border border-gray-100"></div>
    </div>

    <!-- Vacío -->
    <div v-else-if="alertas.length === 0"
      class="bg-gray-50 border-2 border-dashed border-gray-200 rounded-2xl p-14 text-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-14 w-14 mx-auto text-gray-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
      </svg>
      <p class="text-gray-500 font-semibold">
        {{ filtro === 'pendientes' ? 'No hay alertas pendientes' : 'No hay historial de alertas' }}
      </p>
      <p class="text-gray-400 text-sm mt-1">
        {{ filtro === 'pendientes' ? 'Ninguna membresía vence en los próximos 7 días o los usuarios no tienen WhatsApp registrado.' : '' }}
      </p>
    </div>

    <!-- Lista de alertas -->
    <div v-else class="space-y-3">
      <!-- Pendientes: agrupadas por días_anticipacion -->
      <template v-if="filtro === 'pendientes'">
        <template v-for="grupo in alertasAgrupadas" :key="grupo.dias">
          <div class="flex items-center gap-3 mt-5 mb-2 first:mt-0">
            <span class="text-xs font-black uppercase tracking-widest px-3 py-1 rounded-full"
              :class="grupo.dias === 1 ? 'bg-red-100 text-red-700' : grupo.dias === 3 ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700'">
              {{ grupo.dias === 1 ? '⚠ Vence mañana' : `Vence en ${grupo.dias} días` }}
            </span>
            <div class="flex-1 h-px bg-gray-100"></div>
            <span class="text-xs text-gray-400">{{ grupo.items.length }} usuario{{ grupo.items.length !== 1 ? 's' : '' }}</span>
          </div>

          <div v-for="alerta in grupo.items" :key="alerta.id"
            class="bg-white rounded-2xl border shadow-sm p-5 flex items-center gap-4 transition-all"
            :class="grupo.dias === 1 ? 'border-red-100' : grupo.dias === 3 ? 'border-amber-100' : 'border-blue-100'">

            <div class="w-11 h-11 rounded-full flex-shrink-0 flex items-center justify-center text-white font-bold text-sm"
              :class="grupo.dias === 1 ? 'bg-red-500' : grupo.dias === 3 ? 'bg-amber-500' : 'bg-blue-500'">
              {{ alerta.usuario_nombre.charAt(0).toUpperCase() }}
            </div>

            <div class="flex-1 min-w-0">
              <p class="font-bold text-gray-800 truncate">{{ alerta.usuario_nombre }}</p>
              <div class="flex items-center gap-3 mt-0.5">
                <p class="text-sm text-gray-500">
                  Vence el <span class="font-semibold">{{ formatFecha(alerta.fecha_vencimiento) }}</span>
                </p>
                <span v-if="alerta.usuario_telefono" class="text-xs text-gray-400 flex items-center gap-1">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                  </svg>
                  {{ alerta.usuario_telefono }}
                </span>
                <span v-else class="text-xs text-red-400">Sin teléfono</span>
              </div>
            </div>

            <div class="flex items-center gap-2 flex-shrink-0">
              <a v-if="alerta.usuario_telefono"
                :href="whatsappLink(alerta)"
                target="_blank"
                @click="marcarEnviada(alerta)"
                class="flex items-center gap-2 bg-green-500 hover:bg-green-600 text-white text-sm font-bold px-4 py-2 rounded-xl transition-colors shadow-sm">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/>
                  <path d="M12 0C5.373 0 0 5.373 0 12c0 2.123.554 4.118 1.523 5.847L.057 23.888a.75.75 0 00.918.918l6.041-1.466A11.946 11.946 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 21.75a9.725 9.725 0 01-4.964-1.359l-.356-.213-3.692.896.913-3.578-.233-.369A9.718 9.718 0 012.25 12C2.25 6.615 6.615 2.25 12 2.25S21.75 6.615 21.75 12 17.385 21.75 12 21.75z"/>
                </svg>
                Enviar
              </a>
              <button @click="descartar(alerta)" title="Descartar"
                class="p-2 text-gray-300 hover:text-red-400 hover:bg-red-50 rounded-lg transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
          </div>
        </template>
      </template>

      <!-- Historial: solo enviadas, sin agrupar -->
      <template v-else>
        <div v-for="alerta in alertasEnviadas" :key="alerta.id"
          class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 flex items-center gap-4">
          <div class="w-11 h-11 rounded-full flex-shrink-0 flex items-center justify-center text-white font-bold text-sm bg-emerald-500">
            {{ alerta.usuario_nombre.charAt(0).toUpperCase() }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-bold text-gray-800 truncate">{{ alerta.usuario_nombre }}</p>
            <div class="flex items-center gap-3 mt-0.5 flex-wrap">
              <p class="text-sm text-gray-500">
                Vencía el <span class="font-semibold">{{ formatFecha(alerta.fecha_vencimiento) }}</span>
              </p>
              <span v-if="alerta.usuario_telefono" class="text-xs text-gray-400 flex items-center gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                </svg>
                {{ alerta.usuario_telefono }}
              </span>
            </div>
            <p v-if="alerta.fecha_enviada" class="text-xs text-emerald-600 mt-0.5">
              ✓ Enviada el {{ formatFechaHora(alerta.fecha_enviada) }}
            </p>
          </div>
          <span class="text-sm text-emerald-600 font-semibold flex items-center gap-1 flex-shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
            Enviada
          </span>
        </div>

        <div v-if="alertasEnviadas.length === 0"
          class="bg-gray-50 border-2 border-dashed border-gray-200 rounded-2xl p-14 text-center">
          <p class="text-gray-500 font-semibold">Aún no has enviado ningún recordatorio</p>
        </div>
      </template>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'

const alertas = ref([])
const cargando = ref(true)
const filtro = ref('pendientes')
const toast = ref('')
const pendientesCount = ref(0)

// ── Agrupadas por días (solo pendientes) ──────────────────────
const alertasAgrupadas = computed(() => {
  const grupos = {}
  for (const a of alertas.value) {
    if (a.enviada) continue
    if (!grupos[a.dias_anticipacion]) grupos[a.dias_anticipacion] = []
    grupos[a.dias_anticipacion].push(a)
  }
  return Object.entries(grupos)
    .sort(([a], [b]) => Number(a) - Number(b))
    .map(([dias, items]) => ({ dias: Number(dias), items }))
})

// ── Solo enviadas, ordenadas por fecha de envío descendente ───
const alertasEnviadas = computed(() =>
  alertas.value
    .filter(a => a.enviada)
    .sort((a, b) => new Date(b.fecha_enviada || 0) - new Date(a.fecha_enviada || 0))
)

// ── Fetch ─────────────────────────────────────────────────────
async function cargar() {
  cargando.value = true
  try {
    await api.post('/alertas/generar')
    const soloP = filtro.value === 'pendientes'
    const [resAlertas, resContar] = await Promise.all([
      api.get('/alertas/', { params: { solo_pendientes: soloP } }),
      api.get('/alertas/contar'),
    ])
    alertas.value = resAlertas.data
    pendientesCount.value = resContar.data.pendientes
  } finally {
    cargando.value = false
  }
}

async function marcarEnviada(alerta) {
  try {
    await api.post(`/alertas/${alerta.id}/marcar-enviada`)
    alerta.enviada = true
    pendientesCount.value = Math.max(0, pendientesCount.value - 1)
    mostrarToast(`Recordatorio enviado a ${alerta.usuario_nombre}`)
  } catch { /* silencioso */ }
}

async function descartar(alerta) {
  if (!confirm(`¿Descartar la alerta de ${alerta.usuario_nombre}?`)) return
  try {
    await api.delete(`/alertas/${alerta.id}`)
    await cargar()
  } catch (e) {
    alert(e.response?.data?.detail || 'Error.')
  }
}

// ── WhatsApp link ─────────────────────────────────────────────
function whatsappLink(alerta) {
  const tel = alerta.usuario_telefono.replace(/\D/g, '')
  const numero = tel.length === 10 ? '57' + tel : tel
  const dias = alerta.dias_anticipacion
  const fecha = formatFecha(alerta.fecha_vencimiento)
  const msg =
    `Hola ${alerta.usuario_nombre}! 👋 Te recordamos que tu membresía en *Jain Sport Box* vence ` +
    (dias === 1 ? `*mañana* (${fecha})` : `en *${dias} días* (${fecha})`) +
    `. Para renovar contáctanos. 💪🔥`
  return `https://wa.me/${numero}?text=${encodeURIComponent(msg)}`
}

// ── Helpers ───────────────────────────────────────────────────
const formatFecha = (f) =>
  new Date(f + 'T12:00:00').toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })

const formatFechaHora = (f) =>
  new Date(f).toLocaleDateString('es-CO', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })

function mostrarToast(msg) {
  toast.value = msg
  setTimeout(() => { toast.value = '' }, 3500)
}

onMounted(cargar)
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
