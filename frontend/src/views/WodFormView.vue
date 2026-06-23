<template>
  <div class="animate-fade-in-up">
    <!-- Header -->
    <div class="flex items-start gap-4 mb-8">
      <button
        type="button"
        @click="volver"
        class="mt-1 p-2 rounded-lg hover:bg-gray-100 text-gray-400 transition-colors flex-shrink-0"
        title="Volver"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <div class="flex-1 min-w-0">
        <h2 class="text-3xl font-black text-gray-800 tracking-tight">
          {{ modoEdicion ? 'Editar WOD' : (esPersonalizado ? 'Nuevo WOD Personalizado' : 'Nuevo WOD') }}
        </h2>
        <p class="text-gray-500 mt-1">
          {{ esPersonalizado ? 'Programación específica por género' : 'Workout of the Day' }}
        </p>
      </div>
      <button
        type="button"
        @click="guardar"
        :disabled="guardando"
        class="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white font-bold py-2.5 px-6 rounded-lg shadow transition-colors disabled:bg-red-300 flex-shrink-0"
      >
        <span v-if="guardando" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
        {{ guardando ? 'Guardando...' : (modoEdicion ? 'Actualizar WOD' : 'Crear WOD') }}
      </button>
    </div>

    <!-- Error -->
    <div v-if="errorForm" class="mb-6 bg-red-50 text-red-700 text-sm p-4 rounded-xl border border-red-100 font-medium">
      {{ errorForm }}
    </div>

    <!-- Skeleton cargando (modo edición sin state) -->
    <div v-if="cargando" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="space-y-5">
        <div v-for="i in 4" :key="i" class="bg-gray-100 rounded-2xl animate-pulse" :style="`height:${i===3?120:72}px`" />
      </div>
      <div class="bg-gray-100 rounded-2xl animate-pulse h-80" />
    </div>

    <!-- Form -->
    <form v-else @submit.prevent="guardar" class="space-y-5">

      <!-- Fila 1: género (solo personalizados) -->
      <div v-if="esPersonalizado" class="bg-white rounded-2xl border border-gray-100 p-6">
        <p class="text-sm font-semibold text-gray-700 mb-3">
          Género destino
          <span v-if="!modoEdicion" class="text-gray-400 font-normal">(puedes elegir ambos)</span>
        </p>
        <div v-if="modoEdicion">
          <span
            class="inline-block text-sm font-bold px-4 py-2 rounded-full"
            :class="form.genero_destino === 'masculino' ? 'bg-red-100 text-red-700' : 'bg-gray-200 text-gray-700'"
          >
            {{ form.genero_destino === 'masculino' ? 'Masculino' : 'Femenino' }}
          </span>
        </div>
        <div v-else class="flex gap-3">
          <button
            type="button"
            @click="generos.masculino = !generos.masculino"
            class="flex-1 py-3 px-4 rounded-xl border-2 font-bold text-sm transition-all flex items-center justify-center gap-2"
            :class="generos.masculino ? 'border-red-500 bg-red-50 text-red-700 shadow-sm' : 'border-gray-200 text-gray-400 hover:border-gray-300'"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            Masculino
          </button>
          <button
            type="button"
            @click="generos.femenino = !generos.femenino"
            class="flex-1 py-3 px-4 rounded-xl border-2 font-bold text-sm transition-all flex items-center justify-center gap-2"
            :class="generos.femenino ? 'border-gray-700 bg-gray-700 text-white shadow-sm' : 'border-gray-200 text-gray-400 hover:border-gray-300'"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            Femenino
          </button>
        </div>
      </div>

      <!-- Fila 2: título + fecha en fila -->
      <div class="flex flex-col sm:flex-row gap-5">
        <div class="bg-white rounded-2xl border border-gray-100 p-6 flex-1">
          <label class="block text-sm font-semibold text-gray-700 mb-2">Título</label>
          <input
            v-model="form.titulo"
            type="text"
            required
            autofocus
            placeholder="Ej: AMRAP 20 min"
            class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all text-base font-semibold"
          />
        </div>
        <div class="bg-white rounded-2xl border border-gray-100 p-6 sm:w-52">
          <label class="block text-sm font-semibold text-gray-700 mb-2">Fecha</label>
          <input
            v-model="form.fecha"
            type="date"
            required
            class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all"
          />
        </div>
      </div>

      <!-- Fila 2b: tipo de WOD -->
      <div class="flex flex-col sm:flex-row gap-5">
        <div class="bg-white rounded-2xl border border-gray-100 p-6 flex-1">
          <label class="block text-sm font-semibold text-gray-700 mb-2">
            Tipo de WOD <span class="text-gray-400 font-normal">(opcional)</span>
          </label>
          <select
            v-model="form.tipo"
            class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all bg-white text-sm"
          >
            <option value="">Sin especificar</option>
            <option value="For Time">For Time</option>
            <option value="AMRAP">AMRAP</option>
            <option value="EMOM">EMOM</option>
            <option value="Por Rondas">Por Rondas</option>
            <option value="Fuerza">Fuerza</option>
            <option value="Otro">Otro</option>
          </select>
        </div>
      </div>

      <!-- Fila 3: descripción -->
      <div class="bg-white rounded-2xl border border-gray-100 p-6">
        <label class="block text-sm font-semibold text-gray-700 mb-2">
          Descripción / Notas generales
          <span class="text-gray-400 font-normal">(opcional)</span>
        </label>
        <textarea
          v-model="form.descripcion"
          rows="4"
          placeholder="Ej: AMRAP 20 min. Escala según nivel. Descansa lo necesario entre series."
          class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all resize-none text-sm leading-relaxed"
        />
      </div>

      <!-- Fila 4: toggle visible -->
      <div class="bg-white rounded-2xl border border-gray-100 p-6 flex items-center justify-between gap-4">
        <div>
          <p class="font-semibold text-gray-800">Visible para clientes</p>
          <p class="text-sm text-gray-400 mt-0.5">Los clientes podrán ver este WOD en su pantalla</p>
        </div>
        <button
          type="button"
          @click="form.activo = !form.activo"
          class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none flex-shrink-0"
          :class="form.activo ? 'bg-green-500' : 'bg-gray-300'"
        >
          <span
            class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform"
            :class="form.activo ? 'translate-x-6' : 'translate-x-1'"
          />
        </button>
      </div>

      <!-- Fila 5: ejercicios (ancho completo) -->
      <div class="bg-white rounded-2xl border border-gray-100 p-6">
        <WodEjerciciosEditor v-model="form.ejercicios" :catalogo="catalogo" />
      </div>

      <!-- Botones al pie -->
      <div class="flex gap-3 pt-1">
        <button
          type="button"
          @click="volver"
          class="py-3 px-6 rounded-xl border border-gray-300 text-gray-600 font-semibold hover:bg-gray-50 transition-colors"
        >
          Cancelar
        </button>
        <button
          type="submit"
          :disabled="guardando"
          class="flex-1 py-3 rounded-xl bg-red-600 hover:bg-red-700 text-white font-bold transition-colors disabled:bg-red-300 flex items-center justify-center gap-2"
        >
          <span v-if="guardando" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
          {{ guardando ? 'Guardando...' : (modoEdicion ? 'Actualizar WOD' : 'Crear WOD') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'
import WodEjerciciosEditor from '../components/WodEjerciciosEditor.vue'

const route  = useRoute()
const router = useRouter()

const esPersonalizado = computed(() => !!route.meta.personalizado)
const modoEdicion     = computed(() => !!route.params.id)

const cargando   = ref(modoEdicion.value && !history.state?.wod)
const guardando  = ref(false)
const errorForm  = ref('')
const catalogo   = ref([])

const hoyISO = new Date().toISOString().slice(0, 10)

const form = ref({
  titulo: '',
  descripcion: '',
  fecha: hoyISO,
  activo: true,
  genero_destino: '',
  tipo: '',
  ejercicios: [],
})

// Para creación de personalizados: selección múltiple de géneros
const generos = ref({ masculino: true, femenino: true })

function volver() {
  router.push(esPersonalizado.value ? '/wods/personalizados' : '/wods')
}

function _mapEjercicio(e) {
  return {
    ejercicio_id:    e.ejercicio_id,
    nombre:          e.nombre,
    video_url:       e.video_url,
    descripcion:     e.descripcion || null,
    notas:           e.notas || '',
    rep_min:         e.rep_min         ?? null,
    rep_max:         e.rep_max         ?? null,
    rir:             e.rir             ?? null,
    porcentaje_rm:   e.porcentaje_rm   ?? null,
    tiempo_segundos: e.tiempo_segundos ?? null,
  }
}

function _aplicarWod(wod) {
  form.value = {
    titulo:         wod.titulo,
    descripcion:    wod.descripcion || '',
    fecha:          wod.fecha,
    activo:         wod.activo,
    genero_destino: wod.genero_destino || '',
    tipo:           wod.tipo || '',
    ejercicios:     (wod.ejercicios || []).map(_mapEjercicio),
  }
}

async function cargarCatalogo() {
  try {
    const { data } = await api.get('/ejercicios/')
    catalogo.value = data
  } catch {
    catalogo.value = []
  }
}

async function cargarWodParaEdicion() {
  // Primero intenta usar el state que pasó la vista anterior
  const stateWod = history.state?.wod
  if (stateWod) {
    _aplicarWod(stateWod)
    cargando.value = false
    return
  }
  // Fallback: busca en la lista completa por ID
  try {
    const endpoint = esPersonalizado.value ? '/wods/personalizados' : '/wods/'
    const { data } = await api.get(endpoint)
    const wod = data.find(w => w.id === Number(route.params.id))
    if (wod) _aplicarWod(wod)
    else volver()
  } catch {
    volver()
  } finally {
    cargando.value = false
  }
}

async function guardar() {
  if (esPersonalizado.value && !modoEdicion.value) {
    if (!generos.value.masculino && !generos.value.femenino) {
      errorForm.value = 'Selecciona al menos un género destino.'
      return
    }
  }
  guardando.value = true
  errorForm.value = ''
  try {
    const ejercicios = form.value.ejercicios.map((e, i) => ({
      ejercicio_id:    e.ejercicio_id,
      notas:           e.notas?.trim() || null,
      rep_min:         e.rep_min         || null,
      rep_max:         e.rep_max         || null,
      rir:             e.rir             ?? null,
      porcentaje_rm:   e.porcentaje_rm   ?? null,
      tiempo_segundos: e.tiempo_segundos ?? null,
      orden:           i,
    }))

    const tipo = form.value.tipo || null
    if (modoEdicion.value) {
      const payload = {
        titulo:      form.value.titulo,
        descripcion: form.value.descripcion,
        fecha:       form.value.fecha,
        activo:      form.value.activo,
        tipo,
        ejercicios,
      }
      await api.put(`/wods/${route.params.id}`, payload)
    } else if (esPersonalizado.value) {
      const base = {
        titulo:           form.value.titulo,
        descripcion:      form.value.descripcion,
        fecha:            form.value.fecha,
        activo:           form.value.activo,
        es_personalizado: true,
        tipo,
        ejercicios,
      }
      const lista = []
      if (generos.value.masculino) lista.push('masculino')
      if (generos.value.femenino)  lista.push('femenino')
      for (const g of lista) {
        await api.post('/wods/', { ...base, genero_destino: g })
      }
    } else {
      await api.post('/wods/', {
        titulo:      form.value.titulo,
        descripcion: form.value.descripcion,
        fecha:       form.value.fecha,
        activo:      form.value.activo,
        tipo,
        ejercicios,
      })
    }
    volver()
  } catch (e) {
    errorForm.value = e.response?.data?.detail || 'Error al guardar el WOD.'
  } finally {
    guardando.value = false
  }
}

onMounted(async () => {
  await cargarCatalogo()
  if (modoEdicion.value) await cargarWodParaEdicion()
})
</script>
