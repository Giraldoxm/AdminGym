<template>
  <div class="animate-fade-in-up">

    <!-- ── Header ── -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
      <div>
        <h2 class="text-3xl font-extrabold text-gray-900 tracking-tight">
          {{ canManage ? 'Tienda' : 'Catálogo' }}
        </h2>
        <p class="text-gray-500 mt-1">
          {{ canManage ? 'Gestión de inventario y punto de venta' : 'Productos disponibles en el box' }}
        </p>
      </div>
      <button v-if="canManage" @click="abrirCrear()"
        class="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white font-bold py-2.5 px-5 rounded-lg shadow transition-colors">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Nuevo producto
      </button>
    </div>

    <!-- ── Tabs (solo admin/coach) ── -->
    <div v-if="canManage" class="flex gap-1 bg-gray-100 p-1 rounded-xl w-fit mb-6">
      <button @click="tabActivo = 'inventario'"
        class="px-5 py-2 rounded-lg text-sm font-bold transition-all"
        :class="tabActivo === 'inventario' ? 'bg-white shadow text-gray-900' : 'text-gray-500 hover:text-gray-700'">
        Inventario
      </button>
      <button @click="tabActivo = 'pos'"
        class="px-5 py-2 rounded-lg text-sm font-bold transition-all"
        :class="tabActivo === 'pos' ? 'bg-white shadow text-gray-900' : 'text-gray-500 hover:text-gray-700'">
        Punto de Venta
        <span v-if="totalCarrito > 0"
          class="ml-2 bg-red-600 text-white text-xs font-black px-2 py-0.5 rounded-full">
          {{ totalCarrito }}
        </span>
      </button>
    </div>

    <!-- ════════════════════════════════════════
         TAB: INVENTARIO (admin/coach)
    ════════════════════════════════════════ -->
    <div v-if="canManage && tabActivo === 'inventario'">
      <!-- Filtro de búsqueda -->
      <div class="flex gap-3 mb-5">
        <div class="relative flex-1 max-w-sm">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 absolute left-3 top-3 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          <input v-model="busqueda" type="text" placeholder="Buscar producto..."
            class="w-full pl-9 pr-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 outline-none text-sm">
        </div>
      </div>

      <!-- Grid productos inventario -->
      <div v-if="cargando" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
        <div v-for="i in 8" :key="i" class="bg-white rounded-2xl h-72 animate-pulse border border-gray-100"></div>
      </div>

      <div v-else-if="productosFiltrados.length === 0" class="bg-gray-50 border-2 border-dashed border-gray-200 rounded-2xl p-14 text-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-14 w-14 mx-auto text-gray-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
        </svg>
        <p class="text-gray-500 font-medium">No hay productos en el inventario.</p>
        <button @click="abrirCrear()" class="mt-4 text-red-600 font-semibold hover:underline text-sm">
          + Agregar el primero
        </button>
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
        <div v-for="p in productosFiltrados" :key="p.id"
          class="bg-white rounded-2xl border border-gray-100 overflow-hidden group transition-shadow hover:shadow-md">

          <!-- Foto -->
          <div class="relative h-44 bg-gray-50 flex items-center justify-center overflow-hidden">
            <img v-if="p.foto_url" :src="mediaUrl(p.foto_url)"
              class="w-full h-full object-cover" :alt="p.nombre" />
            <div v-else class="flex flex-col items-center text-gray-300">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-14 w-14" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
              <span class="text-xs mt-1">Sin foto</span>
            </div>
            <!-- Badges -->
            <div class="absolute top-2 left-2 flex gap-1.5">
              <span v-if="p.stock === 0" class="bg-gray-800 text-white text-xs font-bold px-2 py-0.5 rounded-full">Agotado</span>
              <span v-else-if="p.stock <= 5" class="bg-amber-400 text-white text-xs font-bold px-2 py-0.5 rounded-full">Poco stock</span>
            </div>
            <!-- Acciones overlay -->
            <div class="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-all flex items-center justify-center gap-3 opacity-0 group-hover:opacity-100">
              <button @click="abrirEditar(p)" title="Editar"
                class="w-9 h-9 bg-white rounded-full flex items-center justify-center shadow-lg hover:bg-red-50 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
                </svg>
              </button>
              <button @click="confirmarEliminar(p)" title="Eliminar"
                class="w-9 h-9 bg-white rounded-full flex items-center justify-center shadow-lg hover:bg-red-50 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
            </div>
          </div>

          <div class="p-4">
            <div class="flex items-start justify-between gap-2 mb-1">
              <p class="font-bold text-gray-800 truncate flex-1">{{ p.nombre }}</p>
              <span v-if="p.categoria" class="text-xs bg-red-50 text-red-600 px-2 py-0.5 rounded-full font-medium whitespace-nowrap">{{ p.categoria }}</span>
            </div>
            <p class="text-xs text-gray-400 line-clamp-1 mb-3">{{ p.descripcion || 'Sin descripción' }}</p>
            <div class="flex items-center justify-between">
              <span class="text-lg font-black text-red-600">${{ p.precio.toLocaleString('es-CO') }}</span>
              <span class="text-sm font-semibold" :class="p.stock > 5 ? 'text-emerald-600' : p.stock > 0 ? 'text-amber-500' : 'text-red-500'">
                Stock: {{ p.stock }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ════════════════════════════════════════
         TAB: POS (admin/coach) + CATÁLOGO (cliente)
    ════════════════════════════════════════ -->
    <div v-if="!canManage || tabActivo === 'pos'" class="flex flex-col lg:flex-row gap-6">

      <!-- Productos -->
      <div class="flex-1 min-w-0">
        <!-- Filtro categorías -->
        <div v-if="categorias.length > 0" class="flex flex-wrap gap-2 mb-5">
          <button @click="categoriaFiltro = null"
            class="px-3 py-1.5 rounded-full text-sm font-semibold transition-colors"
            :class="categoriaFiltro === null ? 'bg-gray-900 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:border-gray-400'">
            Todos
          </button>
          <button v-for="cat in categorias" :key="cat" @click="categoriaFiltro = cat"
            class="px-3 py-1.5 rounded-full text-sm font-semibold transition-colors"
            :class="categoriaFiltro === cat ? 'bg-gray-900 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:border-gray-400'">
            {{ cat }}
          </button>
        </div>

        <!-- Grid -->
        <div v-if="cargando" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="i in 6" :key="i" class="bg-white rounded-2xl h-72 animate-pulse border border-gray-100"></div>
        </div>

        <div v-else-if="productosActivos.length === 0"
          class="bg-gray-50 border-2 border-dashed border-gray-200 rounded-2xl p-14 text-center text-gray-400">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-14 w-14 mx-auto text-gray-200 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/>
          </svg>
          No hay productos disponibles.
        </div>

        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="p in productosActivos" :key="p.id"
            class="bg-white rounded-2xl border border-gray-100 overflow-hidden hover:shadow-md transition-shadow group">

            <!-- Foto -->
            <div class="relative h-40 bg-gray-50 overflow-hidden">
              <img v-if="p.foto_url" :src="mediaUrl(p.foto_url)"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
              <div v-else class="w-full h-full flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
              </div>
              <div v-if="canManage" class="absolute top-2 right-2">
                <span class="text-xs font-bold px-2 py-0.5 rounded-full"
                  :class="p.stock > 5 ? 'bg-emerald-100 text-emerald-700' : p.stock > 0 ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-600'">
                  {{ p.stock > 0 ? `${p.stock} disp.` : 'Agotado' }}
                </span>
              </div>
            </div>

            <div class="p-4">
              <div class="flex items-start gap-2 mb-1">
                <p class="font-bold text-gray-800 flex-1 truncate">{{ p.nombre }}</p>
                <span v-if="p.categoria && canManage" class="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full whitespace-nowrap">{{ p.categoria }}</span>
              </div>
              <p v-if="canManage" class="text-xs text-gray-400 line-clamp-2 mb-3 min-h-[32px]">{{ p.descripcion || '' }}</p>
              <div class="flex items-center justify-between" :class="canManage ? '' : 'mt-2'">
                <span v-if="canManage" class="text-xl font-black text-red-600">${{ p.precio.toLocaleString('es-CO') }}</span>
                <span v-else class="text-sm font-semibold"
                  :class="p.stock > 5 ? 'text-emerald-600' : p.stock > 0 ? 'text-amber-500' : 'text-red-500'">
                  {{ p.stock > 0 ? `${p.stock} disponible${p.stock !== 1 ? 's' : ''}` : 'Agotado' }}
                </span>
                <button v-if="canManage" @click="agregarAlCarrito(p)" :disabled="p.stock === 0"
                  class="flex items-center gap-1.5 text-sm font-bold px-3 py-1.5 rounded-lg transition-colors"
                  :class="p.stock > 0
                    ? 'bg-red-600 hover:bg-red-700 text-white'
                    : 'bg-gray-100 text-gray-400 cursor-not-allowed'">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                  </svg>
                  Agregar
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Carrito (solo admin/coach) ── -->
      <div v-if="canManage" class="w-full lg:w-80 lg:flex-shrink-0">
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm lg:sticky lg:top-6">
          <div class="p-5 border-b border-gray-100">
            <h3 class="font-bold text-gray-800 flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"/>
              </svg>
              Carrito
              <span v-if="totalCarrito > 0" class="ml-auto bg-red-100 text-red-700 text-xs font-black px-2 py-0.5 rounded-full">
                {{ totalCarrito }} ítem{{ totalCarrito !== 1 ? 's' : '' }}
              </span>
            </h3>
          </div>

          <!-- Items carrito -->
          <div class="p-4 space-y-3 max-h-64 overflow-y-auto">
            <p v-if="carrito.length === 0" class="text-sm text-gray-400 text-center py-6">
              El carrito está vacío.<br>
              <span class="text-xs">Agrega productos desde el catálogo.</span>
            </p>
            <div v-for="item in carrito" :key="item.producto.id"
              class="flex items-center gap-3 bg-gray-50 rounded-xl p-3">
              <div class="w-10 h-10 rounded-lg overflow-hidden bg-gray-200 flex-shrink-0">
                <img v-if="item.producto.foto_url" :src="mediaUrl(item.producto.foto_url)"
                  class="w-full h-full object-cover" />
                <div v-else class="w-full h-full flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/>
                  </svg>
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-xs font-bold text-gray-700 truncate">{{ item.producto.nombre }}</p>
                <p class="text-xs text-gray-400">${{ item.producto.precio.toLocaleString('es-CO') }} c/u</p>
              </div>
              <div class="flex items-center gap-1">
                <button @click="ajustarCantidad(item, -1)"
                  class="w-6 h-6 rounded-full bg-gray-200 hover:bg-red-100 hover:text-red-600 flex items-center justify-center text-sm font-bold transition-colors">−</button>
                <span class="w-6 text-center text-sm font-bold text-gray-700">{{ item.cantidad }}</span>
                <button @click="ajustarCantidad(item, 1)"
                  :disabled="item.cantidad >= item.producto.stock"
                  class="w-6 h-6 rounded-full bg-gray-200 hover:bg-red-100 hover:text-red-600 flex items-center justify-center text-sm font-bold transition-colors disabled:opacity-40">+</button>
              </div>
            </div>
          </div>

          <!-- Total y acciones -->
          <div v-if="carrito.length > 0" class="px-4 pb-4 border-t border-gray-100 pt-4">

            <!-- Método de pago -->
            <div class="mb-4">
              <p class="text-xs font-semibold text-gray-600 mb-2">Método de pago *</p>
              <div class="grid grid-cols-2 gap-2">
                <label v-for="m in metodosPago" :key="m.value"
                  class="flex items-center justify-center gap-1.5 p-2.5 rounded-lg border-2 cursor-pointer transition-all text-sm font-semibold"
                  :class="metodoPagoVenta === m.value
                    ? 'border-red-600 bg-red-50 text-red-700'
                    : 'border-gray-200 text-gray-600 hover:border-gray-300'">
                  <input type="radio" v-model="metodoPagoVenta" :value="m.value" class="sr-only">
                  <svg v-if="m.value === 'efectivo'" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z"/></svg>
                  {{ m.label }}
                </label>
              </div>
            </div>

            <div class="flex items-center justify-between mb-4">
              <span class="text-sm font-semibold text-gray-600">Total</span>
              <span class="text-xl font-black text-gray-900">${{ totalVenta.toLocaleString('es-CO') }}</span>
            </div>

            <div v-if="errorVenta" class="text-xs text-red-600 bg-red-50 rounded-lg p-2 mb-3">{{ errorVenta }}</div>

            <button @click="registrarVenta" :disabled="procesandoVenta || !metodoPagoVenta"
              class="w-full py-3 rounded-xl bg-red-600 hover:bg-red-700 text-white font-bold transition-colors disabled:bg-red-300 flex items-center justify-center gap-2">
              <span v-if="procesandoVenta" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              {{ procesandoVenta ? 'Procesando...' : 'Registrar venta' }}
            </button>

            <button @click="limpiarCarrito" class="w-full mt-2 py-2 text-sm text-gray-400 hover:text-red-500 transition-colors">
              Vaciar carrito
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ════════════════════════════════════════
         MODAL: Crear / Editar Producto
    ════════════════════════════════════════ -->
    <div v-if="mostrarModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[92vh] overflow-y-auto">
        <div class="p-6 border-b border-gray-100 flex items-center justify-between">
          <h3 class="text-lg font-bold text-gray-800">
            {{ editandoProducto ? 'Editar producto' : 'Nuevo producto' }}
          </h3>
          <button @click="cerrarModal" class="p-2 rounded-lg hover:bg-gray-100 text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <form @submit.prevent="guardarProducto" class="p-6 space-y-4">

          <!-- Foto -->
          <div class="flex flex-col items-center">
            <div class="relative w-full h-40 rounded-xl overflow-hidden border-2 border-dashed border-gray-200 bg-gray-50 cursor-pointer hover:border-red-400 hover:bg-red-50 transition-all"
              @click="$refs.inputFoto.click()">
              <img v-if="fotoPreview || (editandoProducto?.foto_url && !fotoArchivo)"
                :src="fotoPreview || mediaUrl(editandoProducto.foto_url)"
                class="w-full h-full object-cover" />
              <div v-else class="w-full h-full flex flex-col items-center justify-center text-gray-400">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
                <span class="text-sm font-medium">Clic para subir foto</span>
                <span class="text-xs mt-1">JPG, PNG o WEBP</span>
              </div>
              <input ref="inputFoto" type="file" accept="image/jpeg,image/png,image/webp"
                class="hidden" @change="onFotoChange" />
            </div>
            <button v-if="fotoArchivo" type="button" @click="fotoArchivo = null; fotoPreview = null"
              class="mt-1 text-xs text-red-400 hover:text-red-600">Quitar foto</button>
          </div>

          <!-- Nombre -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">Nombre *</label>
            <input v-model="form.nombre" type="text" required placeholder="Ej: Proteína Whey 1kg"
              class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none">
          </div>

          <!-- Descripción -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">Descripción</label>
            <textarea v-model="form.descripcion" rows="2" placeholder="Descripción del producto..."
              class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none resize-none text-sm"></textarea>
          </div>

          <!-- Precio y Stock -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1.5">Precio ($) *</label>
              <input v-model.number="form.precio" type="number" min="0" step="1" required
                placeholder="Ej: 45000"
                class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none">
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1.5">Stock *</label>
              <input v-model.number="form.stock" type="number" min="0" required
                placeholder="Ej: 20"
                class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none">
            </div>
          </div>

          <!-- Categoría -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">Categoría</label>
            <input v-model="form.categoria" type="text" list="lista-categorias"
              placeholder="Ej: Suplementos, Ropa, Accesorios"
              class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none">
            <datalist id="lista-categorias">
              <option v-for="cat in categoriasTodas" :key="cat" :value="cat" />
            </datalist>
          </div>

          <div v-if="errorForm" class="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg p-3">{{ errorForm }}</div>

          <div class="flex gap-3 pt-2">
            <button type="button" @click="cerrarModal"
              class="flex-1 py-2.5 rounded-xl border border-gray-300 text-gray-600 font-semibold hover:bg-gray-50 transition-colors">
              Cancelar
            </button>
            <button type="submit" :disabled="guardando"
              class="flex-1 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white font-bold transition-colors disabled:bg-red-300 flex items-center justify-center gap-2">
              <span v-if="guardando" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
              {{ guardando ? 'Guardando...' : (editandoProducto ? 'Actualizar' : 'Crear producto') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ── Toast de éxito ── -->
    <Transition enter-from-class="opacity-0 translate-y-4" enter-active-class="transition-all duration-300" leave-to-class="opacity-0 translate-y-4" leave-active-class="transition-all duration-300">
      <div v-if="toast" class="fixed bottom-6 right-6 bg-gray-900 text-white px-5 py-3 rounded-xl shadow-2xl flex items-center gap-3 z-50">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-emerald-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
        </svg>
        <span class="text-sm font-semibold">{{ toast }}</span>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api, { mediaUrl } from '../api'
import { useAuth } from '../composables/useAuth'

const { canManage } = useAuth()

// ── Estado ───────────────────────────────────────────────────
const productos = ref([])
const cargando = ref(true)
const tabActivo = ref('inventario')
const busqueda = ref('')
const categoriaFiltro = ref(null)
const toast = ref('')

// ── Modal producto ────────────────────────────────────────────
const mostrarModal = ref(false)
const editandoProducto = ref(null)
const guardando = ref(false)
const errorForm = ref('')
const fotoArchivo = ref(null)
const fotoPreview = ref(null)

const formVacio = () => ({ nombre: '', descripcion: '', precio: '', stock: 0, categoria: '' })
const form = ref(formVacio())

// ── Carrito POS ───────────────────────────────────────────────
const carrito = ref([])
const metodoPagoVenta = ref(null)
const procesandoVenta = ref(false)
const errorVenta = ref('')

const metodosPago = [
  { value: 'efectivo',      label: 'Efectivo' },
  { value: 'transferencia', label: 'Transferencia' },
]

// ── Computed ──────────────────────────────────────────────────
const productosFiltrados = computed(() => {
  return productos.value.filter(p => {
    if (!p.activo) return false
    if (busqueda.value && !p.nombre.toLowerCase().includes(busqueda.value.toLowerCase())) return false
    return true
  })
})

const productosActivos = computed(() => {
  return productos.value.filter(p => {
    if (!p.activo) return false
    if (categoriaFiltro.value && p.categoria !== categoriaFiltro.value) return false
    return true
  })
})

const categorias = computed(() => {
  const cats = [...new Set(productos.value.filter(p => p.activo && p.categoria).map(p => p.categoria))]
  return cats.sort()
})

const categoriasTodas = computed(() => {
  return [...new Set(productos.value.filter(p => p.categoria).map(p => p.categoria))].sort()
})

const totalCarrito = computed(() => carrito.value.reduce((s, i) => s + i.cantidad, 0))
const totalVenta = computed(() => carrito.value.reduce((s, i) => s + i.producto.precio * i.cantidad, 0))

// ── Fetch ─────────────────────────────────────────────────────
async function cargarProductos() {
  cargando.value = true
  try {
    const params = canManage.value ? { solo_activos: false } : { solo_activos: true }
    const { data } = await api.get('/productos/', { params })
    productos.value = data
  } finally {
    cargando.value = false
  }
}

// ── CRUD Producto ─────────────────────────────────────────────
function abrirCrear() {
  editandoProducto.value = null
  form.value = formVacio()
  fotoArchivo.value = null
  fotoPreview.value = null
  errorForm.value = ''
  mostrarModal.value = true
}

function abrirEditar(p) {
  editandoProducto.value = p
  form.value = {
    nombre: p.nombre,
    descripcion: p.descripcion || '',
    precio: p.precio,
    stock: p.stock,
    categoria: p.categoria || '',
  }
  fotoArchivo.value = null
  fotoPreview.value = null
  errorForm.value = ''
  mostrarModal.value = true
}

function cerrarModal() { mostrarModal.value = false }

function onFotoChange(e) {
  const f = e.target.files[0]
  if (!f) return
  fotoArchivo.value = f
  fotoPreview.value = URL.createObjectURL(f)
}

async function guardarProducto() {
  guardando.value = true
  errorForm.value = ''
  try {
    let productoGuardado
    const payload = {
      nombre: form.value.nombre,
      descripcion: form.value.descripcion || null,
      precio: form.value.precio,
      stock: form.value.stock,
      categoria: form.value.categoria || null,
    }

    if (editandoProducto.value) {
      const { data } = await api.put(`/productos/${editandoProducto.value.id}`, payload)
      productoGuardado = data
    } else {
      const { data } = await api.post('/productos/', payload)
      productoGuardado = data
    }

    if (fotoArchivo.value) {
      const fd = new FormData()
      fd.append('foto', fotoArchivo.value)
      const { data } = await api.post(`/productos/${productoGuardado.id}/foto`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      productoGuardado = data
    }

    cerrarModal()
    await cargarProductos()
    mostrarToast(editandoProducto.value ? 'Producto actualizado' : 'Producto creado correctamente')
  } catch (e) {
    const d = e.response?.data?.detail
    errorForm.value = Array.isArray(d) ? d[0].msg : (d || 'Error al guardar.')
  } finally {
    guardando.value = false
  }
}

async function confirmarEliminar(p) {
  if (!confirm(`¿Eliminar "${p.nombre}"? Esta acción no se puede deshacer.`)) return
  try {
    await api.delete(`/productos/${p.id}`)
    mostrarToast('Producto eliminado')
    await cargarProductos()
  } catch (e) {
    alert(e.response?.data?.detail || 'Error al eliminar.')
  }
}

// ── Carrito POS ───────────────────────────────────────────────
function agregarAlCarrito(p) {
  const existente = carrito.value.find(i => i.producto.id === p.id)
  if (existente) {
    if (existente.cantidad < p.stock) existente.cantidad++
  } else {
    carrito.value.push({ producto: p, cantidad: 1 })
  }
  if (tabActivo.value !== 'pos') tabActivo.value = 'pos'
}

function ajustarCantidad(item, delta) {
  item.cantidad += delta
  if (item.cantidad <= 0) carrito.value = carrito.value.filter(i => i !== item)
}

function limpiarCarrito() {
  carrito.value = []
  metodoPagoVenta.value = null
  errorVenta.value = ''
}

async function registrarVenta() {
  if (!carrito.value.length) return
  procesandoVenta.value = true
  errorVenta.value = ''
  try {
    for (const item of carrito.value) {
      await api.post('/ventas/', {
        producto_id: item.producto.id,
        cantidad: item.cantidad,
        usuario_id: null,
        metodo_pago: metodoPagoVenta.value,
      })
    }
    mostrarToast(`Venta registrada · $${totalVenta.value.toLocaleString('es-CO')}`)
    limpiarCarrito()
    await cargarProductos()
  } catch (e) {
    errorVenta.value = e.response?.data?.detail || 'Error al registrar la venta.'
  } finally {
    procesandoVenta.value = false
  }
}

// ── Toast ─────────────────────────────────────────────────────
function mostrarToast(msg) {
  toast.value = msg
  setTimeout(() => { toast.value = '' }, 3000)
}

onMounted(cargarProductos)
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
