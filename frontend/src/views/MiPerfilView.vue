<template>
  <div class="max-w-3xl mx-auto">
    <h2 class="text-2xl font-black text-gray-800 mb-1">Mi Perfil</h2>
    <p class="text-sm text-gray-500 mb-8">Administra tus datos personales y tu cuenta.</p>

    <!-- Loading -->
    <div v-if="cargando" class="flex justify-center py-24">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-red-600"></div>
    </div>

    <template v-else-if="usuario">

      <!-- ── Encabezado: foto + identidad ── -->
      <div class="flex flex-col sm:flex-row sm:items-center gap-6 pb-8 mb-8 border-b border-gray-200">
        <div class="relative mx-auto sm:mx-0">
          <img
            class="h-28 w-28 rounded-full object-cover border-4 border-gray-100 shadow-sm"
            :src="fotoSrc(usuario)"
            alt=""
          />
          <button
            @click="fileInput?.click()"
            :disabled="subiendoFoto"
            title="Cambiar foto"
            class="absolute bottom-1 right-1 w-9 h-9 rounded-full bg-red-600 text-white shadow-md flex items-center justify-center hover:bg-red-700 transition-colors disabled:opacity-50"
          >
            <span v-if="subiendoFoto" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
          </button>
          <input ref="fileInput" type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="onFotoSeleccionada"/>
        </div>
        <div class="text-center sm:text-left">
          <h3 class="text-2xl font-black text-gray-800 leading-tight">{{ usuario.nombre }}</h3>
          <p class="text-sm text-gray-500 break-all mt-0.5">{{ usuario.email }}</p>
          <span class="inline-block text-xs font-bold px-3 py-1 rounded-full bg-gray-100 text-gray-700 mt-2">
            {{ rolLabel(usuario.rol) }}
          </span>
          <p v-if="errorFoto" class="text-xs text-red-600 font-semibold bg-red-50 rounded-lg px-3 py-1.5 mt-3 inline-block">{{ errorFoto }}</p>
        </div>
      </div>

      <!-- ── Datos personales ── -->
      <section class="mb-10">
        <h4 class="text-lg font-black text-gray-800 mb-1">Datos personales</h4>
        <p class="text-sm text-gray-500 mb-5">Tu información de contacto e identidad.</p>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div>
            <label class="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1.5">Nombre completo</label>
            <input v-model="form.nombre" type="text" placeholder="Nombre completo"
              class="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-gray-800 focus:border-transparent transition"/>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1.5">Email</label>
            <input v-model="form.email" type="email" placeholder="correo@ejemplo.com"
              class="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-gray-800 focus:border-transparent transition"/>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1.5">Teléfono</label>
            <input v-model="form.telefono" type="tel" placeholder="Número de teléfono"
              class="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-gray-800 focus:border-transparent transition"/>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1.5">Documento de identidad</label>
            <input v-model="form.documento_identidad" type="text" placeholder="Número de documento"
              class="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-gray-800 focus:border-transparent transition"/>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1.5">Género</label>
            <div class="grid grid-cols-2 gap-2">
              <button type="button" @click="form.genero = 'masculino'"
                class="py-2.5 rounded-xl border text-sm font-semibold transition-colors"
                :class="form.genero === 'masculino' ? 'border-blue-500 bg-blue-50 text-blue-700' : 'border-gray-200 text-gray-500 hover:border-gray-300'">
                Masculino
              </button>
              <button type="button" @click="form.genero = 'femenino'"
                class="py-2.5 rounded-xl border text-sm font-semibold transition-colors"
                :class="form.genero === 'femenino' ? 'border-purple-500 bg-purple-50 text-purple-700' : 'border-gray-200 text-gray-500 hover:border-gray-300'">
                Femenino
              </button>
            </div>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1.5">Fecha de nacimiento <span class="text-gray-400 font-normal">(opcional)</span></label>
            <input v-model="form.fecha_nacimiento" type="date"
              class="block w-full min-w-0 appearance-none px-3.5 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-gray-800 focus:border-transparent transition"/>
          </div>
        </div>
      </section>

      <!-- ── Seguridad ── -->
      <section class="mb-10 pt-8 border-t border-gray-200">
        <h4 class="text-lg font-black text-gray-800 mb-1">Seguridad</h4>
        <p class="text-sm text-gray-500 mb-5">Cambia tu contraseña de acceso.</p>

        <label class="flex items-center gap-2.5 cursor-pointer mb-4">
          <input type="checkbox" v-model="cambiarPassword" class="w-4 h-4 accent-gray-800 rounded"/>
          <span class="text-sm font-semibold text-gray-700">Cambiar contraseña</span>
        </label>
        <div v-if="cambiarPassword" class="max-w-md">
          <label class="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1.5">Nueva contraseña</label>
          <div class="relative">
            <input
              v-model="form.password"
              :type="verPassword ? 'text' : 'password'"
              placeholder="Mínimo 6 caracteres"
              class="w-full px-3.5 py-2.5 pr-10 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-gray-800 focus:border-transparent transition"
            />
            <button type="button" @click="verPassword = !verPassword"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
              <svg v-if="verPassword" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
            </button>
          </div>
          <p v-if="form.password && form.password.length < 6" class="text-xs text-red-500 font-semibold mt-1.5">
            Mínimo 6 caracteres
          </p>
        </div>
      </section>

      <!-- ── Acciones ── -->
      <div class="flex flex-col sm:flex-row items-center gap-3 pt-6 border-t border-gray-200">
        <p v-if="errorEditar" class="text-sm text-red-600 font-semibold bg-red-50 rounded-lg px-3 py-2 flex-1">{{ errorEditar }}</p>
        <p v-else-if="guardadoOk" class="text-sm text-emerald-600 font-semibold bg-emerald-50 rounded-lg px-3 py-2 flex-1">Cambios guardados correctamente.</p>
        <div v-else class="flex-1"></div>
        <div class="flex gap-3 w-full sm:w-auto">
          <button @click="resetForm" :disabled="guardando || !hayCambios"
            class="flex-1 sm:flex-none px-5 py-2.5 rounded-xl border border-gray-200 text-gray-600 font-semibold hover:bg-gray-50 transition-colors text-sm disabled:opacity-40">
            Descartar
          </button>
          <button @click="guardarEdicion" :disabled="guardando || !hayCambios"
            class="flex-1 sm:flex-none px-6 py-2.5 rounded-xl bg-gray-800 hover:bg-black text-white font-bold transition-colors text-sm disabled:bg-gray-300 flex items-center justify-center gap-2">
            <svg v-if="guardando" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
            </svg>
            {{ guardando ? 'Guardando…' : 'Guardar cambios' }}
          </button>
        </div>
      </div>

    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api, { mediaUrl } from '../api'

const usuario = ref(null)
const cargando = ref(true)

// ── Foto ────────────────────────────────────────────────────
const fileInput = ref(null)
const subiendoFoto = ref(false)
const errorFoto = ref('')

function onFotoSeleccionada(e) {
  const file = e.target.files?.[0]
  if (file) subirFoto(file)
  e.target.value = ''
}

async function subirFoto(file) {
  errorFoto.value = ''
  subiendoFoto.value = true
  try {
    const fd = new FormData()
    fd.append('foto', file)
    const { data } = await api.post('/me/foto', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    usuario.value = data
  } catch (err) {
    errorFoto.value = err.response?.data?.detail || 'No se pudo subir la foto.'
  } finally {
    subiendoFoto.value = false
  }
}

// ── Formulario ──────────────────────────────────────────────
const guardando = ref(false)
const guardadoOk = ref(false)
const errorEditar = ref('')
const cambiarPassword = ref(false)
const verPassword = ref(false)
const form = ref({})

function resetForm() {
  form.value = {
    nombre: usuario.value.nombre,
    email: usuario.value.email,
    telefono: usuario.value.telefono || '',
    documento_identidad: usuario.value.documento_identidad || '',
    genero: usuario.value.genero || '',
    fecha_nacimiento: usuario.value.fecha_nacimiento || '',
    password: '',
  }
  cambiarPassword.value = false
  verPassword.value = false
  errorEditar.value = ''
}

const hayCambios = computed(() => {
  if (!usuario.value) return false
  const f = form.value
  return (
    f.nombre !== usuario.value.nombre ||
    f.email !== usuario.value.email ||
    f.telefono !== (usuario.value.telefono || '') ||
    f.documento_identidad !== (usuario.value.documento_identidad || '') ||
    f.genero !== (usuario.value.genero || '') ||
    f.fecha_nacimiento !== (usuario.value.fecha_nacimiento || '') ||
    (cambiarPassword.value && !!f.password)
  )
})

async function guardarEdicion() {
  errorEditar.value = ''
  guardadoOk.value = false

  if (cambiarPassword.value && form.value.password.length < 6) {
    errorEditar.value = 'La contraseña debe tener al menos 6 caracteres.'
    return
  }

  const payload = {}
  if (form.value.nombre !== usuario.value.nombre) payload.nombre = form.value.nombre
  if (form.value.email !== usuario.value.email) payload.email = form.value.email
  if (form.value.telefono !== (usuario.value.telefono || '')) payload.telefono = form.value.telefono
  if (form.value.documento_identidad !== (usuario.value.documento_identidad || '')) payload.documento_identidad = form.value.documento_identidad
  if (form.value.genero !== (usuario.value.genero || '')) payload.genero = form.value.genero
  if (form.value.fecha_nacimiento !== (usuario.value.fecha_nacimiento || '')) payload.fecha_nacimiento = form.value.fecha_nacimiento || null
  if (cambiarPassword.value && form.value.password) payload.password = form.value.password

  if (Object.keys(payload).length === 0) return

  guardando.value = true
  try {
    const { data } = await api.patch('/me', payload)
    usuario.value = data
    if (data.nombre) localStorage.setItem('userName', data.nombre)
    resetForm()
    guardadoOk.value = true
  } catch (e) {
    errorEditar.value = e.response?.data?.detail || 'Error al guardar los cambios.'
  } finally {
    guardando.value = false
  }
}

// ── Helpers ─────────────────────────────────────────────────
const fotoSrc = (u) => u?.foto_url
  ? mediaUrl(u.foto_url)
  : `https://ui-avatars.com/api/?name=${encodeURIComponent(u?.nombre || 'U')}&background=dc2626&color=fff&size=128`

const rolLabel = (rol) => ({ admin: 'Administrador', coach: 'Coach', cliente: 'Cliente', pendiente: 'Pendiente' }[rol] || rol)

// ── Fetch ───────────────────────────────────────────────────
onMounted(async () => {
  try {
    const { data } = await api.get('/me')
    usuario.value = data
    resetForm()
  } catch { /* silencioso */ }
  cargando.value = false
})
</script>
