<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-3xl font-black text-gray-800 tracking-tight">WODs Personalizados</h2>
        <p class="text-gray-500 mt-1">Entrenamientos especiales por género</p>
      </div>
      <button
        v-if="isStaff"
        @click="router.push('/wods/personalizados/nuevo')"
        class="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white font-bold py-2.5 px-5 rounded-lg shadow transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Nuevo WOD
      </button>
    </div>

    <!-- ── VISTA STAFF ── -->
    <template v-if="isStaff">
      <!-- Stats activos -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
        <div class="bg-red-50 rounded-2xl p-5 border border-red-100">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-red-600 rounded-xl flex items-center justify-center flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div>
              <p class="text-xs font-bold text-red-500 uppercase tracking-widest">Masculino activos</p>
              <p class="text-3xl font-black text-red-700">{{ countActivos('masculino') }}</p>
              <p class="text-xs text-red-400">{{ countActivos('masculino') === 1 ? 'WOD activo' : 'WODs activos' }}</p>
            </div>
          </div>
        </div>
        <div class="bg-gray-100 rounded-2xl p-5 border border-gray-200">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-gray-600 rounded-xl flex items-center justify-center flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div>
              <p class="text-xs font-bold text-gray-500 uppercase tracking-widest">Femenino activos</p>
              <p class="text-3xl font-black text-gray-700">{{ countActivos('femenino') }}</p>
              <p class="text-xs text-gray-400">{{ countActivos('femenino') === 1 ? 'WOD activo' : 'WODs activos' }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- WODs Personalizados Activos -->
      <div class="mb-10">
        <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-widest mb-3">WODs Personalizados Activos</h3>

        <div v-if="wodsActivos.length > 0" class="space-y-3">
          <div
            v-for="wod in wodsActivos"
            :key="wod.id"
            class="rounded-2xl p-5 text-white shadow-lg"
            :class="wod.genero_destino === 'masculino' ? 'bg-gray-900' : 'bg-gray-800'"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-2 flex-wrap">
                  <span
                    class="inline-block text-xs font-bold px-2.5 py-1 rounded-md"
                    :class="wod.genero_destino === 'masculino' ? 'bg-red-600 text-white' : 'bg-gray-600 text-white'"
                  >
                    {{ wod.genero_destino === 'masculino' ? 'Masculino' : 'Femenino' }}
                  </span>
                  <span v-if="wod.tipo" class="text-xs font-bold bg-white/15 text-white px-2 py-0.5 rounded-md">
                    {{ wod.tipo }}
                  </span>
                </div>
                <h4 class="text-xl font-black mb-1">{{ wod.titulo }}</h4>
                <p v-if="wod.descripcion" class="text-sm whitespace-pre-line leading-relaxed text-gray-300 mb-2">{{ wod.descripcion }}</p>
                <button
                  v-if="wod.ejercicios && wod.ejercicios.length"
                  @click.stop="toggleExpandido(wod.id)"
                  class="flex items-center gap-1.5 text-xs font-semibold text-gray-400 hover:text-white transition-colors"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 transition-transform duration-200" :class="expandidos[wod.id] ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7" />
                  </svg>
                  {{ expandidos[wod.id] ? 'Ocultar ejercicios' : `Ver ${wod.ejercicios.length} ejercicio${wod.ejercicios.length !== 1 ? 's' : ''}` }}
                </button>
                <div v-show="expandidos[wod.id]" class="mt-3">
                  <WodEjerciciosLista :ejercicios="wod.ejercicios" dark />
                </div>
              </div>
              <div class="flex gap-2 flex-shrink-0">
                <button
                  @click="toggleWod(wod)"
                  title="Mover al historial"
                  class="p-2 rounded-lg bg-white/10 hover:bg-yellow-500/40 transition-colors"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                </button>
                <button @click="router.push({ name: 'WodPersonalizadoEditar', params: { id: wod.id }, state: { wod } })" class="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors" title="Editar">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                  </svg>
                </button>
                <button @click="eliminarWod(wod)" class="p-2 rounded-lg bg-white/10 hover:bg-red-500/60 transition-colors" title="Eliminar">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="!cargando" class="bg-gray-50 rounded-xl border border-dashed border-gray-200 p-8 text-center">
          <p class="text-gray-400 font-medium text-sm">No hay WODs personalizados activos</p>
          <button @click="router.push('/wods/personalizados/nuevo')" class="mt-3 text-red-600 font-semibold hover:underline text-sm">
            + Crear el primero
          </button>
        </div>
      </div>

      <!-- Historial de personalizados -->
      <div v-if="wodsHistorial.length > 0">
        <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-widest mb-3">Historial de Personalizados</h3>

        <!-- Buscador -->
        <div class="relative mb-3">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M17 11A6 6 0 115 11a6 6 0 0112 0z" />
          </svg>
          <input
            v-model="busquedaHistorial"
            type="text"
            placeholder="Buscar en el historial..."
            class="w-full pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-red-500/30 focus:border-red-400"
          />
        </div>

        <!-- Filtro por tipo -->
        <div class="flex flex-wrap gap-1.5 mb-4">
          <button
            v-for="t in ['', 'For Time', 'AMRAP', 'EMOM', 'Por Rondas', 'Fuerza', 'Otro']"
            :key="t"
            @click="tipoFiltroHistorial = t"
            class="text-xs font-semibold px-2.5 py-1 rounded-full border transition-colors"
            :class="tipoFiltroHistorial === t
              ? 'bg-gray-800 text-white border-gray-800'
              : 'bg-white text-gray-400 border-gray-200 hover:border-gray-400'"
          >
            {{ t || 'Todos' }}
          </button>
        </div>

        <div v-if="historialFiltrado.length > 0" class="space-y-2">
          <div
            v-for="wod in historialFiltrado"
            :key="wod.id"
            class="bg-white rounded-xl border border-gray-200 p-4 flex items-start gap-4 hover:shadow-sm transition-shadow opacity-60"
          >
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-0.5 flex-wrap">
                <p class="font-bold text-gray-800 truncate">{{ wod.titulo }}</p>
                <span
                  class="text-xs font-bold px-2 py-0.5 rounded-full flex-shrink-0"
                  :class="wod.genero_destino === 'masculino' ? 'bg-red-100 text-red-700' : 'bg-gray-200 text-gray-700'"
                >
                  {{ wod.genero_destino === 'masculino' ? 'Masculino' : 'Femenino' }}
                </span>
                <span v-if="wod.tipo" class="text-xs font-bold bg-gray-200 text-gray-600 px-2 py-0.5 rounded-md flex-shrink-0">{{ wod.tipo }}</span>
              </div>
              <p class="text-xs text-gray-400 mt-0.5">Última fecha: {{ formatFecha(wod.fecha) }}</p>
              <p v-if="wod.descripcion" class="text-sm text-gray-500 line-clamp-2 mt-1">{{ wod.descripcion }}</p>
              <button
                v-if="wod.ejercicios && wod.ejercicios.length"
                @click.stop="toggleExpandido(wod.id)"
                class="mt-1.5 flex items-center gap-1 text-xs font-semibold text-gray-400 hover:text-red-600 transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 transition-transform duration-200" :class="expandidos[wod.id] ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7" />
                </svg>
                {{ expandidos[wod.id] ? 'Ocultar' : `${wod.ejercicios.length} ejercicio${wod.ejercicios.length !== 1 ? 's' : ''}` }}
              </button>
              <div v-show="expandidos[wod.id]" class="mt-2">
                <WodEjerciciosLista :ejercicios="wod.ejercicios" class="mt-1" />
              </div>
            </div>
            <div class="flex gap-1 flex-shrink-0">
              <button
                @click="toggleWod(wod)"
                title="Restaurar a activos"
                class="p-1.5 rounded-lg text-gray-400 hover:bg-green-50 hover:text-green-600 transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </button>
              <button @click="router.push({ name: 'WodPersonalizadoEditar', params: { id: wod.id }, state: { wod } })" class="p-1.5 rounded-lg text-gray-400 hover:bg-gray-100 hover:text-red-600 transition-colors" title="Editar">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
              </button>
              <button @click="eliminarWod(wod)" class="p-1.5 rounded-lg text-gray-400 hover:bg-red-50 hover:text-red-600 transition-colors" title="Eliminar">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
        <div v-else class="bg-gray-50 rounded-xl border border-gray-200 p-5 text-center">
          <p class="text-gray-400 text-sm">{{ (busquedaHistorial || tipoFiltroHistorial) ? 'Sin resultados para ese filtro' : 'El historial está vacío' }}</p>
        </div>
      </div>

      <div v-if="!cargando && wodsActivos.length === 0 && wodsHistorial.length === 0" class="bg-gray-50 border-2 border-dashed border-gray-200 rounded-2xl p-12 text-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-14 w-14 text-gray-300 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
        </svg>
        <p class="text-gray-500 font-bold text-lg mb-1">Sin WODs personalizados</p>
        <p class="text-gray-400 text-sm mb-4">Crea el primer WOD personalizado para tus atletas.</p>
        <button @click="router.push('/wods/personalizados/nuevo')" class="text-red-600 font-semibold hover:underline text-sm">
          + Crear el primero
        </button>
      </div>
    </template>

    <!-- ── VISTA CLIENTE ── -->
    <template v-else>
      <!-- Sin acceso al plan -->
      <div v-if="sinAcceso" class="bg-gray-50 border-2 border-dashed border-gray-200 rounded-2xl p-14 text-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-gray-300 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        <p class="text-lg font-bold text-gray-600 mb-2">Plan no incluido</p>
        <p class="text-gray-400 text-sm max-w-xs mx-auto">Tu plan actual no incluye entrenamientos personalizados. Actualiza tu membresía para acceder.</p>
        <router-link to="/planes" class="inline-block mt-5 bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-5 rounded-lg text-sm transition-colors">
          Ver planes disponibles
        </router-link>
      </div>

      <template v-else>
        <!-- WOD de hoy -->
        <div class="mb-8">
          <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-widest mb-3">
            Tu WOD de Hoy · {{ fechaHoyTexto }}
          </h3>

          <div
            v-if="wodDeHoy"
            class="rounded-2xl p-6 text-white shadow-lg"
            :class="colorCard"
          >
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xs font-bold uppercase tracking-widest bg-red-600 text-white px-2 py-0.5 rounded-md">WOD Personalizado</span>
              <span class="text-xs font-bold px-2.5 py-0.5 rounded-full" :class="colorBadge">
                {{ generoLabel }}
              </span>
            </div>
            <h3 class="text-2xl font-black mt-2 mb-1">{{ wodDeHoy.titulo }}</h3>
            <p v-if="wodDeHoy.descripcion" class="whitespace-pre-line leading-relaxed text-gray-300 text-sm mb-2">{{ wodDeHoy.descripcion }}</p>
            <button
              v-if="wodDeHoy.ejercicios && wodDeHoy.ejercicios.length"
              @click="toggleExpandido(wodDeHoy.id)"
              class="flex items-center gap-1.5 text-xs font-semibold text-gray-400 hover:text-white transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 transition-transform duration-200" :class="expandidos[wodDeHoy.id] ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7" />
              </svg>
              {{ expandidos[wodDeHoy.id] ? 'Ocultar ejercicios' : `Ver ${wodDeHoy.ejercicios.length} ejercicio${wodDeHoy.ejercicios.length !== 1 ? 's' : ''}` }}
            </button>
            <div v-show="expandidos[wodDeHoy.id]" class="mt-3">
              <WodEjerciciosLista :ejercicios="wodDeHoy.ejercicios" dark />
            </div>
          </div>

          <div v-else-if="!cargando" class="bg-gray-50 border-2 border-dashed border-gray-200 rounded-2xl p-10 text-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-300 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <p class="text-gray-400 font-medium">No hay WOD personalizado para hoy</p>
            <p class="text-gray-300 text-sm mt-1">Vuelve mañana o consulta el historial.</p>
          </div>
        </div>

        <!-- Historial -->
        <div v-if="wodsAnteriores.length > 0">
          <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-widest mb-3">Historial</h3>
          <div class="space-y-2">
            <div
              v-for="wod in wodsAnteriores"
              :key="wod.id"
              class="bg-white rounded-xl border border-gray-200 p-4 flex items-start gap-3 hover:shadow-sm transition-shadow"
            >
              <div
                class="w-11 h-11 rounded-xl flex flex-col items-center justify-center flex-shrink-0"
                :class="generoCliente === 'masculino' ? 'bg-red-50' : 'bg-gray-100'"
              >
                <span class="text-sm font-black leading-none" :class="generoCliente === 'masculino' ? 'text-red-700' : 'text-gray-700'">
                  {{ diaDelMes(wod.fecha) }}
                </span>
                <span class="text-xs leading-none mt-0.5" :class="generoCliente === 'masculino' ? 'text-red-400' : 'text-gray-400'">
                  {{ mesCorto(wod.fecha) }}
                </span>
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-bold text-gray-800 truncate">{{ wod.titulo }}</p>
                <p v-if="wod.descripcion" class="text-sm text-gray-500 line-clamp-2 mt-0.5">{{ wod.descripcion }}</p>
                <button
                  v-if="wod.ejercicios && wod.ejercicios.length"
                  @click.stop="toggleExpandido(wod.id)"
                  class="mt-1.5 flex items-center gap-1 text-xs font-semibold text-gray-400 hover:text-red-600 transition-colors"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 transition-transform duration-200" :class="expandidos[wod.id] ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7" />
                  </svg>
                  {{ expandidos[wod.id] ? 'Ocultar' : `${wod.ejercicios.length} ejercicio${wod.ejercicios.length !== 1 ? 's' : ''}` }}
                </button>
                <div v-show="expandidos[wod.id]" class="mt-2">
                  <WodEjerciciosLista :ejercicios="wod.ejercicios" class="mt-1" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </template>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { useAuth } from '../composables/useAuth'
import WodEjerciciosLista from '../components/WodEjerciciosLista.vue'

const { isAdmin, isCoach } = useAuth()
const isStaff = computed(() => isAdmin.value || isCoach.value)
const router = useRouter()

const wods       = ref([])
const cargando   = ref(true)
const sinAcceso  = ref(false)
const expandidos = ref({})

function toggleExpandido(id) {
  expandidos.value[id] = !expandidos.value[id]
}

const generoCliente = computed(() => localStorage.getItem('userGenero') || '')

const hoyISO = computed(() => new Date().toISOString().slice(0, 10))
const fechaHoyTexto = computed(() =>
  new Date().toLocaleDateString('es-CO', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
)

const wodsActivos   = computed(() => wods.value.filter(w => w.activo))
const wodsHistorial = computed(() => wods.value.filter(w => !w.activo))

const wodDeHoy = computed(() => wods.value.find(w => w.fecha === hoyISO.value) || null)
const wodsAnteriores = computed(() => wods.value.filter(w => w.fecha !== hoyISO.value))

const generoLabel = computed(() =>
  generoCliente.value === 'masculino' ? 'Masculino' : generoCliente.value === 'femenino' ? 'Femenino' : ''
)
const colorCard = computed(() =>
  generoCliente.value === 'masculino' ? 'bg-gray-900' : 'bg-gray-800'
)
const colorBadge = computed(() =>
  generoCliente.value === 'masculino'
    ? 'bg-red-600 text-white'
    : 'bg-gray-600 text-white'
)

function countActivos(genero) {
  return wods.value.filter(w => w.activo && w.genero_destino === genero).length
}

const busquedaHistorial   = ref('')
const tipoFiltroHistorial = ref('')

const historialFiltrado = computed(() => {
  let result = wodsHistorial.value
  const q = busquedaHistorial.value.trim().toLowerCase()
  if (q) result = result.filter(w => w.titulo.toLowerCase().includes(q))
  if (tipoFiltroHistorial.value) result = result.filter(w => w.tipo === tipoFiltroHistorial.value)
  return result
})

function formatFecha(fecha) {
  return new Date(fecha + 'T12:00:00').toLocaleDateString('es-CO', { day: 'numeric', month: 'long', year: 'numeric' })
}

function diaDelMes(fecha) {
  return new Date(fecha + 'T12:00:00').getDate()
}

function mesCorto(fecha) {
  return new Date(fecha + 'T12:00:00').toLocaleDateString('es-CO', { month: 'short' })
}

async function cargar() {
  cargando.value = true
  sinAcceso.value = false
  try {
    const { data } = await api.get('/wods/personalizados')
    wods.value = data
  } catch (e) {
    if (e.response?.status === 403) {
      sinAcceso.value = true
    }
  } finally {
    cargando.value = false
  }
}


async function toggleWod(wod) {
  try {
    const { data } = await api.patch(`/wods/${wod.id}/toggle`)
    const idx = wods.value.findIndex(w => w.id === wod.id)
    if (idx !== -1) wods.value[idx] = data
  } catch (e) {
    alert(e.response?.data?.detail || 'Error al cambiar estado del WOD.')
  }
}

async function eliminarWod(wod) {
  if (!confirm(`¿Eliminar el WOD "${wod.titulo}"?`)) return
  try {
    await api.delete(`/wods/${wod.id}`)
    await cargar()
  } catch (e) {
    alert(e.response?.data?.detail || 'Error al eliminar.')
  }
}

onMounted(cargar)
</script>
