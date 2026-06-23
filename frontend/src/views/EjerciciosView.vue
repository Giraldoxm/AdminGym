<template>
  <div class="animate-fade-in-up">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-3xl font-black text-gray-800 tracking-tight">Ejercicios</h2>
        <p class="text-gray-500 mt-1">Catálogo reutilizable para armar los WODs</p>
      </div>
      <button
        v-if="puedeEditar"
        @click="abrirFormulario()"
        class="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white font-bold py-2.5 px-5 rounded-lg shadow transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Nuevo ejercicio
      </button>
    </div>

    <!-- Buscador -->
    <div class="mb-4 relative max-w-sm">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 absolute left-3 top-3 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      <input
        v-model="busqueda"
        type="text"
        placeholder="Buscar ejercicio..."
        class="w-full pl-9 pr-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 outline-none text-sm"
      />
    </div>

    <!-- Filtro por categoría -->
    <div class="flex flex-wrap gap-2 mb-5">
      <button
        v-for="cat in ['', 'Cardio', 'Fuerza', 'Gimnasia', 'Olímpico', 'Otro']"
        :key="cat"
        @click="categoriaFiltro = cat"
        class="text-xs font-semibold px-3 py-1.5 rounded-full border transition-colors"
        :class="categoriaFiltro === cat
          ? 'bg-gray-800 text-white border-gray-800'
          : 'bg-white text-gray-500 border-gray-200 hover:border-gray-400'"
      >
        {{ cat || 'Todas' }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="cargando" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="i in 6" :key="i" class="bg-white rounded-2xl h-28 animate-pulse border border-gray-100" />
    </div>

    <!-- Vacío -->
    <div
      v-else-if="ejerciciosFiltrados.length === 0"
      class="bg-gray-50 border-2 border-dashed border-gray-200 rounded-2xl p-14 text-center"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-14 w-14 mx-auto text-gray-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
      <p class="text-gray-500 font-medium">
        {{ (busqueda || categoriaFiltro) ? 'No se encontraron ejercicios.' : 'Aún no hay ejercicios registrados.' }}
      </p>
      <button v-if="puedeEditar && !busqueda && !categoriaFiltro" @click="abrirFormulario()" class="mt-4 text-red-600 font-semibold hover:underline text-sm">
        + Crear el primero
      </button>
    </div>

    <!-- Grid -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="ej in ejerciciosFiltrados"
        :key="ej.id"
        class="bg-white rounded-2xl border border-gray-100 p-5 hover:shadow-md transition-shadow flex flex-col"
      >
        <div class="flex items-start justify-between gap-3 mb-3">
          <div class="flex-1 min-w-0">
            <h3 class="font-black text-gray-800 truncate">{{ ej.nombre }}</h3>
            <span v-if="ej.categoria" class="inline-block text-xs font-semibold px-2 py-0.5 rounded-full mt-1 mb-0.5" :class="categoriaCss(ej.categoria)">
              {{ ej.categoria }}
            </span>
            <p v-if="ej.descripcion" class="text-xs text-gray-500 mt-1 line-clamp-2">{{ ej.descripcion }}</p>
            <p v-if="ej.video_url" class="text-xs text-gray-400 truncate mt-0.5">{{ ej.video_url }}</p>
            <p v-else class="text-xs text-gray-300 italic mt-0.5">Sin video</p>
          </div>
          <div v-if="puedeEditar" class="flex gap-1 flex-shrink-0">
            <button
              @click="abrirFormulario(ej)"
              class="p-1.5 rounded-lg text-gray-400 hover:bg-gray-100 hover:text-red-600 transition-colors"
              title="Editar"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
            </button>
            <button
              @click="eliminar(ej)"
              class="p-1.5 rounded-lg text-gray-400 hover:bg-red-50 hover:text-red-600 transition-colors"
              title="Eliminar"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>

        <a
          v-if="ej.video_url"
          :href="ej.video_url"
          target="_blank"
          rel="noopener noreferrer"
          class="mt-auto inline-flex items-center gap-2 text-sm font-semibold text-red-600 hover:text-red-700"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z" />
          </svg>
          Ver video
        </a>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="mostrarModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md">
        <div class="p-6 border-b border-gray-100 flex items-center justify-between">
          <h3 class="text-lg font-bold text-gray-800">{{ editando ? 'Editar ejercicio' : 'Nuevo ejercicio' }}</h3>
          <button @click="cerrarModal" class="p-2 rounded-lg hover:bg-gray-100 text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <form @submit.prevent="guardar" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">Nombre</label>
            <input
              v-model="form.nombre"
              type="text"
              required
              placeholder="Ej: Pull-up"
              class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all"
            />
          </div>
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">Link del video <span class="text-gray-400 font-normal">(opcional)</span></label>
            <input
              v-model="form.video_url"
              type="url"
              placeholder="https://youtube.com/watch?v=..."
              class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all"
            />
          </div>
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">Descripción <span class="text-gray-400 font-normal">(opcional)</span></label>
            <textarea
              v-model="form.descripcion"
              rows="3"
              placeholder="Explica la técnica, puntos clave, variantes…"
              class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all resize-none text-sm"
            ></textarea>
          </div>
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">Categoría <span class="text-gray-400 font-normal">(opcional)</span></label>
            <select
              v-model="form.categoria"
              class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all bg-white text-sm"
            >
              <option value="">Sin categoría</option>
              <option value="Cardio">Cardio</option>
              <option value="Fuerza">Fuerza</option>
              <option value="Gimnasia">Gimnasia</option>
              <option value="Olímpico">Olímpico</option>
              <option value="Otro">Otro</option>
            </select>
          </div>
          <div v-if="errorForm" class="bg-red-50 text-red-600 text-sm p-3 rounded-lg border border-red-100">
            {{ errorForm }}
          </div>
          <div class="flex gap-3 pt-2">
            <button type="button" @click="cerrarModal" class="flex-1 py-2.5 rounded-lg border border-gray-300 text-gray-600 font-semibold hover:bg-gray-50 transition-colors">
              Cancelar
            </button>
            <button :disabled="guardando" class="flex-1 py-2.5 rounded-lg bg-red-600 hover:bg-red-700 text-white font-bold transition-colors disabled:bg-red-300 flex items-center justify-center gap-2">
              <span v-if="guardando" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
              {{ guardando ? 'Guardando...' : (editando ? 'Actualizar' : 'Crear') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'

const ejercicios      = ref([])
const cargando        = ref(true)
const busqueda        = ref('')
const categoriaFiltro = ref('')
const mostrarModal    = ref(false)
const editando        = ref(null)
const guardando       = ref(false)
const errorForm       = ref('')
const form            = ref({ nombre: '', video_url: '', descripcion: '', categoria: '' })

const userRol     = computed(() => localStorage.getItem('userRol') || 'cliente')
const puedeEditar = computed(() => ['admin', 'coach'].includes(userRol.value))

const CATEGORIA_CSS = {
  'Cardio':    'bg-red-100 text-red-700',
  'Fuerza':    'bg-blue-100 text-blue-700',
  'Gimnasia':  'bg-purple-100 text-purple-700',
  'Olímpico':  'bg-amber-100 text-amber-700',
  'Otro':      'bg-gray-100 text-gray-600',
}
function categoriaCss(cat) { return CATEGORIA_CSS[cat] || 'bg-gray-100 text-gray-600' }

const ejerciciosFiltrados = computed(() => {
  let result = ejercicios.value
  const q = busqueda.value.trim().toLowerCase()
  if (q) result = result.filter(e => e.nombre.toLowerCase().includes(q))
  if (categoriaFiltro.value) result = result.filter(e => e.categoria === categoriaFiltro.value)
  return result
})

async function cargar() {
  cargando.value = true
  try {
    const { data } = await api.get('/ejercicios/')
    ejercicios.value = data
  } finally {
    cargando.value = false
  }
}

function abrirFormulario(ej = null) {
  editando.value = ej
  errorForm.value = ''
  form.value = ej
    ? { nombre: ej.nombre, video_url: ej.video_url || '', descripcion: ej.descripcion || '', categoria: ej.categoria || '' }
    : { nombre: '', video_url: '', descripcion: '', categoria: '' }
  mostrarModal.value = true
}

function cerrarModal() {
  mostrarModal.value = false
  editando.value = null
}

async function guardar() {
  guardando.value = true
  errorForm.value = ''
  try {
    const payload = {
      nombre: form.value.nombre.trim(),
      video_url: form.value.video_url.trim() || null,
      descripcion: form.value.descripcion.trim() || null,
      categoria: form.value.categoria || null,
    }
    if (editando.value) {
      await api.put(`/ejercicios/${editando.value.id}`, payload)
    } else {
      await api.post('/ejercicios/', payload)
    }
    cerrarModal()
    await cargar()
  } catch (e) {
    errorForm.value = e.response?.data?.detail || 'Error al guardar.'
  } finally {
    guardando.value = false
  }
}

async function eliminar(ej) {
  if (!confirm(`¿Eliminar el ejercicio "${ej.nombre}"?`)) return
  try {
    await api.delete(`/ejercicios/${ej.id}`)
    await cargar()
  } catch (e) {
    alert(e.response?.data?.detail || 'Error al eliminar.')
  }
}

onMounted(cargar)
</script>
