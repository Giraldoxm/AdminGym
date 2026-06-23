<template>
  <div class="animate-fade-in-up">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
      <div>
        <h2 class="text-3xl font-extrabold text-gray-900 tracking-tight">Usuarios</h2>
        <p class="text-gray-500 mt-1">Gestiona los usuarios y sus membresías</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <button @click="abrirPalanquera" :disabled="palanqueraAbriendo" class="bg-emerald-600 hover:bg-emerald-700 disabled:opacity-60 text-white px-4 py-2.5 rounded-lg shadow-md hover:shadow-lg transition-all font-semibold flex items-center gap-2 transform active:scale-95">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5 9V7a5 5 0 019.9-1 1 1 0 11-1.98.32A3 3 0 007 7v2h6a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm5 3a1 1 0 00-1 1v2a1 1 0 102 0v-2a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          {{ palanqueraAbriendo ? 'Abriendo…' : 'Abrir palanquera' }}
        </button>
        <button @click="abrirBuscarHuella" class="bg-gray-700 hover:bg-gray-800 text-white px-4 py-2.5 rounded-lg shadow-md hover:shadow-lg transition-all font-semibold flex items-center gap-2 transform active:scale-95">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M6.625 2.655A9 9 0 0119 11a1 1 0 11-2 0 7 7 0 00-9.625-6.492 1 1 0 11-.75-1.853zM4.662 4.959A1 1 0 014.75 6.37 6.97 6.97 0 003 11a1 1 0 11-2 0 8.97 8.97 0 012.25-5.953 1 1 0 011.412-.088z" clip-rule="evenodd"/>
            <path fill-rule="evenodd" d="M5 11a5 5 0 1110 0 1 1 0 11-2 0 3 3 0 10-6 0c0 1.677-.345 3.276-.968 4.729a1 1 0 11-1.838-.789A9.964 9.964 0 005 11z" clip-rule="evenodd"/>
          </svg>
          Buscar por Huella
        </button>
        <button @click="showForm = true" class="bg-red-600 hover:bg-red-700 text-white px-5 py-2.5 rounded-lg shadow-md hover:shadow-lg transition-all font-semibold flex items-center gap-2 transform active:scale-95">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
          </svg>
          Nuevo Usuario
        </button>
      </div>
    </div>

    <!-- Panel: cumpleaños hoy -->
    <div v-if="cumpleaneros.length > 0" class="mb-5 border border-gray-300/60 rounded-2xl overflow-hidden">
      <!-- Header clicable -->
      <button
        @click="cumpleanosExpandido = !cumpleanosExpandido"
        class="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-50/60 transition-colors">
        <div class="flex items-center gap-2">
          <span>🎂</span>
          <span class="text-xs font-bold text-gray-600 uppercase tracking-widest">Cumpleaños hoy</span>
          <span class="text-[10px] font-black bg-red-600 text-white w-4 h-4 flex items-center justify-center rounded-full">{{ cumpleaneros.length }}</span>
        </div>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400 transition-transform"
          :class="cumpleanosExpandido ? 'rotate-180' : ''"
          fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
        </svg>
      </button>
      <!-- Filas colapsables -->
      <div v-if="cumpleanosExpandido" class="flex flex-col divide-y divide-gray-100">
        <div
          v-for="u in cumpleaneros" :key="u.id"
          class="flex items-center justify-between gap-3 px-4 py-2.5 bg-transparent">
          <span class="text-sm font-semibold text-gray-800 truncate">{{ u.nombre }}</span>
          <div class="flex items-center gap-2 flex-shrink-0">
            <a
              v-if="u.telefono"
              :href="whatsappCumpleanos(u)"
              target="_blank"
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/>
                <path d="M12 0C5.373 0 0 5.373 0 12c0 2.126.553 4.116 1.522 5.85L0 24l6.335-1.48A11.945 11.945 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 21.818a9.818 9.818 0 01-5.006-1.371l-.36-.214-3.73.871.938-3.63-.234-.373A9.817 9.817 0 012.182 12C2.182 6.57 6.57 2.182 12 2.182c5.43 0 9.818 4.388 9.818 9.818 0 5.43-4.388 9.818-9.818 9.818z"/>
              </svg>
              Felicitar
            </a>
            <button
              @click="router.push(`/usuarios/${u.id}`)"
              class="px-3 py-1.5 rounded-lg bg-white border border-gray-200 hover:border-gray-300 text-gray-600 hover:text-gray-800 text-xs font-semibold transition-colors">
              Ver perfil
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Buscador -->
    <div class="relative mb-4">
      <svg xmlns="http://www.w3.org/2000/svg" class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z"/>
      </svg>
      <input
        v-model="busqueda"
        type="text"
        placeholder="Buscar por nombre o documento de identidad..."
        class="w-full pl-9 pr-4 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none text-sm transition-all"
      >
      <button v-if="busqueda" @click="busqueda = ''" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
      </button>
    </div>

    <!-- Filtros -->
    <div class="flex flex-wrap gap-2 mb-5">
      <button v-for="tab in tabs" :key="tab.key" @click="filtroActivo = tab.key"
        class="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all border"
        :class="filtroActivo === tab.key
          ? 'bg-red-600 text-white border-red-600 shadow-md'
          : 'bg-white text-gray-600 border-gray-200 hover:border-red-300 hover:text-red-600'">
        {{ tab.label }}
        <span class="text-xs font-black px-1.5 py-0.5 rounded-full"
          :class="filtroActivo === tab.key ? 'bg-white/20 text-white' : 'bg-gray-100 text-gray-500'">
          {{ tab.count }}
        </span>
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading && filtroActivo !== 'pendientes'" class="flex justify-center py-16">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600"></div>
    </div>

    <!-- Empty -->
    <div v-else-if="filtroActivo !== 'pendientes' && usuariosFiltrados.length === 0" class="bg-white rounded-xl border border-gray-100 px-6 py-12 text-center text-gray-400">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
      {{ tabs.find(t => t.key === filtroActivo)?.emptyMsg || 'No hay usuarios.' }}
    </div>

    <template v-else-if="filtroActivo !== 'pendientes'">
      <!-- ── Cards (móvil) ── -->
      <div class="sm:hidden space-y-3">
        <div v-for="user in usuariosFiltrados" :key="user.id"
          class="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
          <div class="flex items-center gap-3 mb-3">
            <img class="h-11 w-11 rounded-full object-cover bg-gray-100 flex-shrink-0" :src="fotoSrc(user)" alt="" />
            <div class="min-w-0 flex-1">
              <p class="font-semibold text-gray-900 truncate">{{ user.nombre }}</p>
              <p class="text-xs text-gray-500 truncate">{{ user.email }}</p>
            </div>
            <span class="px-2 py-0.5 text-xs font-semibold rounded-full flex-shrink-0"
              :class="{
                'bg-purple-100 text-purple-800': user.rol === 'admin',
                'bg-blue-100 text-blue-800': user.rol === 'coach',
                'bg-gray-100 text-gray-700': user.rol === 'cliente',
              }">{{ user.rol }}</span>
          </div>
          <div class="flex items-center justify-between">
            <div>
              <template v-if="user.fecha_vencimiento">
                <p class="text-sm font-semibold" :class="colorTextoDias(diasRestantes(user.fecha_vencimiento))">
                  {{ etiquetaDias(diasRestantes(user.fecha_vencimiento)) }}
                </p>
                <p class="text-xs text-gray-400">Vence {{ formatFecha(user.fecha_vencimiento) }}</p>
              </template>
              <span v-else class="text-sm text-gray-400 italic">Sin membresía</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-full border"
                :class="user.esta_en_gym ? 'bg-green-100 text-green-800 border-green-200' : 'bg-gray-100 text-gray-600 border-gray-200'">
                <span class="w-1.5 h-1.5 rounded-full" :class="user.esta_en_gym ? 'bg-green-500' : 'bg-gray-400'"></span>
                {{ user.esta_en_gym ? 'Activo' : 'Fuera' }}
              </span>
              <button @click="verUsuario(user)" class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
              </button>
              <button @click="confirmarEliminar(user)" class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Tabla (desktop) ── -->
      <div class="hidden sm:block bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Usuario</th>
                <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Rol</th>
                <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Membresía</th>
                <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Estado</th>
                <th class="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Acciones</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-100">
              <tr v-for="user in usuariosFiltrados" :key="user.id" class="hover:bg-gray-50 transition-colors group">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center gap-3">
                    <img class="h-10 w-10 rounded-full object-cover bg-gray-100 flex-shrink-0" :src="fotoSrc(user)" alt="" />
                    <div>
                      <div class="text-sm font-semibold text-gray-900 group-hover:text-red-600 transition-colors">{{ user.nombre }}</div>
                      <div class="text-xs text-gray-500">{{ user.email }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full"
                    :class="{
                      'bg-purple-100 text-purple-800': user.rol === 'admin',
                      'bg-blue-100 text-blue-800': user.rol === 'coach',
                      'bg-gray-100 text-gray-700': user.rol === 'cliente',
                    }">{{ user.rol }}</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <template v-if="user.fecha_vencimiento">
                    <div class="flex items-center gap-2">
                      <span class="w-2 h-2 rounded-full flex-shrink-0" :class="colorPuntoDias(diasRestantes(user.fecha_vencimiento))"></span>
                      <div>
                        <p class="text-sm font-semibold" :class="colorTextoDias(diasRestantes(user.fecha_vencimiento))">{{ etiquetaDias(diasRestantes(user.fecha_vencimiento)) }}</p>
                        <p class="text-xs text-gray-400">Vence {{ formatFecha(user.fecha_vencimiento) }}</p>
                      </div>
                    </div>
                  </template>
                  <span v-else class="text-sm text-gray-400 italic">Sin membresía</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-3 py-1 inline-flex items-center gap-1.5 text-xs font-semibold rounded-full border shadow-sm"
                    :class="user.esta_en_gym ? 'bg-green-100 text-green-800 border-green-200' : 'bg-gray-100 text-gray-600 border-gray-200'">
                    <span class="w-2 h-2 rounded-full" :class="user.esta_en_gym ? 'bg-green-500' : 'bg-gray-400'"></span>
                    {{ user.esta_en_gym ? 'Activo' : 'Fuera' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center gap-2">
                    <button @click="verUsuario(user)" title="Ver detalle" class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                    </button>
                    <button @click="confirmarEliminar(user)" title="Eliminar" class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <!-- ── Tab: Pendientes ── -->
    <template v-if="filtroActivo === 'pendientes'">
      <div v-if="loadingPendientes" class="flex justify-center py-16">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600"></div>
      </div>
      <div v-else-if="pendientes.length === 0" class="bg-white rounded-xl border border-gray-100 px-6 py-12 text-center text-gray-400">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        No hay usuarios pendientes de aprobación.
      </div>
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="p in pendientes" :key="p.id" class="bg-white rounded-xl border border-red-100 shadow-sm p-5 flex flex-col gap-3">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
            </div>
            <div class="min-w-0">
              <p class="font-bold text-gray-900 truncate">{{ p.nombre }}</p>
              <p class="text-xs text-gray-500 truncate">{{ p.email }}</p>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2 text-xs">
            <div class="bg-gray-50 rounded-lg px-3 py-2">
              <p class="text-gray-400 font-semibold uppercase tracking-wide mb-0.5">Documento</p>
              <p class="font-semibold text-gray-700">{{ p.documento_identidad }}</p>
            </div>
            <div class="bg-gray-50 rounded-lg px-3 py-2">
              <p class="text-gray-400 font-semibold uppercase tracking-wide mb-0.5">Teléfono</p>
              <p class="font-semibold text-gray-700">{{ p.telefono || '—' }}</p>
            </div>
            <div class="bg-gray-50 rounded-lg px-3 py-2 col-span-2">
              <p class="text-gray-400 font-semibold uppercase tracking-wide mb-0.5">Género</p>
              <p class="font-semibold text-gray-700 capitalize">{{ p.genero || '—' }}</p>
            </div>
          </div>
          <p class="text-xs text-gray-400">Registrado {{ formatFechaCorta(p.created_at) }}</p>
          <button @click="abrirActivar(p)"
            class="w-full py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white font-bold text-sm transition-colors flex items-center justify-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            Asignar Plan y Activar
          </button>
        </div>
      </div>
    </template>

    <!-- ── Modal: Activar usuario pendiente ── -->
    <div v-if="showActivar" class="fixed inset-0 flex items-end sm:items-center justify-center bg-gray-900/60 backdrop-blur-sm z-50 p-4">
      <div class="bg-white rounded-2xl w-full max-w-lg shadow-2xl max-h-[90vh] flex flex-col overflow-hidden">
        <div class="bg-gradient-to-r from-red-600 to-red-700 px-6 py-5 flex items-center gap-3 flex-shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <div>
            <h3 class="text-lg font-bold text-white">Activar Usuario</h3>
            <p class="text-red-100 text-sm">{{ activarUsuario?.nombre }}</p>
          </div>
          <button @click="showActivar = false" class="ml-auto text-white/70 hover:text-white">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <div class="px-6 py-5 overflow-y-auto flex-1 space-y-5">
          <!-- Selección de plan -->
          <div>
            <p class="text-sm font-semibold text-gray-700 mb-3">Selecciona el plan a asignar</p>
            <div class="grid grid-cols-2 gap-3">
              <label v-for="plan in planes" :key="plan.id"
                class="flex flex-col items-center p-4 rounded-xl border-2 cursor-pointer transition-all"
                :class="activarPlan === plan.id ? 'border-red-500 bg-red-50' : 'border-gray-200 hover:border-gray-300'">
                <input type="radio" v-model="activarPlan" :value="plan.id" class="sr-only">
                <span class="text-2xl font-black mb-0.5" :class="activarPlan === plan.id ? 'text-red-600' : 'text-gray-700'">
                  {{ plan.duracion_dias }}<span class="text-sm font-bold">d</span>
                </span>
                <span class="text-sm font-bold text-center" :class="activarPlan === plan.id ? 'text-red-700' : 'text-gray-600'">{{ plan.nombre }}</span>
                <span class="text-xs mt-1" :class="activarPlan === plan.id ? 'text-red-500' : 'text-gray-400'">${{ plan.precio.toLocaleString() }}</span>
              </label>
            </div>
          </div>

          <!-- Monto -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">
              Monto cobrado ($)
              <span v-if="activarPlan" class="text-gray-400 font-normal">— sugerido ${{ (planes.find(p => p.id === activarPlan)?.precio || 0).toLocaleString() }}</span>
            </label>
            <input v-model.number="activarMonto" type="number" min="0" step="any"
              class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none"
              :placeholder="activarPlan ? '$' + (planes.find(p => p.id === activarPlan)?.precio || 0).toLocaleString() : 'Ej: 100000'">
          </div>

          <!-- Método de pago -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">Método de pago</label>
            <div class="grid grid-cols-2 gap-2">
              <label v-for="m in metodos" :key="m.value"
                class="flex items-center justify-center gap-1.5 p-2.5 rounded-lg border-2 cursor-pointer transition-all text-sm font-semibold"
                :class="activarMetodo === m.value ? 'border-red-500 bg-red-50 text-red-700' : 'border-gray-200 text-gray-600 hover:border-gray-300'">
                <input type="radio" v-model="activarMetodo" :value="m.value" class="sr-only">
                {{ m.label }}
              </label>
            </div>
          </div>

          <div v-if="errorActivar" class="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg p-3">{{ errorActivar }}</div>

          <div class="flex gap-3">
            <button @click="showActivar = false" class="flex-1 py-2.5 rounded-xl border border-gray-200 text-gray-600 font-semibold hover:bg-gray-50 transition-colors">Cancelar</button>
            <button @click="confirmarActivar" :disabled="guardandoActivar || !activarPlan"
              class="flex-1 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white font-bold transition-colors disabled:bg-red-300 flex items-center justify-center gap-2">
              <span v-if="guardandoActivar" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
              {{ guardandoActivar ? 'Activando...' : 'Activar Usuario' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Modal: Ver detalle ── -->
    <div v-if="usuarioSeleccionado" class="fixed inset-0 flex items-end sm:items-center justify-center bg-gray-900/60 backdrop-blur-sm z-50 p-4">
      <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">
        <div class="bg-gradient-to-r from-red-600 to-red-700 px-5 py-5 sm:px-8 sm:py-6 flex items-center gap-4 flex-shrink-0">
          <img class="h-16 w-16 rounded-full border-4 border-white shadow-md object-cover" :src="fotoSrc(usuarioSeleccionado, 128)" alt="" />
          <div>
            <h3 class="text-xl font-bold text-white">{{ usuarioSeleccionado.nombre }}</h3>
            <span class="inline-block mt-1 px-2.5 py-0.5 text-xs font-semibold bg-white/20 text-white rounded-full">{{ usuarioSeleccionado.rol }}</span>
          </div>
          <button @click="usuarioSeleccionado = null" class="ml-auto text-white/70 hover:text-white">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="px-5 py-5 sm:px-8 sm:py-6 space-y-4 overflow-y-auto flex-1">
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-gray-50 rounded-xl p-4">
              <p class="text-xs text-gray-400 font-semibold uppercase tracking-wide mb-1">Email</p>
              <p class="text-sm font-semibold text-gray-800 break-all">{{ usuarioSeleccionado.email }}</p>
            </div>
            <div class="bg-gray-50 rounded-xl p-4">
              <p class="text-xs text-gray-400 font-semibold uppercase tracking-wide mb-1">Documento</p>
              <p class="text-sm font-semibold text-gray-800">{{ usuarioSeleccionado.documento_identidad }}</p>
            </div>
            <div class="bg-gray-50 rounded-xl p-4">
              <p class="text-xs text-gray-400 font-semibold uppercase tracking-wide mb-1">Género</p>
              <span
                v-if="usuarioSeleccionado.genero"
                class="inline-block text-xs font-bold px-2.5 py-1 rounded-full"
                :class="usuarioSeleccionado.genero === 'masculino' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'"
              >
                {{ usuarioSeleccionado.genero === 'masculino' ? 'Masculino' : 'Femenino' }}
              </span>
              <p v-else class="text-sm text-gray-400 italic">—</p>
            </div>
            <div class="bg-gray-50 rounded-xl p-4">
              <p class="text-xs text-gray-400 font-semibold uppercase tracking-wide mb-1">Huella Digital</p>
              <div class="flex items-center justify-between gap-2">
                <p class="text-sm font-semibold" :class="usuarioSeleccionado.huella_id ? 'text-emerald-700' : 'text-gray-400'">
                  {{ usuarioSeleccionado.huella_id ? 'Registrada' : 'No registrada' }}
                </p>
                <button
                  @click="abrirEnrolamiento(usuarioSeleccionado)"
                  class="text-xs px-2.5 py-1 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-semibold transition-colors flex items-center gap-1"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M6.625 2.655A9 9 0 0119 11a1 1 0 11-2 0 7 7 0 00-9.625-6.492 1 1 0 11-.75-1.853zM4.662 4.959A1 1 0 014.75 6.37 6.97 6.97 0 003 11a1 1 0 11-2 0 8.97 8.97 0 012.25-5.953 1 1 0 011.412-.088z" clip-rule="evenodd"/>
                    <path fill-rule="evenodd" d="M5 11a5 5 0 1110 0 1 1 0 11-2 0 3 3 0 10-6 0c0 1.677-.345 3.276-.968 4.729a1 1 0 11-1.838-.789A9.964 9.964 0 005 11z" clip-rule="evenodd"/>
                  </svg>
                  {{ usuarioSeleccionado.huella_id ? 'Re-registrar' : 'Registrar' }}
                </button>
              </div>
            </div>
            <div class="bg-gray-50 rounded-xl p-4 col-span-2">
              <p class="text-xs text-gray-400 font-semibold uppercase tracking-wide mb-2">Membresía</p>
              <template v-if="usuarioSeleccionado.fecha_vencimiento">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-bold" :class="colorTextoDias(diasRestantes(usuarioSeleccionado.fecha_vencimiento))">
                      {{ etiquetaDias(diasRestantes(usuarioSeleccionado.fecha_vencimiento)) }}
                    </p>
                    <p class="text-xs text-gray-500 mt-0.5">Vence el {{ formatFecha(usuarioSeleccionado.fecha_vencimiento) }}</p>
                  </div>
                  <div class="w-12 h-12 rounded-full flex items-center justify-center"
                    :class="bgCirculoDias(diasRestantes(usuarioSeleccionado.fecha_vencimiento))">
                    <span class="text-xs font-black" :class="colorTextoDias(diasRestantes(usuarioSeleccionado.fecha_vencimiento))">
                      {{ Math.abs(diasRestantes(usuarioSeleccionado.fecha_vencimiento)) }}d
                    </span>
                  </div>
                </div>
              </template>
              <p v-else class="text-sm text-gray-400">Sin membresía activa</p>
            </div>
            <div class="bg-gray-50 rounded-xl p-4">
              <p class="text-xs text-gray-400 font-semibold uppercase tracking-wide mb-1">En el box</p>
              <div class="flex items-center gap-2 mt-1">
                <span class="w-2.5 h-2.5 rounded-full" :class="usuarioSeleccionado.esta_en_gym ? 'bg-green-500' : 'bg-gray-300'"></span>
                <p class="text-sm font-semibold text-gray-800">{{ usuarioSeleccionado.esta_en_gym ? 'Activo' : 'Fuera' }}</p>
              </div>
            </div>
            <div class="bg-gray-50 rounded-xl p-4">
              <p class="text-xs text-gray-400 font-semibold uppercase tracking-wide mb-1">Miembro desde</p>
              <p class="text-sm font-semibold text-gray-800">{{ formatFechaCorta(usuarioSeleccionado.created_at) }}</p>
            </div>
          </div>
        </div>
        <div class="px-8 pb-6 flex gap-3">
          <button @click="usuarioSeleccionado = null" class="py-2.5 px-4 rounded-xl border border-gray-200 text-gray-600 font-semibold hover:bg-gray-50 transition-colors">Cerrar</button>
          <button @click="abrirRenovar(usuarioSeleccionado); usuarioSeleccionado = null" class="flex-1 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white font-semibold transition-colors">Renovar</button>
          <button @click="abrirEditar(usuarioSeleccionado); usuarioSeleccionado = null" class="flex-1 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-600 text-white font-semibold transition-colors">Editar</button>
        </div>
      </div>
    </div>

    <!-- ── Modal: Renovar membresía ── -->
    <div v-if="showRenovar" class="fixed inset-0 flex items-end sm:items-center justify-center bg-gray-900/60 backdrop-blur-sm z-50 p-4">
      <div class="bg-white rounded-2xl w-full max-w-lg shadow-2xl max-h-[90vh] flex flex-col overflow-hidden">
        <div class="bg-gradient-to-r from-emerald-500 to-emerald-600 px-6 py-5 flex items-center gap-3 flex-shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
          <div>
            <h3 class="text-lg font-bold text-white">Renovar Membresía</h3>
            <p class="text-emerald-100 text-sm">{{ renovarUsuario?.nombre }}</p>
          </div>
          <button @click="showRenovar = false" class="ml-auto text-white/70 hover:text-white">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <div class="px-6 py-5 overflow-y-auto flex-1">
          <!-- Estado actual -->
          <div class="mb-5 p-3 rounded-xl"
            :class="renovarUsuario?.fecha_vencimiento && diasRestantes(renovarUsuario.fecha_vencimiento) > 0
              ? 'bg-emerald-50 border border-emerald-100'
              : 'bg-red-50 border border-red-100'">
            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Membresía actual</p>
            <template v-if="renovarUsuario?.fecha_vencimiento">
              <p class="text-sm font-bold" :class="colorTextoDias(diasRestantes(renovarUsuario.fecha_vencimiento))">
                {{ etiquetaDias(diasRestantes(renovarUsuario.fecha_vencimiento)) }}
              </p>
              <p class="text-xs text-gray-500">Vence el {{ formatFecha(renovarUsuario.fecha_vencimiento) }} · Los días nuevos se sumarán a esa fecha.</p>
            </template>
            <p v-else class="text-sm text-gray-500">Sin membresía activa — los días contarán desde hoy.</p>
          </div>

          <!-- Selección de plan -->
          <p class="text-sm font-semibold text-gray-700 mb-3">Selecciona un plan</p>
          <div class="grid grid-cols-2 gap-3 mb-4">
            <label v-for="plan in planes" :key="plan.id"
              class="flex flex-col items-center p-4 rounded-xl border-2 cursor-pointer transition-all"
              :class="renovarPlan === plan.id ? 'border-emerald-500 bg-emerald-50' : 'border-gray-200 hover:border-gray-300'">
              <input type="radio" v-model="renovarPlan" :value="plan.id" class="sr-only">
              <span class="text-2xl font-black mb-0.5" :class="renovarPlan === plan.id ? 'text-emerald-600' : 'text-gray-700'">
                {{ plan.duracion_dias }}<span class="text-sm font-bold">d</span>
              </span>
              <span class="text-sm font-bold" :class="renovarPlan === plan.id ? 'text-emerald-700' : 'text-gray-600'">{{ plan.nombre }}</span>
              <span class="text-xs mt-1" :class="renovarPlan === plan.id ? 'text-emerald-500' : 'text-gray-400'">${{ plan.precio.toLocaleString() }}</span>
            </label>

            <label class="flex flex-col items-center p-4 rounded-xl border-2 cursor-pointer transition-all col-span-2"
              :class="renovarPlan === 'personalizado' ? 'border-emerald-500 bg-emerald-50' : 'border-gray-200 hover:border-gray-300'">
              <input type="radio" v-model="renovarPlan" value="personalizado" class="sr-only">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mb-1" :class="renovarPlan === 'personalizado' ? 'text-emerald-500' : 'text-gray-400'" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/></svg>
              <span class="text-sm font-bold" :class="renovarPlan === 'personalizado' ? 'text-emerald-700' : 'text-gray-600'">Personalizado (días)</span>
            </label>
          </div>

          <!-- Días personalizados -->
          <div v-if="renovarPlan === 'personalizado'" class="mb-4">
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">Días a agregar</label>
            <input v-model.number="renovarDias" type="number" min="1" max="365"
              class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-emerald-500 outline-none"
              placeholder="Ej: 10">
          </div>

          <!-- Monto -->
          <div class="mb-4">
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">
              Monto cobrado ($)
              <span v-if="renovarPlan !== 'personalizado' && planSeleccionadoObj" class="text-gray-400 font-normal">
                — sugerido ${{ planSeleccionadoObj.precio.toLocaleString() }}
              </span>
            </label>
            <input v-model.number="renovarMonto" type="number" min="0" step="any"
              class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-emerald-500 outline-none"
              :placeholder="planSeleccionadoObj ? '$' + planSeleccionadoObj.precio.toLocaleString() : 'Ej: 100000'">
          </div>

          <!-- Método de pago -->
          <div class="mb-5">
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">Método de pago</label>
            <div class="grid grid-cols-3 gap-2">
              <label v-for="m in metodos" :key="m.value"
                class="flex items-center justify-center gap-1.5 p-2.5 rounded-lg border-2 cursor-pointer transition-all text-sm font-semibold"
                :class="renovarMetodo === m.value ? 'border-emerald-500 bg-emerald-50 text-emerald-700' : 'border-gray-200 text-gray-600 hover:border-gray-300'">
                <input type="radio" v-model="renovarMetodo" :value="m.value" class="sr-only">
                {{ m.label }}
              </label>
            </div>
          </div>

          <div v-if="errorRenovar" class="mb-4 text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg p-3">{{ errorRenovar }}</div>

          <div class="flex gap-3">
            <button @click="showRenovar = false" class="flex-1 py-2.5 rounded-xl border border-gray-200 text-gray-600 font-semibold hover:bg-gray-50 transition-colors">Cancelar</button>
            <button @click="confirmarRenovacion" :disabled="guardandoRenovar || !renovarPlan"
              class="flex-1 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white font-bold transition-colors disabled:bg-emerald-200 flex items-center justify-center gap-2">
              <span v-if="guardandoRenovar" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
              {{ guardandoRenovar ? 'Guardando...' : 'Confirmar Renovación' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Modal: Editar usuario ── -->
    <div v-if="showEditar" class="fixed inset-0 flex items-end sm:items-center justify-center bg-gray-900/60 backdrop-blur-sm z-50 p-4">
      <div class="bg-white rounded-2xl p-5 sm:p-8 w-full max-w-lg shadow-2xl max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-6">
          <div>
            <h3 class="text-2xl font-bold text-gray-900">Editar Usuario</h3>
            <p class="text-sm text-gray-500 mt-0.5">{{ editando?.nombre }}</p>
          </div>
          <button @click="cerrarEditar" class="text-gray-400 hover:text-gray-600">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <!-- Foto -->
        <div class="mb-6 flex flex-col items-center">
          <div class="relative h-24 w-24 rounded-full border-4 border-dashed border-gray-200 bg-gray-50 flex items-center justify-center cursor-pointer hover:border-red-400 hover:bg-red-50 transition-all overflow-hidden"
            @click="$refs.inputFotoEdit.click()">
            <img v-if="editFotoPreview" :src="editFotoPreview" class="h-full w-full object-cover" />
            <img v-else-if="editando?.foto_url" :src="mediaUrl(editando.foto_url)" class="h-full w-full object-cover" />
            <div v-else class="flex flex-col items-center text-gray-400">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
            </div>
            <input ref="inputFotoEdit" type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="onFotoEditChange" />
          </div>
          <p class="text-xs text-gray-400 mt-2">Clic para cambiar la foto</p>
        </div>

        <form @submit.prevent="guardarEdicion">
          <div class="mb-5">
            <label class="block text-gray-700 text-sm font-semibold mb-2">Email</label>
            <input v-model="editForm.email" type="email" class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none transition-all" required>
          </div>
          <div class="mb-5">
            <label class="block text-gray-700 text-sm font-semibold mb-2">Teléfono / WhatsApp</label>
            <input v-model="editForm.telefono" type="tel" class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none transition-all" placeholder="Ej. 3001234567">
          </div>
          <div class="mb-5">
            <label class="block text-gray-700 text-sm font-semibold mb-2">Género</label>
            <div class="grid grid-cols-2 gap-3">
              <button
                type="button"
                @click="editForm.genero = 'masculino'"
                class="py-2.5 rounded-xl border-2 font-bold text-sm transition-all"
                :class="editForm.genero === 'masculino'
                  ? 'border-blue-600 bg-blue-600 text-white'
                  : 'border-gray-200 text-gray-500 hover:border-blue-300 hover:text-blue-600'"
              >
                Masculino
              </button>
              <button
                type="button"
                @click="editForm.genero = 'femenino'"
                class="py-2.5 rounded-xl border-2 font-bold text-sm transition-all"
                :class="editForm.genero === 'femenino'
                  ? 'border-purple-600 bg-purple-600 text-white'
                  : 'border-gray-200 text-gray-500 hover:border-purple-300 hover:text-purple-600'"
              >
                Femenino
              </button>
            </div>
          </div>
          <div class="mb-6">
            <label class="block text-gray-700 text-sm font-semibold mb-2">Nueva Contraseña <span class="text-gray-400 font-normal">(dejar vacío para no cambiar)</span></label>
            <input v-model="editForm.password" type="password" minlength="6" class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none transition-all" placeholder="Min. 6 caracteres">
          </div>
          <div class="flex justify-end gap-3 pt-4 border-t border-gray-100">
            <button @click="cerrarEditar" type="button" class="px-5 py-2.5 rounded-lg text-gray-600 font-semibold hover:bg-gray-100 transition-colors">Cancelar</button>
            <button type="submit" :disabled="guardandoEdicion" class="px-5 py-2.5 rounded-lg bg-red-600 hover:bg-red-700 text-white font-semibold shadow-md inline-flex items-center gap-2 transition-all active:scale-95">
              <span v-if="guardandoEdicion" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
              {{ guardandoEdicion ? 'Guardando...' : 'Guardar Cambios' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ── Modal: Crear usuario ── -->
    <div v-if="showForm" class="fixed inset-0 flex items-end sm:items-center justify-center bg-gray-900/60 backdrop-blur-sm z-50 p-4">
      <div class="bg-white rounded-2xl p-5 sm:p-8 w-full max-w-lg shadow-2xl max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold text-gray-900">Registrar Usuario</h3>
          <button @click="cerrarFormulario" class="text-gray-400 hover:text-gray-600">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <!-- Foto -->
        <div class="mb-6 flex flex-col items-center">
          <div class="relative h-24 w-24 rounded-full border-4 border-dashed border-gray-200 bg-gray-50 flex items-center justify-center cursor-pointer hover:border-red-400 hover:bg-red-50 transition-all overflow-hidden"
            @click="$refs.inputFoto.click()">
            <img v-if="fotoPreview" :src="fotoPreview" class="h-full w-full object-cover" />
            <div v-else class="flex flex-col items-center text-gray-400">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
            </div>
            <input ref="inputFoto" type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="onFotoChange" />
          </div>
          <p class="text-xs text-gray-400 mt-2">Foto de perfil (opcional)</p>
          <button v-if="fotoArchivo" type="button" @click="quitarFoto" class="text-xs text-red-400 hover:text-red-600 mt-1">Quitar foto</button>
        </div>

        <form @submit.prevent="crearUsuario">
          <div class="mb-5">
            <label class="block text-gray-700 text-sm font-semibold mb-2">Nombre Completo</label>
            <input v-model="nuevoUsuario.nombre" type="text" class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none transition-all" placeholder="Ej. Juan Pérez" required>
          </div>
          <div class="mb-5">
            <label class="block text-gray-700 text-sm font-semibold mb-2">Documento de Identidad <span class="text-red-500">*</span></label>
            <input v-model="nuevoUsuario.documento_identidad" type="text" required minlength="5" maxlength="20" class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none transition-all" placeholder="Ej. 1020456789">
          </div>
          <div class="mb-5">
            <label class="block text-gray-700 text-sm font-semibold mb-2">Email</label>
            <input v-model="nuevoUsuario.email" type="email" class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none transition-all" placeholder="Ej. juan@correo.com" required>
          </div>
          <div class="mb-5">
            <label class="block text-gray-700 text-sm font-semibold mb-2">Contraseña</label>
            <input v-model="nuevoUsuario.password" type="password" class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none transition-all" placeholder="Min. 6 caracteres" required minlength="6">
          </div>
          <div class="mb-5">
            <label class="block text-gray-700 text-sm font-semibold mb-2">Teléfono / WhatsApp <span class="text-red-500">*</span></label>
            <input v-model="nuevoUsuario.telefono" type="tel" required minlength="7" class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none transition-all" placeholder="Ej. 3001234567">
          </div>
          <div class="mb-5">
            <label class="block text-gray-700 text-sm font-semibold mb-2">Género <span class="text-red-500">*</span></label>
            <div class="grid grid-cols-2 gap-3">
              <button
                type="button"
                @click="nuevoUsuario.genero = 'masculino'"
                class="py-3 rounded-xl border-2 font-bold text-sm transition-all"
                :class="nuevoUsuario.genero === 'masculino'
                  ? 'border-blue-600 bg-blue-600 text-white'
                  : 'border-gray-200 text-gray-500 hover:border-blue-300 hover:text-blue-600'"
              >
                Masculino
              </button>
              <button
                type="button"
                @click="nuevoUsuario.genero = 'femenino'"
                class="py-3 rounded-xl border-2 font-bold text-sm transition-all"
                :class="nuevoUsuario.genero === 'femenino'
                  ? 'border-purple-600 bg-purple-600 text-white'
                  : 'border-gray-200 text-gray-500 hover:border-purple-300 hover:text-purple-600'"
              >
                Femenino
              </button>
            </div>
          </div>
          <div class="mb-5">
            <label class="block text-gray-700 text-sm font-semibold mb-2">Fecha de nacimiento <span class="text-gray-400 font-normal">(opcional)</span></label>
            <input v-model="nuevoUsuario.fecha_nacimiento" type="date"
              class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none transition-all">
          </div>
          <div class="mb-6">
            <label class="block text-gray-700 text-sm font-semibold mb-2">Rol</label>
            <select v-model="nuevoUsuario.rol" class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none appearance-none transition-all">
              <option value="cliente">Cliente</option>
              <option value="coach">Coach</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <!-- Plan inicial -->
          <div class="border-t border-gray-100 pt-5 mb-6">
            <label class="block text-gray-700 text-sm font-semibold mb-3">Plan de Membresía <span class="text-gray-400 font-normal">(opcional)</span></label>
            <div class="grid grid-cols-2 gap-3">
              <label class="flex flex-col items-center p-3 rounded-xl border-2 cursor-pointer transition-all"
                :class="planSeleccionado === 'ninguno' ? 'border-red-500 bg-red-50' : 'border-gray-200 hover:border-gray-300'">
                <input type="radio" v-model="planSeleccionado" value="ninguno" class="sr-only">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mb-1" :class="planSeleccionado === 'ninguno' ? 'text-red-400' : 'text-gray-300'" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"/></svg>
                <span class="text-xs font-semibold" :class="planSeleccionado === 'ninguno' ? 'text-red-700' : 'text-gray-500'">Sin plan</span>
              </label>
              <label v-for="plan in planes" :key="plan.id"
                class="flex flex-col items-center p-3 rounded-xl border-2 cursor-pointer transition-all"
                :class="planSeleccionado === plan.id ? 'border-red-500 bg-red-50' : 'border-gray-200 hover:border-gray-300'">
                <input type="radio" v-model="planSeleccionado" :value="plan.id" class="sr-only">
                <span class="text-lg font-black" :class="planSeleccionado === plan.id ? 'text-red-600' : 'text-gray-700'">{{ plan.duracion_dias }}d</span>
                <span class="text-xs font-semibold" :class="planSeleccionado === plan.id ? 'text-red-700' : 'text-gray-600'">{{ plan.nombre }}</span>
                <span class="text-xs mt-0.5" :class="planSeleccionado === plan.id ? 'text-red-500' : 'text-gray-400'">${{ plan.precio.toLocaleString() }}</span>
              </label>
              <label class="flex flex-col items-center p-3 rounded-xl border-2 cursor-pointer transition-all col-span-2"
                :class="planSeleccionado === 'personalizado' ? 'border-red-500 bg-red-50' : 'border-gray-200 hover:border-gray-300'">
                <input type="radio" v-model="planSeleccionado" value="personalizado" class="sr-only">
                <span class="text-xs font-semibold" :class="planSeleccionado === 'personalizado' ? 'text-red-700' : 'text-gray-600'">Personalizado (días)</span>
              </label>
            </div>

            <div v-if="planSeleccionado === 'personalizado'" class="mt-3 grid grid-cols-2 gap-3">
              <div>
                <label class="block text-gray-600 text-xs font-semibold mb-1">Días de acceso</label>
                <input v-model.number="planPersonalizado.dias" type="number" min="1" max="365" class="w-full px-3 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none text-sm" placeholder="Ej. 7" required>
              </div>
              <div>
                <label class="block text-gray-600 text-xs font-semibold mb-1">Monto ($)</label>
                <input v-model.number="planPersonalizado.monto" type="number" min="0" step="any" class="w-full px-3 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none text-sm" placeholder="Ej. 30000" required>
              </div>
            </div>
            <div v-if="planSeleccionado !== 'ninguno' && planSeleccionado !== 'personalizado'" class="mt-3">
              <label class="block text-gray-600 text-xs font-semibold mb-1">Monto cobrado ($)</label>
              <input v-model.number="montoPlanDefault" type="number" min="0" step="1000"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none text-sm"
                :placeholder="'Sugerido: $' + (planes.find(p => p.id === planSeleccionado)?.precio?.toLocaleString() || '')">
            </div>

            <!-- Método de pago: visible cuando se elige cualquier plan -->
            <div v-if="planSeleccionado !== 'ninguno'" class="mt-3">
              <label class="block text-gray-600 text-xs font-semibold mb-1">Método de pago <span class="text-red-500">*</span></label>
              <div class="grid grid-cols-2 gap-2">
                <label class="flex items-center gap-2 p-2.5 rounded-lg border-2 cursor-pointer transition-all"
                  :class="metodoPago === 'efectivo' ? 'border-red-500 bg-red-50' : 'border-gray-200 hover:border-gray-300'">
                  <input type="radio" v-model="metodoPago" value="efectivo" class="sr-only">
                  <span class="text-sm font-semibold" :class="metodoPago === 'efectivo' ? 'text-red-700' : 'text-gray-600'">💵 Efectivo</span>
                </label>
                <label class="flex items-center gap-2 p-2.5 rounded-lg border-2 cursor-pointer transition-all"
                  :class="metodoPago === 'transferencia' ? 'border-red-500 bg-red-50' : 'border-gray-200 hover:border-gray-300'">
                  <input type="radio" v-model="metodoPago" value="transferencia" class="sr-only">
                  <span class="text-sm font-semibold" :class="metodoPago === 'transferencia' ? 'text-red-700' : 'text-gray-600'">🏦 Transferencia</span>
                </label>
              </div>
            </div>
          </div>

          <div class="flex justify-end gap-3 pt-4 border-t border-gray-100">
            <button @click="cerrarFormulario" type="button" class="px-5 py-2.5 rounded-lg text-gray-600 font-semibold hover:bg-gray-100 transition-colors">Cancelar</button>
            <button type="submit" :disabled="saving || !nuevoUsuario.genero" class="px-5 py-2.5 rounded-lg bg-red-600 hover:bg-red-700 text-white font-semibold shadow-md inline-flex items-center gap-2 transition-all active:scale-95 disabled:bg-red-300">
              <span v-if="saving" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
              {{ saving ? 'Guardando...' : 'Crear Usuario' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <!-- ── Modal: Buscar por Huella ── -->
  <div v-if="showVerifyModal" class="fixed inset-0 flex items-center justify-center bg-gray-900/70 backdrop-blur-sm z-50 p-4">
    <div class="bg-white rounded-2xl w-full max-w-sm shadow-2xl overflow-hidden">
      <div class="bg-gradient-to-r from-gray-700 to-gray-800 px-6 py-5 flex items-center gap-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M6.625 2.655A9 9 0 0119 11a1 1 0 11-2 0 7 7 0 00-9.625-6.492 1 1 0 11-.75-1.853zM4.662 4.959A1 1 0 014.75 6.37 6.97 6.97 0 003 11a1 1 0 11-2 0 8.97 8.97 0 012.25-5.953 1 1 0 011.412-.088z" clip-rule="evenodd"/>
          <path fill-rule="evenodd" d="M5 11a5 5 0 1110 0 1 1 0 11-2 0 3 3 0 10-6 0c0 1.677-.345 3.276-.968 4.729a1 1 0 11-1.838-.789A9.964 9.964 0 005 11z" clip-rule="evenodd"/>
        </svg>
        <h3 class="text-lg font-bold text-white">Buscar por Huella</h3>
        <button v-if="!verifyStatus?.espera" @click="cerrarVerify" class="ml-auto text-white/70 hover:text-white">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <div class="px-6 py-6 text-center">
        <!-- Encontrado -->
        <div v-if="verifyStatus?.encontrado && verifyStatus?.usuario" class="flex flex-col items-center gap-3">
          <div class="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
          </div>
          <p class="text-emerald-700 font-bold text-lg">Usuario identificado</p>
          <div class="w-full bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-left">
            <p class="text-xs text-gray-400 uppercase font-semibold mb-1">Nombre</p>
            <p class="font-bold text-gray-800 text-lg">{{ verifyStatus.usuario.nombre }}</p>
          </div>
          <div class="flex gap-3 w-full mt-1">
            <button @click="cerrarVerify" class="flex-1 py-2.5 rounded-xl border border-gray-200 text-gray-600 font-semibold hover:bg-gray-50 transition-colors">Cerrar</button>
            <button @click="irAlPerfil(verifyStatus.usuario.id)" class="flex-1 py-2.5 rounded-xl bg-gray-700 hover:bg-gray-800 text-white font-bold transition-colors">Ver perfil</button>
          </div>
        </div>

        <!-- No encontrado -->
        <div v-else-if="verifyStatus?.no_match" class="flex flex-col items-center gap-3">
          <div class="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <p class="text-amber-700 font-bold text-lg">Huella no reconocida</p>
          <p class="text-gray-400 text-sm">No hay ningún usuario registrado con esta huella.</p>
          <div class="flex gap-3 w-full mt-1">
            <button @click="cerrarVerify" class="flex-1 py-2.5 rounded-xl border border-gray-200 text-gray-600 font-semibold hover:bg-gray-50">Cerrar</button>
            <button @click="reiniciarVerify" class="flex-1 py-2.5 rounded-xl bg-gray-700 hover:bg-gray-800 text-white font-bold transition-colors">Reintentar</button>
          </div>
        </div>

        <!-- Error -->
        <div v-else-if="verifyStatus?.error" class="flex flex-col items-center gap-3">
          <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <p class="text-red-600 font-bold">Error</p>
          <p class="text-gray-500 text-sm">{{ verifyStatus.mensaje }}</p>
          <div class="flex gap-3 w-full mt-1">
            <button @click="cerrarVerify" class="flex-1 py-2.5 rounded-xl border border-gray-200 text-gray-600 font-semibold hover:bg-gray-50">Cerrar</button>
            <button @click="reiniciarVerify" class="flex-1 py-2.5 rounded-xl bg-gray-700 hover:bg-gray-800 text-white font-bold transition-colors">Reintentar</button>
          </div>
        </div>

        <!-- Esperando dedo -->
        <div v-else class="flex flex-col items-center gap-4">
          <div v-if="verifyBridgeError" class="w-full p-3 bg-amber-50 border border-amber-200 rounded-xl text-amber-700 text-sm">
            <p class="font-semibold">Bridge no disponible</p>
            <p class="mt-1">Asegúrate de que el bridge esté corriendo:<br>
              <code class="text-xs bg-amber-100 px-1 rounded">dotnet run --project servicio_biometrico/HuelleroBridge.csproj</code>
            </p>
          </div>
          <template v-else>
            <div class="relative w-20 h-20">
              <div class="absolute inset-0 rounded-full bg-gray-200 animate-ping opacity-40"></div>
              <div class="relative w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center border-2 border-gray-400">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-gray-700" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M6.625 2.655A9 9 0 0119 11a1 1 0 11-2 0 7 7 0 00-9.625-6.492 1 1 0 11-.75-1.853zM4.662 4.959A1 1 0 014.75 6.37 6.97 6.97 0 003 11a1 1 0 11-2 0 8.97 8.97 0 012.25-5.953 1 1 0 011.412-.088z" clip-rule="evenodd"/>
                  <path fill-rule="evenodd" d="M5 11a5 5 0 1110 0 1 1 0 11-2 0 3 3 0 10-6 0c0 1.677-.345 3.276-.968 4.729a1 1 0 11-1.838-.789A9.964 9.964 0 005 11z" clip-rule="evenodd"/>
                </svg>
              </div>
            </div>
            <p class="text-gray-700 font-semibold">Coloca el dedo en el lector</p>
            <p class="text-gray-400 text-sm">{{ verifyStatus?.mensaje || 'Cargando templates...' }}</p>
            <button @click="cerrarVerify" class="text-sm text-red-500 hover:text-red-700 font-medium">Cancelar</button>
          </template>
        </div>
      </div>
    </div>
  </div>

  <!-- ── Modal: Enrolamiento de Huella ── -->
  <div v-if="showEnrolModal" class="fixed inset-0 flex items-center justify-center bg-gray-900/70 backdrop-blur-sm z-50 p-4">
    <div class="bg-white rounded-2xl w-full max-w-sm shadow-2xl overflow-hidden">
      <div class="bg-gradient-to-r from-indigo-600 to-indigo-700 px-6 py-5 flex items-center gap-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M6.625 2.655A9 9 0 0119 11a1 1 0 11-2 0 7 7 0 00-9.625-6.492 1 1 0 11-.75-1.853zM4.662 4.959A1 1 0 014.75 6.37 6.97 6.97 0 003 11a1 1 0 11-2 0 8.97 8.97 0 012.25-5.953 1 1 0 011.412-.088z" clip-rule="evenodd"/>
          <path fill-rule="evenodd" d="M5 11a5 5 0 1110 0 1 1 0 11-2 0 3 3 0 10-6 0c0 1.677-.345 3.276-.968 4.729a1 1 0 11-1.838-.789A9.964 9.964 0 005 11z" clip-rule="evenodd"/>
        </svg>
        <div>
          <h3 class="text-lg font-bold text-white">Registrar Huella</h3>
          <p class="text-indigo-200 text-sm">{{ enrolTarget?.nombre }}</p>
        </div>
        <button v-if="!enrolStatus?.activo" @click="cerrarEnrolModal" class="ml-auto text-white/70 hover:text-white">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <div class="px-6 py-6 text-center">
        <!-- Completado -->
        <div v-if="enrolStatus?.completado" class="flex flex-col items-center gap-3">
          <div class="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
          </div>
          <p class="text-emerald-700 font-bold text-lg">Huella registrada</p>
          <p class="text-gray-500 text-sm">{{ enrolStatus.mensaje }}</p>
          <button @click="cerrarEnrolModal" class="mt-2 w-full py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white font-bold transition-colors">Cerrar</button>
        </div>

        <!-- Error -->
        <div v-else-if="enrolStatus?.error" class="flex flex-col items-center gap-3">
          <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </div>
          <p class="text-red-600 font-bold">Error en el enrolamiento</p>
          <p class="text-gray-500 text-sm">{{ enrolStatus.error }}</p>
          <div class="flex gap-3 w-full mt-2">
            <button @click="cerrarEnrolModal" class="flex-1 py-2.5 rounded-xl border border-gray-200 text-gray-600 font-semibold hover:bg-gray-50 transition-colors">Cancelar</button>
            <button @click="iniciarEnrolamiento" class="flex-1 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold transition-colors">Reintentar</button>
          </div>
        </div>

        <!-- En progreso -->
        <div v-else-if="enrolStatus?.activo" class="flex flex-col items-center gap-4">
          <!-- Icono huella animado -->
          <div class="relative w-20 h-20">
            <div class="absolute inset-0 rounded-full bg-indigo-100 animate-ping opacity-40"></div>
            <div class="relative w-20 h-20 bg-indigo-50 rounded-full flex items-center justify-center border-2 border-indigo-300">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-indigo-600" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M6.625 2.655A9 9 0 0119 11a1 1 0 11-2 0 7 7 0 00-9.625-6.492 1 1 0 11-.75-1.853zM4.662 4.959A1 1 0 014.75 6.37 6.97 6.97 0 003 11a1 1 0 11-2 0 8.97 8.97 0 012.25-5.953 1 1 0 011.412-.088z" clip-rule="evenodd"/>
                <path fill-rule="evenodd" d="M5 11a5 5 0 1110 0 1 1 0 11-2 0 3 3 0 10-6 0c0 1.677-.345 3.276-.968 4.729a1 1 0 11-1.838-.789A9.964 9.964 0 005 11z" clip-rule="evenodd"/>
              </svg>
            </div>
          </div>

          <!-- Progreso pasos -->
          <div class="flex gap-2">
            <div v-for="i in enrolStatus.total" :key="i"
              class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all"
              :class="i < enrolStatus.paso ? 'bg-emerald-500 text-white' :
                      i === enrolStatus.paso ? 'bg-indigo-600 text-white ring-4 ring-indigo-200' :
                      'bg-gray-100 text-gray-400'">
              {{ i < enrolStatus.paso ? '✓' : i }}
            </div>
          </div>

          <p class="text-gray-700 font-semibold">{{ enrolStatus.mensaje }}</p>
          <p class="text-gray-400 text-sm">Captura {{ enrolStatus.paso }} de {{ enrolStatus.total }}</p>

          <button @click="cancelarEnrolamiento" class="mt-1 text-sm text-red-500 hover:text-red-700 font-medium">Cancelar</button>
        </div>

        <!-- Inicio / bridge desconectado -->
        <div v-else class="flex flex-col items-center gap-4">
          <div v-if="enrolBridgeError" class="w-full p-3 bg-amber-50 border border-amber-200 rounded-xl text-amber-700 text-sm">
            <p class="font-semibold">Bridge no disponible</p>
            <p class="mt-1">Asegúrate de que el bridge esté corriendo:<br>
              <code class="text-xs bg-amber-100 px-1 rounded">dotnet run --project servicio_biometrico/HuelleroBridge.csproj</code>
            </p>
          </div>
          <div v-else>
            <p class="text-gray-500 text-sm mb-4">Se capturarán <strong>{{ ENROL_STEPS }} muestras</strong> del dedo del usuario.<br>Asegúrate de que el lector esté conectado.</p>
            <button @click="iniciarEnrolamiento" class="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-lg transition-colors flex items-center justify-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clip-rule="evenodd"/>
              </svg>
              Iniciar captura
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast: apertura de palanquera -->
    <div v-if="palanqueraToast"
         class="fixed bottom-6 right-6 z-50 px-5 py-3 rounded-xl shadow-2xl text-white font-semibold flex items-center gap-2 animate-fade-in-up"
         :class="palanqueraToast.ok ? 'bg-emerald-600' : 'bg-red-600'">
      <span>{{ palanqueraToast.ok ? '✅' : '⚠️' }}</span>
      {{ palanqueraToast.texto }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import api, { mediaUrl } from '../api'

const router = useRouter()
const BRIDGE_URL = 'http://localhost:8001'
const ENROL_STEPS = 4

// ── En gym ───────────────────────────────────────────────────
const enGym = ref([])
let gymInterval = null

const fetchEnGym = async () => {
  try { enGym.value = (await api.get('/asistencia/en-gym')).data } catch {}
}

// ── Estado ──────────────────────────────────────────────────
const usuarios = ref([])
const pendientes = ref([])
const planes = ref([])
const loading = ref(true)
const loadingPendientes = ref(false)
const usuarioSeleccionado = ref(null)
const filtroActivo = ref('todos')
const busqueda = ref('')

// ── Palanquera (apertura manual) ─────────────────────────────
const palanqueraAbriendo = ref(false)
const palanqueraToast    = ref(null)   // { ok: bool, texto: string }

const abrirPalanquera = async () => {
  palanqueraAbriendo.value = true
  try {
    const r = await fetch(`${BRIDGE_URL}/palanquera/abrir`, { method: 'POST' })
    if (!r.ok) throw new Error()
    palanqueraToast.value = { ok: true, texto: 'Palanquera abierta' }
  } catch {
    palanqueraToast.value = { ok: false, texto: 'No se pudo abrir. ¿El bridge está corriendo?' }
  } finally {
    palanqueraAbriendo.value = false
    setTimeout(() => { palanqueraToast.value = null }, 3500)
  }
}

// ── Verificación por huella ──────────────────────────────────
const showVerifyModal  = ref(false)
const verifyStatus     = ref(null)
const verifyBridgeError = ref(false)
let   verifyPollInterval = null

const abrirBuscarHuella = async () => {
  verifyStatus.value     = null
  verifyBridgeError.value = false
  showVerifyModal.value  = true
  try {
    await fetch(`${BRIDGE_URL}/verify/start`, { method: 'POST' })
    _iniciarPollVerify()
  } catch {
    verifyBridgeError.value = true
  }
}

const cerrarVerify = async () => {
  clearInterval(verifyPollInterval)
  verifyPollInterval = null
  try { await fetch(`${BRIDGE_URL}/verify`, { method: 'DELETE' }) } catch {}
  showVerifyModal.value = false
  verifyStatus.value    = null
}

const reiniciarVerify = async () => {
  clearInterval(verifyPollInterval)
  verifyStatus.value = null
  try {
    await fetch(`${BRIDGE_URL}/verify/start`, { method: 'POST' })
    _iniciarPollVerify()
  } catch {
    verifyBridgeError.value = true
  }
}

const irAlPerfil = (id) => {
  cerrarVerify()
  router.push(`/usuarios/${id}`)
}

const _pollVerify = async () => {
  try {
    const r    = await fetch(`${BRIDGE_URL}/status`)
    const data = await r.json()
    const v    = data.verificacion
    verifyStatus.value = v
    if (v.encontrado || v.no_match || v.error) {
      clearInterval(verifyPollInterval)
      verifyPollInterval = null
    }
  } catch {
    verifyBridgeError.value = true
    clearInterval(verifyPollInterval)
    verifyPollInterval = null
  }
}

const _iniciarPollVerify = () => {
  clearInterval(verifyPollInterval)
  _pollVerify()
  verifyPollInterval = setInterval(_pollVerify, 600)
}

// ── Enrolamiento de huella ────────────────────────────────────
const showEnrolModal = ref(false)
const enrolTarget = ref(null)
const enrolStatus = ref(null)
const enrolBridgeError = ref(false)
let enrolPollInterval = null

const abrirEnrolamiento = (usuario) => {
  enrolTarget.value = usuario
  enrolStatus.value = null
  enrolBridgeError.value = false
  showEnrolModal.value = true
  usuarioSeleccionado.value = null
}

const cerrarEnrolModal = () => {
  clearInterval(enrolPollInterval)
  enrolPollInterval = null
  showEnrolModal.value = false
  enrolTarget.value = null
  enrolStatus.value = null
  fetchUsuarios()
}

const iniciarEnrolamiento = async () => {
  if (!enrolTarget.value) return
  enrolBridgeError.value = false
  try {
    const nombre = encodeURIComponent(enrolTarget.value.nombre)
    await fetch(`${BRIDGE_URL}/enroll/${enrolTarget.value.id}?nombre=${nombre}`, { method: 'POST' })
    _iniciarPollEnrol()
  } catch {
    enrolBridgeError.value = true
  }
}

const cancelarEnrolamiento = async () => {
  try { await fetch(`${BRIDGE_URL}/enroll`, { method: 'DELETE' }) } catch {}
  clearInterval(enrolPollInterval)
  enrolPollInterval = null
  enrolStatus.value = null
}

const _pollStatus = async () => {
  try {
    const r = await fetch(`${BRIDGE_URL}/status`)
    const data = await r.json()
    const e = data.enrolamiento
    enrolStatus.value = e
    if (e.completado || (e.error && !e.activo)) {
      clearInterval(enrolPollInterval)
      enrolPollInterval = null
    }
  } catch {
    enrolBridgeError.value = true
    clearInterval(enrolPollInterval)
    enrolPollInterval = null
  }
}

const _iniciarPollEnrol = () => {
  clearInterval(enrolPollInterval)
  _pollStatus()
  enrolPollInterval = setInterval(_pollStatus, 600)
}

// ── Filtros ──────────────────────────────────────────────────
const hoy = () => { const d = new Date(); d.setHours(0,0,0,0); return d }

const tieneMembresia = (u) => {
  if (!u.fecha_vencimiento) return false
  return new Date(u.fecha_vencimiento + 'T00:00:00') >= hoy()
}

const usuariosFiltrados = computed(() => {
  let lista = usuarios.value
  if (filtroActivo.value === 'activos')   lista = lista.filter(u => u.esta_en_gym)
  if (filtroActivo.value === 'membresia') lista = lista.filter(tieneMembresia)
  const q = busqueda.value.trim().toLowerCase()
  if (q) lista = lista.filter(u =>
    u.nombre.toLowerCase().includes(q) ||
    u.documento_identidad?.toLowerCase().includes(q)
  )
  return lista
})

const tabs = computed(() => [
  { key: 'todos',      label: 'Todos',              count: usuarios.value.length,                             emptyMsg: 'No hay usuarios registrados.' },
  { key: 'membresia',  label: 'Con membresía',       count: usuarios.value.filter(tieneMembresia).length,     emptyMsg: 'Ningún usuario tiene membresía activa.' },
  { key: 'activos',    label: 'En el box ahora',     count: usuarios.value.filter(u => u.esta_en_gym).length, emptyMsg: 'No hay usuarios en el box en este momento.' },
  { key: 'pendientes', label: 'Pendientes',          count: pendientes.value.length,                          emptyMsg: 'No hay usuarios pendientes.' },
])

// ── Crear ────────────────────────────────────────────────────
const showForm = ref(false)
const saving = ref(false)
const nuevoUsuario = ref({ nombre: '', documento_identidad: '', email: '', password: '', rol: 'cliente', telefono: '', genero: '', fecha_nacimiento: '' })
const planSeleccionado = ref('ninguno')
const montoPlanDefault = ref('')
const planPersonalizado = ref({ dias: '', monto: '' })
const metodoPago = ref('efectivo')
const fotoArchivo = ref(null)
const fotoPreview = ref(null)

// ── Editar ───────────────────────────────────────────────────
const showEditar = ref(false)
const guardandoEdicion = ref(false)
const editando = ref(null)
const editForm = ref({ email: '', password: '', telefono: '', genero: '' })
const editFotoArchivo = ref(null)
const editFotoPreview = ref(null)

// ── Activar pendiente ─────────────────────────────────────────
const showActivar = ref(false)
const activarUsuario = ref(null)
const activarPlan = ref(null)
const activarMonto = ref('')
const activarMetodo = ref('efectivo')
const guardandoActivar = ref(false)
const errorActivar = ref('')

const abrirActivar = (u) => {
  activarUsuario.value = u
  activarPlan.value = u.plan_solicitado_id || null
  activarMonto.value = u.plan_solicitado?.precio || ''
  activarMetodo.value = 'efectivo'
  errorActivar.value = ''
  showActivar.value = true
}

const confirmarActivar = async () => {
  if (!activarPlan.value) return
  guardandoActivar.value = true
  errorActivar.value = ''
  try {
    await api.post(`/usuarios/${activarUsuario.value.id}/activar`, {
      plan_id: activarPlan.value,
      monto: activarMonto.value || 0,
      metodo_pago: activarMetodo.value,
    })
    showActivar.value = false
    await fetchPendientes()
    await fetchUsuarios()
  } catch (e) {
    errorActivar.value = e.response?.data?.detail || 'Error al activar el usuario.'
  } finally {
    guardandoActivar.value = false
  }
}

// ── Renovar ──────────────────────────────────────────────────
const showRenovar = ref(false)
const guardandoRenovar = ref(false)
const renovarUsuario = ref(null)
const renovarPlan = ref(null)
const renovarDias = ref('')
const renovarMonto = ref('')
const renovarMetodo = ref('efectivo')
const errorRenovar = ref('')

const metodos = [
  { value: 'efectivo', label: 'Efectivo' },
  { value: 'transferencia', label: 'Transferencia' },
]

const planSeleccionadoObj = computed(() =>
  renovarPlan.value && renovarPlan.value !== 'personalizado'
    ? planes.value.find(p => p.id === renovarPlan.value) || null
    : null
)

// ── Helpers ──────────────────────────────────────────────────
const fotoSrc = (user, size = 40) =>
  user.foto_url
    ? mediaUrl(user.foto_url)
    : `https://ui-avatars.com/api/?name=${encodeURIComponent(user.nombre)}&background=random&size=${size}`

const formatFecha = (f) =>
  new Date(f + 'T12:00:00').toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric' })

const formatFechaCorta = (f) =>
  new Date(f).toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric' })

const diasRestantes = (fecha) => {
  const hoy = new Date()
  hoy.setHours(0, 0, 0, 0)
  const vence = new Date(fecha + 'T00:00:00')
  return Math.ceil((vence - hoy) / (1000 * 60 * 60 * 24))
}

const etiquetaDias = (dias) => {
  if (dias > 1) return `${dias} días restantes`
  if (dias === 1) return 'Vence mañana'
  if (dias === 0) return 'Vence hoy'
  return `Vencida hace ${Math.abs(dias)} día${Math.abs(dias) !== 1 ? 's' : ''}`
}

const colorTextoDias = (dias) => {
  if (dias > 7) return 'text-emerald-600'
  if (dias > 0) return 'text-amber-600'
  return 'text-red-600'
}

const colorPuntoDias = (dias) => {
  if (dias > 7) return 'bg-emerald-500'
  if (dias > 0) return 'bg-amber-500'
  return 'bg-red-500'
}

const bgCirculoDias = (dias) => {
  if (dias > 7) return 'bg-emerald-100'
  if (dias > 0) return 'bg-amber-100'
  return 'bg-red-100'
}

// ── Fetch ────────────────────────────────────────────────────
const fetchUsuarios = async () => {
  loading.value = true
  try { usuarios.value = (await api.get('/usuarios/')).data }
  catch (e) { console.error(e) }
  finally { loading.value = false }
}

const fetchPlanes = async () => {
  try { planes.value = (await api.get('/planes/')).data }
  catch (e) { console.error(e) }
}

const fetchPendientes = async () => {
  loadingPendientes.value = true
  try { pendientes.value = (await api.get('/usuarios/pendientes')).data }
  catch (e) { console.error(e) }
  finally { loadingPendientes.value = false }
}

// ── Ver ──────────────────────────────────────────────────────
const verUsuario = (u) => { router.push(`/usuarios/${u.id}`) }

// ── Renovar ──────────────────────────────────────────────────
const abrirRenovar = (user) => {
  renovarUsuario.value = user
  renovarPlan.value = null
  renovarDias.value = ''
  renovarMonto.value = ''
  renovarMetodo.value = 'efectivo'
  errorRenovar.value = ''
  showRenovar.value = true
}

const confirmarRenovacion = async () => {
  if (!renovarPlan.value) return
  guardandoRenovar.value = true
  errorRenovar.value = ''
  try {
    const id = renovarUsuario.value.id
    if (renovarPlan.value === 'personalizado') {
      if (!renovarDias.value || renovarDias.value < 1) {
        errorRenovar.value = 'Ingresa un número de días válido.'
        return
      }
      await api.post('/pagos/directo/', {
        usuario_id: id,
        duracion_dias: renovarDias.value,
        monto: renovarMonto.value || 0,
        metodo_pago: renovarMetodo.value,
      })
    } else {
      const plan = planes.value.find(p => p.id === renovarPlan.value)
      await api.post('/pagos/', {
        usuario_id: id,
        plan_id: renovarPlan.value,
        monto: renovarMonto.value || plan?.precio || 0,
        metodo_pago: renovarMetodo.value,
      })
    }
    showRenovar.value = false
    await fetchUsuarios()
  } catch (e) {
    errorRenovar.value = e.response?.data?.detail || 'Error al renovar la membresía.'
  } finally {
    guardandoRenovar.value = false
  }
}

// ── Crear ────────────────────────────────────────────────────
const cerrarFormulario = () => {
  showForm.value = false
  nuevoUsuario.value = { nombre: '', documento_identidad: '', email: '', password: '', rol: 'cliente', telefono: '', genero: '', fecha_nacimiento: '' }
  planSeleccionado.value = 'ninguno'
  montoPlanDefault.value = ''
  planPersonalizado.value = { dias: '', monto: '' }
  metodoPago.value = 'efectivo'
  fotoArchivo.value = null
  fotoPreview.value = null
}

const onFotoChange = (e) => {
  const f = e.target.files[0]
  if (!f) return
  fotoArchivo.value = f
  fotoPreview.value = URL.createObjectURL(f)
}

const quitarFoto = () => { fotoArchivo.value = null; fotoPreview.value = null }

const crearUsuario = async () => {
  saving.value = true
  try {
    const payload = { ...nuevoUsuario.value }
    if (!payload.fecha_nacimiento) payload.fecha_nacimiento = null
    const { data: nuevo } = await api.post('/usuarios/', payload)

    if (fotoArchivo.value) {
      const fd = new FormData()
      fd.append('foto', fotoArchivo.value)
      await api.post(`/usuarios/${nuevo.id}/foto`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    }

    if (planSeleccionado.value === 'personalizado') {
      await api.post('/pagos/directo/', {
        usuario_id: nuevo.id,
        duracion_dias: planPersonalizado.value.dias,
        monto: planPersonalizado.value.monto,
        metodo_pago: metodoPago.value,
      })
    } else if (planSeleccionado.value !== 'ninguno') {
      const plan = planes.value.find(p => p.id === planSeleccionado.value)
      await api.post('/pagos/', {
        usuario_id: nuevo.id,
        plan_id: planSeleccionado.value,
        monto: montoPlanDefault.value || plan?.precio || 0,
        metodo_pago: metodoPago.value,
      })
    }

    cerrarFormulario()
    await fetchUsuarios()
  } catch (e) {
    const d = e.response?.data?.detail
    alert('Error: ' + (Array.isArray(d) ? d[0].msg : (d || e.message)))
  } finally {
    saving.value = false
  }
}

// ── Editar ───────────────────────────────────────────────────
const confirmarEliminar = async (user) => {
  if (!confirm(`¿Eliminar a ${user.nombre}? Esta acción no se puede deshacer.`)) return
  try {
    await api.delete(`/usuarios/${user.id}`)
    usuarioSeleccionado.value = null
    await fetchUsuarios()
  } catch (e) {
    const d = e.response?.data?.detail
    alert('Error: ' + (Array.isArray(d) ? d[0].msg : (d || e.message)))
  }
}

const abrirEditar = (user) => {
  editando.value = user
  editForm.value = { email: user.email, password: '', telefono: user.telefono || '', genero: user.genero || '' }
  editFotoArchivo.value = null
  editFotoPreview.value = null
  showEditar.value = true
}

const cerrarEditar = () => {
  showEditar.value = false
  editando.value = null
  editFotoArchivo.value = null
  editFotoPreview.value = null
}

const onFotoEditChange = (e) => {
  const f = e.target.files[0]
  if (!f) return
  editFotoArchivo.value = f
  editFotoPreview.value = URL.createObjectURL(f)
}

const guardarEdicion = async () => {
  guardandoEdicion.value = true
  try {
    const id = editando.value.id
    const payload = { email: editForm.value.email, telefono: editForm.value.telefono || null }
    if (editForm.value.password) payload.password = editForm.value.password
    if (editForm.value.genero) payload.genero = editForm.value.genero
    await api.patch(`/usuarios/${id}`, payload)

    if (editFotoArchivo.value) {
      const fd = new FormData()
      fd.append('foto', editFotoArchivo.value)
      await api.post(`/usuarios/${id}/foto`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    }

    cerrarEditar()
    await fetchUsuarios()
  } catch (e) {
    const d = e.response?.data?.detail
    alert('Error: ' + (Array.isArray(d) ? d[0].msg : (d || e.message)))
  } finally {
    guardandoEdicion.value = false
  }
}

// ── WebSocket: actualización en tiempo real del estado en gym ──
// El bridge .NET hace broadcast de eventos "acceso_ok" cada vez que registra
// una entrada/salida. Escuchamos ese socket y patcheamos solo el usuario
// afectado en la lista local — no recargamos toda la tabla.
let accesoWS = null
let accesoReconnectTimer = null

const aplicarEventoAcceso = (data) => {
  if (data?.tipo !== 'acceso_ok' || !data.usuario_id) return
  const u = usuarios.value.find(x => x.id === data.usuario_id)
  if (u) u.esta_en_gym = data.evento === 'entrada'
}

const conectarAccesoWS = () => {
  try {
    accesoWS = new WebSocket('ws://localhost:8765')
    accesoWS.onmessage = (ev) => {
      try { aplicarEventoAcceso(JSON.parse(ev.data)) } catch {}
    }
    accesoWS.onclose = () => {
      accesoWS = null
      // Reintento suave por si el bridge se reinicia.
      accesoReconnectTimer = setTimeout(conectarAccesoWS, 4000)
    }
    accesoWS.onerror = () => { try { accesoWS?.close() } catch {} }
  } catch {
    accesoReconnectTimer = setTimeout(conectarAccesoWS, 4000)
  }
}

// ── Cumpleaños hoy ───────────────────────────────────────────
const cumpleaneros = ref([])
const cumpleanosExpandido = ref(true)

function whatsappCumpleanos(u) {
  const tel = '57' + u.telefono.replace(/\D/g, '')
  const msg = `¡Feliz cumpleaños ${u.nombre.split(' ')[0]}! 🎂🎉 De parte de todo el equipo del Box te deseamos un excelente día. Pasa hoy por el box y reclama tu batido gratis 🥤`
  return `https://wa.me/${tel}?text=${encodeURIComponent(msg)}`
}

async function fetchCumpleaneros() {
  try {
    const { data } = await api.get('/usuarios/cumpleanos-hoy')
    cumpleaneros.value = data
  } catch {
    cumpleaneros.value = []
  }
}

onMounted(() => {
  fetchUsuarios()
  fetchPlanes()
  fetchPendientes()
  fetchCumpleaneros()
  conectarAccesoWS()
  fetchEnGym()
  gymInterval = setInterval(fetchEnGym, 10_000)
})
onUnmounted(() => {
  clearInterval(enrolPollInterval)
  clearInterval(gymInterval)
  clearTimeout(accesoReconnectTimer)
  try { accesoWS?.close() } catch {}
})
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
