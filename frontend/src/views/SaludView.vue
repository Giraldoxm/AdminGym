<template>
  <div class="animate-fade-in-up">

    <!-- Header -->
    <div class="mb-6">
      <h2 class="text-3xl font-extrabold text-gray-900 tracking-tight">Mi Salud</h2>
      <p class="text-gray-500 mt-1">Selecciona una medida para registrar y ver su evolución</p>
    </div>

    <!-- Skeletons -->
    <div v-if="cargando" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
      <div v-for="i in 5" :key="i" class="bg-gray-100 rounded-2xl h-36 animate-pulse"></div>
    </div>

    <template v-else>

      <!-- Banner IMC -->
      <div v-if="imcActual" class="rounded-2xl p-5 shadow-sm border mb-6" :class="imcInfo(imcActual).colorFondo">
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1">
            <p class="text-xs font-bold uppercase tracking-widest mb-1" :class="imcInfo(imcActual).colorTexto">
              Índice de Masa Corporal
            </p>
            <div class="flex items-end gap-3">
              <p class="text-4xl font-black" :class="imcInfo(imcActual).colorTexto">{{ imcActual }}</p>
              <span class="text-sm font-bold mb-1 px-2.5 py-0.5 rounded-full" :class="imcInfo(imcActual).badge">
                {{ imcInfo(imcActual).categoria }}
              </span>
            </div>
            <div class="mt-3 h-2 bg-white/40 rounded-full overflow-hidden max-w-xs">
              <div class="h-full rounded-full transition-all duration-700" :class="imcInfo(imcActual).colorBarra"
                :style="{ width: Math.min(((imcActual - 10) / 30) * 100, 100) + '%' }">
              </div>
            </div>
            <div class="flex justify-between text-xs mt-1 font-medium opacity-70 max-w-xs"
              :class="imcInfo(imcActual).colorTexto">
              <span>Bajo</span><span>Normal</span><span>Sobrepeso</span><span>Obesidad</span>
            </div>
          </div>
          <div class="text-right text-sm shrink-0 opacity-70" :class="imcInfo(imcActual).colorTexto">
            <p>{{ ultimoPeso }} kg</p>
            <p>{{ ultimaAltura }} cm</p>
          </div>
        </div>
      </div>

      <!-- Grid de tarjetas de navegación -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        <RouterLink
          v-for="tipo in TIPOS_SALUD"
          :key="tipo.param"
          :to="`/salud/${tipo.param}`"
          class="bg-white rounded-2xl border shadow-sm overflow-hidden hover:shadow-md transition-shadow group"
          :class="tipo.colorBorder">

          <!-- Cabecera coloreada -->
          <div class="px-5 py-4" :class="tipo.colorBg">
            <div class="flex items-center justify-between">
              <p class="text-xs font-bold uppercase tracking-widest" :class="tipo.colorText">
                {{ tipo.label }}
              </p>
              <svg xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 opacity-40 group-hover:opacity-80 group-hover:translate-x-0.5 transition-all"
                :class="tipo.colorText"
                fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
              </svg>
            </div>
            <p class="text-3xl font-black mt-1 leading-none"
              :class="ultimoValor(tipo.key) !== null ? 'text-gray-900' : 'text-gray-300'">
              <template v-if="ultimoValor(tipo.key) !== null">
                {{ ultimoValor(tipo.key) }}<span class="text-base font-semibold text-gray-400 ml-1">{{ tipo.unidad }}</span>
              </template>
              <template v-else>—</template>
            </p>
            <p v-if="deltaDe(tipo.key) !== null" class="text-xs font-semibold mt-1">
              <template v-if="deltaDe(tipo.key) > 0">
                <span class="text-red-500">↑ {{ Math.abs(deltaDe(tipo.key)) }} {{ tipo.unidad }} vs anterior</span>
              </template>
              <template v-else-if="deltaDe(tipo.key) < 0">
                <span class="text-emerald-600">↓ {{ Math.abs(deltaDe(tipo.key)) }} {{ tipo.unidad }} vs anterior</span>
              </template>
              <template v-else>
                <span class="text-gray-400">Sin cambio</span>
              </template>
            </p>
          </div>

          <!-- Pie de tarjeta -->
          <div class="px-5 py-3 flex items-center justify-between">
            <span class="text-xs text-gray-400">
              {{ conteo(tipo.key) }} registro{{ conteo(tipo.key) !== 1 ? 's' : '' }}
            </span>
            <span class="text-xs font-semibold" :class="tipo.colorText">
              Ver historial y gráfica →
            </span>
          </div>

        </RouterLink>
      </div>

    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import api from '../api'
import { TIPOS_SALUD } from '../data/saludTipos'

const medidas  = ref([])
const cargando = ref(true)

const formatFecha = (f) =>
  new Date(f + 'T12:00:00').toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })

function ultimoValor(key) {
  const lista = medidas.value.filter(m => m[key] != null)
  return lista.length ? lista[lista.length - 1][key] : null
}

function deltaDe(key) {
  const lista = medidas.value.filter(m => m[key] != null)
  if (lista.length < 2) return null
  return Math.round((lista[lista.length - 1][key] - lista[lista.length - 2][key]) * 10) / 10
}

function conteo(key) {
  return medidas.value.filter(m => m[key] != null).length
}

const ultimoPeso   = computed(() => ultimoValor('peso_kg'))
const ultimaAltura = computed(() => ultimoValor('altura_cm'))
const imcActual    = computed(() => {
  if (!ultimoPeso.value || !ultimaAltura.value) return null
  const h = ultimaAltura.value / 100
  return Math.round(ultimoPeso.value / (h * h) * 10) / 10
})

function imcInfo(imc) {
  if (imc < 18.5) return { categoria: 'Bajo peso',  colorTexto: 'text-blue-700',    colorFondo: 'bg-blue-50 border-blue-100',       badge: 'bg-blue-100 text-blue-700',       colorBarra: 'bg-blue-400'    }
  if (imc < 25)   return { categoria: 'Normal',      colorTexto: 'text-emerald-700', colorFondo: 'bg-emerald-50 border-emerald-100', badge: 'bg-emerald-100 text-emerald-700', colorBarra: 'bg-emerald-400' }
  if (imc < 30)   return { categoria: 'Sobrepeso',   colorTexto: 'text-amber-700',   colorFondo: 'bg-amber-50 border-amber-100',     badge: 'bg-amber-100 text-amber-700',     colorBarra: 'bg-amber-400'   }
  return           { categoria: 'Obesidad',    colorTexto: 'text-red-700',     colorFondo: 'bg-red-50 border-red-100',         badge: 'bg-red-100 text-red-700',         colorBarra: 'bg-red-400'     }
}

async function cargar() {
  cargando.value = true
  try {
    const { data } = await api.get('/salud/')
    medidas.value = data
  } finally {
    cargando.value = false
  }
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
