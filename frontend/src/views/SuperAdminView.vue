<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Header -->
    <header class="bg-gray-900 text-white shadow-lg">
      <div class="max-w-5xl mx-auto px-4 sm:px-6 py-4 flex items-center gap-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-indigo-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        <div class="flex-1 min-w-0">
          <h1 class="text-lg font-extrabold tracking-tight truncate">Panel SuperAdmin</h1>
          <p class="text-xs text-gray-400">Gestión de gimnasios y módulos</p>
        </div>
        <button @click="logout" class="text-sm font-semibold text-gray-300 hover:text-white px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors">
          Cerrar sesión
        </button>
      </div>
    </header>

    <main class="max-w-5xl mx-auto px-4 sm:px-6 py-6 space-y-6">
      <!-- Acciones -->
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-bold text-gray-800">Gimnasios <span class="text-gray-400 font-normal">({{ gimnasios.length }})</span></h2>
        <button @click="abrirCrear"
          class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-sm px-4 py-2.5 rounded-lg shadow-md transition-colors flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Nuevo gimnasio
        </button>
      </div>

      <div v-if="cargando" class="text-center py-12 text-gray-400">Cargando…</div>

      <!-- Listado -->
      <div v-else-if="gimnasios.length === 0" class="text-center py-16 bg-white rounded-2xl border border-dashed border-gray-300">
        <p class="text-gray-400 font-medium">Todavía no hay gimnasios.</p>
        <button @click="abrirCrear" class="mt-3 text-sm font-bold text-indigo-600 hover:text-indigo-800">+ Crear el primero</button>
      </div>
      <div v-else class="grid gap-5 sm:grid-cols-2">
        <div v-for="g in gimnasios" :key="g.id"
          class="bg-white rounded-2xl border border-gray-200 shadow-sm hover:shadow-lg transition-shadow overflow-hidden flex flex-col"
          :class="{ 'opacity-75': !g.activo }">
          <!-- Acento superior -->
          <div class="h-1.5" :class="g.activo ? 'bg-gradient-to-r from-indigo-500 via-violet-500 to-fuchsia-500' : 'bg-gray-300'"></div>

          <div class="p-5 flex flex-col flex-1">
            <!-- Encabezado -->
            <div class="flex items-start gap-3">
              <div class="w-12 h-12 rounded-xl flex items-center justify-center text-lg font-black text-white flex-shrink-0 shadow-sm"
                :class="g.activo ? 'bg-gradient-to-br from-indigo-500 to-violet-600' : 'bg-gray-400'">
                {{ inicial(g.nombre) }}
              </div>
              <div class="min-w-0 flex-1">
                <h3 class="text-lg font-bold text-gray-800 truncate leading-tight">{{ g.nombre }}</h3>
                <div class="flex items-center gap-2 mt-1">
                  <span class="text-xs font-mono text-gray-400 truncate">/{{ g.slug }}</span>
                  <span class="text-[10px] font-bold px-2 py-0.5 rounded-full tracking-wide"
                    :class="g.activo ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-200 text-gray-500'">
                    {{ g.activo ? 'ACTIVO' : 'INACTIVO' }}
                  </span>
                </div>
              </div>
              <!-- Switch activo -->
              <button @click="toggleActivo(g)" role="switch" :aria-checked="g.activo" :title="g.activo ? 'Desactivar gimnasio' : 'Activar gimnasio'"
                class="relative w-11 h-6 rounded-full transition-colors flex-shrink-0 mt-0.5"
                :class="g.activo ? 'bg-emerald-500' : 'bg-gray-300'">
                <span class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform"
                  :class="g.activo ? 'translate-x-5' : ''"></span>
              </button>
            </div>

            <!-- Link de registro -->
            <div class="mt-4 flex items-center gap-2 bg-gray-50 border border-gray-100 rounded-lg px-2.5 py-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 010 5.656l-3 3a4 4 0 11-5.656-5.656l1.5-1.5m6.656-.328a4 4 0 010-5.656l3-3a4 4 0 115.656 5.656l-1.5 1.5" />
              </svg>
              <span class="text-xs text-gray-500 font-mono truncate flex-1">/registro?gym={{ g.slug }}</span>
              <button @click="copiarLink(g.slug)"
                class="text-xs font-bold px-2 py-1 rounded-md flex-shrink-0 transition-colors"
                :class="slugCopiado === g.slug ? 'text-emerald-600 bg-emerald-50' : 'text-indigo-600 hover:bg-indigo-50'">
                {{ slugCopiado === g.slug ? '¡Copiado!' : 'Copiar' }}
              </button>
            </div>

            <!-- Módulos -->
            <div class="mt-4 pt-4 border-t border-gray-100 flex-1">
              <div class="flex items-center justify-between mb-2">
                <p class="text-[11px] font-bold text-gray-400 uppercase tracking-widest">Módulos</p>
                <span v-if="!g._cargandoMod" class="text-[11px] font-bold text-gray-400">{{ contarActivos(g) }}/{{ g._modulos.length }}</span>
              </div>
              <div v-if="g._cargandoMod" class="text-sm text-gray-400">Cargando módulos…</div>
              <div v-else class="flex flex-wrap gap-1.5">
                <button v-for="m in g._modulos" :key="m.modulo_id" @click="toggleModulo(g, m)" :title="m.activo ? 'Desactivar' : 'Activar'"
                  class="text-xs font-semibold px-2.5 py-1 rounded-full border transition-all flex items-center gap-1.5"
                  :class="m.activo ? 'border-indigo-200 bg-indigo-50 text-indigo-700 hover:bg-indigo-100' : 'border-gray-200 text-gray-400 hover:border-gray-300 hover:text-gray-500'">
                  <span class="w-1.5 h-1.5 rounded-full" :class="m.activo ? 'bg-indigo-500' : 'bg-gray-300'"></span>
                  {{ m.nombre }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="errorGlobal" class="bg-red-50 text-red-600 text-sm p-3 rounded-lg border border-red-100 font-medium">
        {{ errorGlobal }}
      </div>
    </main>

    <!-- Modal crear gimnasio -->
    <div v-if="modalCrear" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="modalCrear = false">
      <div class="bg-white rounded-xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between sticky top-0 bg-white">
          <h3 class="text-lg font-bold text-gray-800">Nuevo gimnasio</h3>
          <button @click="modalCrear = false" class="text-gray-400 hover:text-gray-600">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <form @submit.prevent="crearGimnasio" class="p-6 space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Nombre del gimnasio *</label>
              <input v-model="form.nombre" required minlength="2"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 outline-none text-sm" placeholder="CrossFit Centro">
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Slug (URL) *</label>
              <input v-model="form.slug" required pattern="[a-z0-9-]+"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 outline-none text-sm font-mono" placeholder="crossfit-centro">
            </div>
          </div>

          <div class="pt-2 border-t border-gray-100">
            <p class="text-sm font-bold text-gray-700 mb-2">Administrador inicial</p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-1">Nombre *</label>
                <input v-model="form.admin_nombre" required minlength="2"
                  class="w-full px-3 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 outline-none text-sm" placeholder="Juan Pérez">
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-1">Email *</label>
                <input v-model="form.admin_email" type="email" required
                  class="w-full px-3 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 outline-none text-sm" placeholder="admin@gym.com">
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-1">Documento *</label>
                <input v-model="form.admin_documento" required minlength="3"
                  class="w-full px-3 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 outline-none text-sm" placeholder="1020456789">
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-1">Teléfono</label>
                <input v-model="form.admin_telefono"
                  class="w-full px-3 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 outline-none text-sm" placeholder="3001234567">
              </div>
              <div class="sm:col-span-2">
                <label class="block text-sm font-semibold text-gray-700 mb-1">Contraseña *</label>
                <input v-model="form.admin_password" type="text" required minlength="6"
                  class="w-full px-3 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 outline-none text-sm" placeholder="Mínimo 6 caracteres">
              </div>
            </div>
          </div>

          <div class="pt-2 border-t border-gray-100">
            <p class="text-sm font-bold text-gray-700 mb-2">Módulos a activar</p>
            <div class="flex flex-wrap gap-2">
              <button v-for="m in catalogoModulos" :key="m.clave" type="button" @click="toggleFormModulo(m.clave)"
                class="text-sm font-semibold px-3 py-1.5 rounded-lg border transition-colors"
                :class="form.modulos.includes(m.clave) ? 'border-indigo-500 bg-indigo-50 text-indigo-700' : 'border-gray-300 text-gray-400'">
                {{ m.nombre }}
              </button>
            </div>
          </div>

          <div v-if="errorForm" class="bg-red-50 text-red-600 text-sm p-3 rounded-lg border border-red-100 font-medium">
            {{ errorForm }}
          </div>

          <div class="flex justify-end gap-2 pt-2">
            <button type="button" @click="modalCrear = false" class="px-4 py-2 text-sm font-semibold text-gray-600 hover:bg-gray-100 rounded-lg">Cancelar</button>
            <button type="submit" :disabled="guardando"
              class="bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 text-white font-bold text-sm px-5 py-2 rounded-lg shadow-md flex items-center gap-2">
              <span v-if="guardando" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
              Crear gimnasio
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import superApi from '../superApi'

const router = useRouter()
const gimnasios = ref([])
const catalogoModulos = ref([])
const cargando = ref(true)
const errorGlobal = ref('')
const slugCopiado = ref('')

const inicial = (nombre) => (nombre || '?').trim().charAt(0).toUpperCase()
const contarActivos = (g) => (g._modulos || []).filter(m => m.activo).length

async function copiarLink(slug) {
  const url = `${window.location.origin}/registro?gym=${slug}`
  try {
    await navigator.clipboard.writeText(url)
  } catch {
    const ta = document.createElement('textarea')
    ta.value = url
    document.body.appendChild(ta); ta.select()
    document.execCommand('copy'); document.body.removeChild(ta)
  }
  slugCopiado.value = slug
  setTimeout(() => { if (slugCopiado.value === slug) slugCopiado.value = '' }, 2000)
}

const modalCrear = ref(false)
const guardando = ref(false)
const errorForm = ref('')
const form = ref({ nombre: '', slug: '', admin_nombre: '', admin_email: '', admin_documento: '', admin_telefono: '', admin_password: '', modulos: [] })

const fetchModulosCatalogo = async () => {
  const { data } = await superApi.get('/superadmin/modulos')
  catalogoModulos.value = data
}

const fetchModulosDeGym = async (g) => {
  g._cargandoMod = true
  try {
    const { data } = await superApi.get(`/superadmin/gimnasios/${g.id}/modulos`)
    g._modulos = data
  } finally {
    g._cargandoMod = false
  }
}

const fetchGimnasios = async () => {
  cargando.value = true
  errorGlobal.value = ''
  try {
    const { data } = await superApi.get('/superadmin/gimnasios')
    gimnasios.value = data.map(g => ({ ...g, _modulos: [], _cargandoMod: false }))
    await Promise.all(gimnasios.value.map(fetchModulosDeGym))
  } catch (e) {
    errorGlobal.value = 'No se pudieron cargar los gimnasios.'
  } finally {
    cargando.value = false
  }
}

const toggleActivo = async (g) => {
  try {
    const { data } = await superApi.patch(`/superadmin/gimnasios/${g.id}`, { activo: !g.activo })
    g.activo = data.activo
  } catch {
    errorGlobal.value = 'No se pudo actualizar el gimnasio.'
  }
}

const toggleModulo = async (g, m) => {
  try {
    const { data } = await superApi.patch(`/superadmin/gimnasios/${g.id}/modulos/${m.modulo_id}`, { activo: !m.activo })
    m.activo = data.activo
  } catch {
    errorGlobal.value = 'No se pudo actualizar el módulo.'
  }
}

const abrirCrear = () => {
  form.value = { nombre: '', slug: '', admin_nombre: '', admin_email: '', admin_documento: '', admin_telefono: '', admin_password: '', modulos: catalogoModulos.value.map(m => m.clave) }
  errorForm.value = ''
  modalCrear.value = true
}

const toggleFormModulo = (clave) => {
  const i = form.value.modulos.indexOf(clave)
  if (i === -1) form.value.modulos.push(clave)
  else form.value.modulos.splice(i, 1)
}

const crearGimnasio = async () => {
  errorForm.value = ''
  guardando.value = true
  try {
    await superApi.post('/superadmin/gimnasios', form.value)
    modalCrear.value = false
    await fetchGimnasios()
  } catch (e) {
    const d = e.response?.data?.detail
    errorForm.value = Array.isArray(d) ? d[0].msg : (d || 'Error al crear el gimnasio.')
  } finally {
    guardando.value = false
  }
}

const logout = () => {
  localStorage.removeItem('superToken')
  router.push('/superadmin/login')
}

onMounted(async () => {
  try {
    await fetchModulosCatalogo()
    await fetchGimnasios()
  } catch (e) {
    if (e.response?.status === 401) router.push('/superadmin/login')
  }
})
</script>
