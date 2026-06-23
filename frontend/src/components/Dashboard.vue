<template>
  <div class="flex h-screen bg-gray-50 font-sans">

    <!-- ── Overlay móvil ── -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 bg-black/50 z-30 md:hidden"
      @click="sidebarOpen = false"
    />

    <!-- ── Sidebar ── -->
    <aside
      class="fixed inset-y-0 left-0 z-40 w-64 bg-black text-white flex flex-col shadow-xl transform transition-transform duration-300 md:relative md:translate-x-0 md:flex"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <!-- Logo -->
      <div class="p-6 border-b border-gray-800 flex items-center gap-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-red-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        <h1 class="text-xl font-extrabold tracking-wider">Jain Sport Box</h1>
        <!-- Cerrar en móvil -->
        <button @click="sidebarOpen = false" class="ml-auto md:hidden text-gray-400 hover:text-white p-1">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <!-- User info -->
      <div class="px-4 py-4 border-b border-gray-800">
        <p class="text-sm font-semibold text-white truncate">{{ nombre }}</p>
        <span class="inline-block mt-1 text-xs font-bold px-2 py-0.5 rounded-full"
          :class="{
            'bg-red-500 text-white': isAdmin,
            'bg-emerald-500 text-white': isCoach,
            'bg-gray-600 text-gray-200': isCliente,
            'bg-amber-500 text-white': isPendiente,
          }">
          {{ rolLabel }}
        </span>

        <!-- Aviso cuenta pendiente -->
        <div v-if="isPendiente" class="mt-3 bg-amber-900/40 rounded-xl p-3 text-center">
          <p class="text-xs font-bold text-amber-300 uppercase tracking-wide mb-1">En espera</p>
          <p class="text-xs text-amber-400">Selecciona un plan para que el admin apruebe tu cuenta.</p>
        </div>

      </div>

      <!-- Nav links -->
      <nav class="flex-1 mt-4 px-4 space-y-2 overflow-y-auto">

        <!-- Usuario pendiente: solo ve Planes -->
        <template v-if="isPendiente">
          <router-link to="/planes" @click="sidebarOpen = false"
            class="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-gray-800 transition-colors"
            active-class="bg-red-600 hover:bg-red-700 font-semibold shadow-md">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Planes
          </router-link>
        </template>

        <!-- ── GESTIÓN (admin + coach) ── -->
        <template v-if="!isPendiente && canManage">
          <div class="pt-2 pb-1 px-2">
            <p class="text-xs font-bold text-gray-500 uppercase tracking-widest">Gestión</p>
          </div>
          <router-link to="/usuarios" @click="sidebarOpen = false"
            class="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-gray-800 transition-colors"
            active-class="bg-red-600 hover:bg-red-700 font-semibold shadow-md">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            Usuarios
          </router-link>
          <router-link to="/sesiones" @click="sidebarOpen = false"
            class="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-gray-800 transition-colors"
            active-class="bg-red-600 hover:bg-red-700 font-semibold shadow-md">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            Sesiones
          </router-link>
          <router-link to="/alertas" @click="sidebarOpen = false"
            class="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-gray-800 transition-colors"
            active-class="bg-red-600 hover:bg-red-700 font-semibold shadow-md">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            Alertas WhatsApp
          </router-link>
          <router-link to="/ejercicios" @click="sidebarOpen = false"
            class="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-gray-800 transition-colors"
            active-class="bg-red-600 hover:bg-red-700 font-semibold shadow-md">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
            </svg>
            Ejercicios
          </router-link>
          <!-- Solo admin -->
          <router-link v-if="isAdmin" to="/planes" @click="sidebarOpen = false"
            class="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-gray-800 transition-colors"
            active-class="bg-red-600 hover:bg-red-700 font-semibold shadow-md">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Planes
          </router-link>
          <router-link v-if="isAdmin" to="/finanzas" @click="sidebarOpen = false"
            class="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-gray-800 transition-colors"
            active-class="bg-red-600 hover:bg-red-700 font-semibold shadow-md">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Finanzas
          </router-link>
        </template>

        <!-- ── CONTENIDO (todos menos pendiente) ── -->
        <template v-if="!isPendiente">
          <div class="pt-2 pb-1 px-2">
            <p class="text-xs font-bold text-gray-500 uppercase tracking-widest">Contenido</p>
          </div>
          <router-link v-if="!membresiaVencida" to="/wods" @click="sidebarOpen = false"
            class="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-gray-800 transition-colors"
            active-class="bg-red-600 hover:bg-red-700 font-semibold shadow-md">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            WODs
          </router-link>
          <router-link v-if="!membresiaVencida && (canManage || tieneWodsPersonalizados)" to="/wods/personalizados" @click="sidebarOpen = false"
            class="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-gray-800 transition-colors"
            active-class="bg-red-600 hover:bg-red-700 font-semibold shadow-md">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
            </svg>
            WODs Personalizados
          </router-link>
          <router-link v-if="canManage" to="/tienda" @click="sidebarOpen = false"
            class="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-gray-800 transition-colors"
            active-class="bg-red-600 hover:bg-red-700 font-semibold shadow-md">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
            Tienda
          </router-link>
        </template>

        <!-- ── MI BOX (coach + cliente) ── -->
        <template v-if="!isPendiente && (isCliente || isCoach)">
          <div class="pt-2 pb-1 px-2">
            <p class="text-xs font-bold text-gray-500 uppercase tracking-widest">Mi Box</p>
          </div>
          <router-link to="/home" @click="sidebarOpen = false"
            class="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-gray-800 transition-colors"
            active-class="bg-red-600 hover:bg-red-700 font-semibold shadow-md">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            Inicio
          </router-link>
          <router-link v-if="isCliente" to="/planes" @click="sidebarOpen = false"
            class="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-gray-800 transition-colors"
            active-class="bg-red-600 hover:bg-red-700 font-semibold shadow-md">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Planes
          </router-link>
          <router-link v-if="isCliente && !membresiaVencida" to="/salud" @click="sidebarOpen = false"
            class="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-gray-800 transition-colors"
            active-class="bg-red-600 hover:bg-red-700 font-semibold shadow-md">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
            Mi Salud
          </router-link>
          <router-link v-if="!membresiaVencida" to="/marcas" @click="sidebarOpen = false"
            class="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-gray-800 transition-colors"
            active-class="bg-red-600 hover:bg-red-700 font-semibold shadow-md">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Mis Marcas
          </router-link>
        </template>

        <!-- ── CUENTA (todos menos pendiente) ── -->
        <template v-if="!isPendiente">
          <div class="pt-2 pb-1 px-2">
            <p class="text-xs font-bold text-gray-500 uppercase tracking-widest">Cuenta</p>
          </div>
          <router-link to="/perfil" @click="sidebarOpen = false"
            class="flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-gray-800 transition-colors"
            active-class="bg-red-600 hover:bg-red-700 font-semibold shadow-md">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            Mi Perfil
          </router-link>
        </template>

      </nav>

      <!-- Chip sesión activa -->
      <div v-if="tieneSession && !isPendiente" class="px-4 pb-3">
        <div class="flex items-center gap-2 bg-red-950 border border-red-800 rounded-xl px-3 py-2.5">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-red-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <button @click="irASesion" class="flex-1 text-left min-w-0">
            <p class="text-xs font-bold text-white truncate">{{ sesion.ejercicio }}</p>
            <p class="text-xs text-red-300">{{ sesion.series.length }} serie{{ sesion.series.length !== 1 ? 's' : '' }} en progreso</p>
          </button>
          <button @click="cancelarSesion" title="Cancelar sesión"
            class="p-1 text-red-500 hover:text-white transition-colors shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Logout -->
      <div class="p-4 border-t border-gray-800">
        <button @click="logout"
          class="w-full flex items-center gap-3 py-3 px-4 rounded-lg text-gray-400 hover:bg-red-600 hover:text-white transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          <span class="font-semibold text-sm">Cerrar Sesión</span>
        </button>
        <p class="text-xs text-gray-600 text-center mt-3">&copy; 2026 Jain Sport Box</p>
      </div>
    </aside>

    <!-- ── Main ── -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">

      <!-- Top bar móvil -->
      <header class="md:hidden flex items-center gap-3 px-4 py-3 bg-black text-white shadow-lg flex-shrink-0">
        <button @click="sidebarOpen = true" class="p-1.5 rounded-lg hover:bg-gray-800 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
        </svg>
        <span class="font-extrabold tracking-wider text-base">Jain Sport Box</span>
      </header>

      <!-- Content -->
      <main class="flex-1 overflow-x-hidden overflow-y-auto">
        <div class="p-4 sm:p-6 md:p-8">
          <router-view></router-view>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth, setFechaVencimiento } from '../composables/useAuth'
import { useSessionMarca } from '../composables/useSessionMarca'
import api from '../api'

const router = useRouter()
const { nombre, rol, isAdmin, isCoach, isCliente, isPendiente, canManage, membresiaVencida } = useAuth()
const { sesion, tieneSession, cancelarSesion } = useSessionMarca()

const sidebarOpen = ref(false)

function irASesion() {
  if (!sesion.value) return
  sidebarOpen.value = false
  router.push('/marcas/' + encodeURIComponent(sesion.value.ejercicio))
}
const tieneWodsPersonalizados = ref(localStorage.getItem('tieneWodsPersonalizados') === 'true')

onMounted(async () => {
  if (!isCliente.value) return
  try {
    const { data } = await api.get('/me')
    tieneWodsPersonalizados.value = !!data.incluye_wods_personalizados
    localStorage.setItem('tieneWodsPersonalizados', String(tieneWodsPersonalizados.value))
    if (data.genero) localStorage.setItem('userGenero', data.genero)
    // Refrescar fecha de vencimiento para que el sidebar reaccione tras renovaciones.
    setFechaVencimiento(data.fecha_vencimiento || '')
  } catch { /* silencioso */ }
})

const rolLabel = computed(() => {
  const labels = { admin: 'Administrador', coach: 'Coach', cliente: 'Cliente', pendiente: 'Cuenta Pendiente' }
  return labels[rol.value] || rol.value
})

const logout = () => {
  cancelarSesion()
  localStorage.removeItem('token')
  localStorage.removeItem('userRol')
  localStorage.removeItem('userName')
  localStorage.removeItem('fechaVencimiento')
  localStorage.removeItem('tieneWodsPersonalizados')
  localStorage.removeItem('userGenero')
  router.push('/login')
}
</script>
