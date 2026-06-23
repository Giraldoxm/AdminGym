<template>
  <div class="animate-fade-in-up">

    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
      <div>
        <h2 class="text-3xl font-extrabold text-gray-900 tracking-tight">Planes de Suscripción</h2>
        <p class="text-gray-500 mt-1">Elige el plan que mejor se adapte a tu entrenamiento</p>
      </div>
      <div v-if="isAdmin" class="flex gap-2">
        <button @click="abrirMetodosPago"
          class="bg-white border border-gray-300 hover:border-red-500 hover:text-red-600 text-gray-700 px-4 py-2.5 rounded-lg shadow-sm transition-all font-semibold flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/>
          </svg>
          Métodos de Pago
        </button>
        <button @click="abrirCrear"
          class="bg-red-600 hover:bg-red-700 text-white px-5 py-2.5 rounded-lg shadow-md hover:shadow-lg transition-all font-semibold flex items-center gap-2 transform active:scale-95">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
          </svg>
          Nuevo Plan
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-red-600"></div>
    </div>

    <!-- Empty -->
    <div v-else-if="planes.length === 0" class="text-center py-20 text-gray-400">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p class="font-semibold text-lg">No hay planes disponibles</p>
      <p v-if="isAdmin" class="text-sm mt-1">Crea el primer plan con el botón de arriba.</p>
    </div>

    <!-- Cards -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="plan in planes" :key="plan.id"
        class="bg-white rounded-2xl shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden flex flex-col">

        <!-- Card header -->
        <div class="bg-gradient-to-br from-gray-900 to-gray-800 px-6 py-6 relative">
          <!-- Admin actions -->
          <div v-if="isAdmin" class="absolute top-3 right-3 flex gap-1">
            <button @click="abrirEditar(plan)" title="Editar"
              class="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-white/10 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button @click="confirmarEliminar(plan)" title="Eliminar"
              class="p-1.5 rounded-lg text-gray-400 hover:text-red-400 hover:bg-red-500/10 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>

          <!-- Icon -->
          <div class="w-11 h-11 bg-red-600 rounded-xl flex items-center justify-center mb-4 shadow-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>

          <h3 class="text-xl font-extrabold text-white leading-tight">{{ plan.nombre }}</h3>

          <div class="flex flex-wrap gap-2 mt-2">
            <span class="inline-flex items-center gap-1 px-3 py-0.5 rounded-full text-xs font-bold bg-white/10 text-gray-300 border border-white/10">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ plan.duracion_dias }} días de acceso
            </span>
            <span v-if="plan.incluye_wods_personalizados"
              class="inline-flex items-center gap-1 px-3 py-0.5 rounded-full text-xs font-bold bg-red-600/80 text-white border border-red-500/50">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              WODs Personalizados
            </span>
          </div>
        </div>

        <!-- Card body -->
        <div class="px-6 py-5 flex flex-col flex-1 gap-4">
          <div class="flex items-end gap-1">
            <span class="text-3xl font-black text-gray-900">${{ formatPrecio(plan.precio) }}</span>
            <span class="text-sm text-gray-400 mb-1">COP / período</span>
          </div>

          <div class="border-t border-gray-100"></div>

          <ul v-if="plan.beneficios.length" class="space-y-2 flex-1">
            <li v-for="b in plan.beneficios" :key="b" class="flex items-start gap-2.5">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-red-500 flex-shrink-0 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
              <span class="text-sm text-gray-600 leading-snug">{{ b }}</span>
            </li>
          </ul>
          <p v-else class="text-sm text-gray-400 italic flex-1">Sin beneficios definidos.</p>

          <!-- Botón: igual para coach, cliente y pendiente -->
          <template v-if="!isAdmin">
            <button v-if="isPendiente && planSolicitadoId === plan.id"
              @click="abrirAdquirir(plan)"
              class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3 rounded-xl mt-2 flex items-center justify-center gap-2 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              Solicitud registrada · Ver pasos
            </button>
            <button v-else @click="abrirAdquirir(plan)"
              class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 rounded-xl transition-all shadow-sm hover:shadow-md active:scale-95 mt-2">
              Adquirir Plan
            </button>
          </template>
        </div>
      </div>
    </div>

    <!-- ════════════════════════════════════════
         MODAL: Adquirir Plan (coach, cliente, pendiente)
    ════════════════════════════════════════ -->
    <div v-if="planAdquiriendo" class="fixed inset-0 flex items-end sm:items-center justify-center bg-gray-900/60 backdrop-blur-sm z-50 p-4">
      <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl overflow-hidden max-h-[92vh] flex flex-col">

        <!-- Header del plan -->
        <div class="bg-gradient-to-br from-gray-900 to-gray-800 px-6 py-6 flex-shrink-0">
          <div class="flex items-start justify-between gap-3">
            <div>
              <div class="w-10 h-10 bg-red-600 rounded-xl flex items-center justify-center mb-3 shadow">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 class="text-xl font-extrabold text-white">{{ planAdquiriendo.nombre }}</h3>
              <div class="flex items-center gap-3 mt-1">
                <span class="text-2xl font-black text-white">${{ formatPrecio(planAdquiriendo.precio) }}</span>
                <span class="text-sm text-gray-400">· {{ planAdquiriendo.duracion_dias }} días</span>
              </div>
            </div>
            <button @click="planAdquiriendo = null" class="text-gray-400 hover:text-white mt-1 flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </div>

        <div class="overflow-y-auto flex-1 px-6 py-5 space-y-5">

          <!-- Beneficios del plan -->
          <ul v-if="planAdquiriendo.beneficios.length" class="space-y-2">
            <li v-for="b in planAdquiriendo.beneficios" :key="b" class="flex items-start gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-red-500 flex-shrink-0 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
              <span class="text-sm text-gray-600">{{ b }}</span>
            </li>
          </ul>

          <div class="border-t border-gray-100"></div>

          <!-- ── Métodos de pago ── -->
          <div>
            <p class="text-sm font-bold text-gray-800 mb-3 flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/>
              </svg>
              Métodos de Pago
            </p>
            <div v-if="metodosPago.length === 0" class="rounded-xl border-2 border-dashed border-gray-200 bg-gray-50 px-4 py-5 text-center text-gray-400 text-sm">
              <p class="font-semibold text-gray-500">No hay métodos de pago disponibles</p>
              <p class="text-xs mt-1 text-gray-400">Contacta al administrador.</p>
            </div>
            <div v-else class="space-y-2">
              <div v-for="(m, idx) in metodosPago" :key="m.id"
                class="rounded-xl border border-gray-200 bg-white px-4 py-3 hover:border-red-300 transition-colors">
                <div class="flex items-start gap-3">
                  <span class="w-6 h-6 rounded-full bg-red-600 text-white text-xs font-black flex items-center justify-center flex-shrink-0 mt-0.5">{{ idx + 1 }}</span>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-bold text-gray-900">{{ m.banco }}</p>
                    <p class="text-xs text-gray-500 mt-0.5">{{ m.tipo_cuenta }}</p>
                    <div class="flex items-center gap-2 mt-1.5">
                      <code class="text-sm font-mono font-semibold text-gray-800 bg-gray-100 px-2 py-0.5 rounded">{{ m.numero_cuenta }}</code>
                      <button type="button" @click="copiarCuenta(m.numero_cuenta)"
                        class="text-xs text-red-600 hover:text-red-700 font-semibold">
                        {{ copiadoId === m.id ? '¡Copiado!' : 'Copiar' }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Instrucciones -->
          <div class="bg-gray-50 rounded-xl p-4 space-y-2.5">
            <p class="text-sm font-bold text-gray-800">¿Cómo adquirir este plan?</p>
            <div class="flex items-start gap-3">
              <span class="w-5 h-5 rounded-full bg-red-600 text-white text-xs font-black flex items-center justify-center flex-shrink-0 mt-0.5">1</span>
              <p class="text-sm text-gray-600">Realiza el pago usando uno de los métodos disponibles arriba por el valor de <span class="font-bold text-gray-800">${{ formatPrecio(planAdquiriendo.precio) }} COP</span>.</p>
            </div>
            <div class="flex items-start gap-3">
              <span class="w-5 h-5 rounded-full bg-red-600 text-white text-xs font-black flex items-center justify-center flex-shrink-0 mt-0.5">2</span>
              <p class="text-sm text-gray-600">Envía el comprobante de pago al administrador por WhatsApp usando el botón de abajo.</p>
            </div>
            <div class="flex items-start gap-3">
              <span class="w-5 h-5 rounded-full bg-red-600 text-white text-xs font-black flex items-center justify-center flex-shrink-0 mt-0.5">3</span>
              <p class="text-sm text-gray-600">El administrador verificará el pago y activará tu plan.</p>
            </div>
          </div>
        </div>

        <!-- Botones fijos abajo -->
        <div class="px-6 pb-6 pt-3 border-t border-gray-100 flex-shrink-0 space-y-2">
          <a :href="whatsappUrl(planAdquiriendo)" target="_blank" rel="noopener"
            class="w-full py-3 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white font-bold transition-colors flex items-center justify-center gap-2.5">
            <svg class="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
              <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51a12.8 12.8 0 00-.57-.01c-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
            </svg>
            Enviar comprobante por WhatsApp
          </a>
          <button @click="planAdquiriendo = null"
            class="w-full py-2.5 rounded-xl border border-gray-200 text-gray-600 font-semibold hover:bg-gray-50 transition-colors text-sm">
            Cerrar
          </button>
        </div>
      </div>
    </div>

    <!-- ── Modal: Crear / Editar Plan (admin) ── -->
    <div v-if="showForm" class="fixed inset-0 flex items-end sm:items-center justify-center bg-gray-900/60 backdrop-blur-sm z-50 p-4">
      <div class="bg-white rounded-2xl w-full max-w-lg shadow-2xl max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center px-6 pt-6 pb-0 mb-5">
          <h3 class="text-2xl font-bold text-gray-900">{{ editando ? 'Editar Plan' : 'Nuevo Plan' }}</h3>
          <button @click="cerrarForm" class="text-gray-400 hover:text-gray-600">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="guardarPlan" class="px-6 pb-6 space-y-5">
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">Nombre del plan <span class="text-red-500">*</span></label>
            <input v-model="form.nombre" type="text" required minlength="2" maxlength="80"
              class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none transition-all"
              placeholder="Ej. Plan Mensual">
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1.5">Precio (COP) <span class="text-red-500">*</span></label>
              <input v-model.number="form.precio" type="number" required min="1" step="1"
                class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none transition-all"
                placeholder="Ej. 100000">
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1.5">Duración (días) <span class="text-red-500">*</span></label>
              <input v-model.number="form.duracion_dias" type="number" required min="1"
                class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none transition-all"
                placeholder="Ej. 30">
            </div>
          </div>

          <!-- WODs Personalizados -->
          <label class="flex items-start gap-3 p-4 rounded-xl border-2 cursor-pointer transition-all"
            :class="form.incluye_wods_personalizados ? 'border-red-500 bg-red-50' : 'border-gray-200 hover:border-gray-300'">
            <input type="checkbox" v-model="form.incluye_wods_personalizados" class="mt-0.5 accent-red-600 w-4 h-4 flex-shrink-0">
            <div>
              <p class="text-sm font-semibold text-gray-800">Incluye WODs Personalizados</p>
              <p class="text-xs text-gray-500 mt-0.5">Los miembros con este plan tendrán acceso a programación de entrenamiento personalizada.</p>
            </div>
          </label>

          <div>
            <div class="flex justify-between items-center mb-1.5">
              <label class="block text-sm font-semibold text-gray-700">Beneficios</label>
              <button type="button" @click="agregarBeneficio"
                class="text-xs text-red-600 hover:text-red-700 font-semibold flex items-center gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
                </svg>
                Agregar
              </button>
            </div>
            <div class="space-y-2">
              <div v-for="(b, i) in form.beneficios" :key="i" class="flex gap-2">
                <input v-model="form.beneficios[i]" type="text"
                  class="flex-1 px-3 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none text-sm transition-all"
                  :placeholder="`Beneficio ${i + 1}`">
                <button type="button" @click="eliminarBeneficio(i)"
                  class="p-2.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <button v-if="form.beneficios.length === 0" type="button" @click="agregarBeneficio"
                class="w-full py-3 border-2 border-dashed border-gray-200 rounded-lg text-sm text-gray-400 hover:border-red-300 hover:text-red-400 transition-colors">
                + Agregar primer beneficio
              </button>
            </div>
          </div>

          <div v-if="errorForm" class="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg p-3">{{ errorForm }}</div>

          <div class="flex gap-3 pt-2 border-t border-gray-100">
            <button type="button" @click="cerrarForm"
              class="flex-1 py-2.5 rounded-xl border border-gray-200 text-gray-600 font-semibold hover:bg-gray-50 transition-colors">
              Cancelar
            </button>
            <button type="submit" :disabled="guardando"
              class="flex-1 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white font-bold transition-colors disabled:bg-red-300 flex items-center justify-center gap-2">
              <span v-if="guardando" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
              {{ guardando ? 'Guardando...' : (editando ? 'Guardar cambios' : 'Crear Plan') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ── Modal: Confirmar eliminación ── -->
    <div v-if="planAEliminar" class="fixed inset-0 flex items-center justify-center bg-gray-900/60 backdrop-blur-sm z-50 p-4">
      <div class="bg-white rounded-2xl w-full max-w-sm shadow-2xl p-6">
        <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h3 class="text-lg font-bold text-gray-900 text-center">Eliminar Plan</h3>
        <p class="text-sm text-gray-500 text-center mt-2">
          ¿Estás seguro de eliminar <span class="font-semibold text-gray-700">{{ planAEliminar.nombre }}</span>? Esta acción no se puede deshacer.
        </p>
        <div class="flex gap-3 mt-6">
          <button @click="planAEliminar = null"
            class="flex-1 py-2.5 rounded-xl border border-gray-200 text-gray-600 font-semibold hover:bg-gray-50 transition-colors">
            Cancelar
          </button>
          <button @click="ejecutarEliminar" :disabled="eliminando"
            class="flex-1 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white font-bold transition-colors disabled:bg-red-300 flex items-center justify-center gap-2">
            <span v-if="eliminando" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
            {{ eliminando ? 'Eliminando...' : 'Eliminar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── Modal: Gestionar métodos de pago (admin) ── -->
    <div v-if="showMetodosModal" class="fixed inset-0 flex items-end sm:items-center justify-center bg-gray-900/60 backdrop-blur-sm z-50 p-4">
      <div class="bg-white rounded-2xl w-full max-w-2xl shadow-2xl max-h-[90vh] flex flex-col">
        <div class="flex justify-between items-center px-6 pt-6 pb-4 border-b border-gray-100 flex-shrink-0">
          <div>
            <h3 class="text-2xl font-bold text-gray-900">Métodos de Pago</h3>
            <p class="text-xs text-gray-500 mt-0.5">Aparecen en el orden de la lista a los usuarios al adquirir un plan.</p>
          </div>
          <button @click="showMetodosModal = false" class="text-gray-400 hover:text-gray-600">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="overflow-y-auto flex-1 px-6 py-5 space-y-3">
          <div v-if="metodosPago.length === 0" class="text-center py-6 text-gray-400 text-sm italic">
            No hay métodos registrados aún.
          </div>
          <div v-for="(m, idx) in metodosPago" :key="m.id"
            class="rounded-xl border border-gray-200 px-4 py-3 flex items-center gap-3">
            <div class="flex flex-col gap-1">
              <button type="button" @click="moverMetodo(idx, -1)" :disabled="idx === 0"
                class="text-gray-400 hover:text-red-600 disabled:opacity-30">▲</button>
              <button type="button" @click="moverMetodo(idx, 1)" :disabled="idx === metodosPago.length - 1"
                class="text-gray-400 hover:text-red-600 disabled:opacity-30">▼</button>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-bold text-gray-900">{{ m.banco }}</p>
              <p class="text-xs text-gray-500">{{ m.tipo_cuenta }} · <code class="font-mono">{{ m.numero_cuenta }}</code></p>
            </div>
            <button type="button" @click="abrirEditarMetodo(m)" title="Editar"
              class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button type="button" @click="eliminarMetodo(m)" title="Eliminar"
              class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>

        <form @submit.prevent="guardarMetodo" class="px-6 pb-6 pt-4 border-t border-gray-100 space-y-3 flex-shrink-0">
          <p class="text-sm font-bold text-gray-700">{{ metodoEditando ? 'Editar método' : 'Agregar nuevo método' }}</p>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <input v-model="formMetodo.banco" type="text" required placeholder="Banco"
              class="px-3 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none text-sm">
            <input v-model="formMetodo.tipo_cuenta" type="text" required placeholder="Tipo de cuenta"
              class="px-3 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none text-sm">
            <input v-model="formMetodo.numero_cuenta" type="text" required placeholder="Número de cuenta"
              class="px-3 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none text-sm">
          </div>
          <div v-if="errorMetodo" class="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg p-2">{{ errorMetodo }}</div>
          <div class="flex gap-2">
            <button v-if="metodoEditando" type="button" @click="cancelarEdicionMetodo"
              class="px-4 py-2 rounded-lg border border-gray-200 text-gray-600 font-semibold hover:bg-gray-50 text-sm">
              Cancelar edición
            </button>
            <button type="submit" :disabled="guardandoMetodo"
              class="flex-1 py-2.5 rounded-lg bg-red-600 hover:bg-red-700 text-white font-bold transition-colors disabled:bg-red-300 text-sm">
              {{ guardandoMetodo ? 'Guardando...' : (metodoEditando ? 'Guardar cambios' : 'Agregar método') }}
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { useAuth } from '../composables/useAuth'

const { isAdmin, isPendiente } = useAuth()

const planes        = ref([])
const loading       = ref(true)
const adminTelefono = ref('')

// Métodos de pago (lista visible a todos; admin gestiona)
const metodosPago      = ref([])
const showMetodosModal = ref(false)
const metodoEditando   = ref(null)
const formMetodo       = ref({ banco: '', tipo_cuenta: '', numero_cuenta: '' })
const errorMetodo      = ref('')
const guardandoMetodo  = ref(false)
const copiadoId        = ref(null)

// Plan seleccionado para adquirir
const planAdquiriendo  = ref(null)
const planSolicitadoId = ref(null)

// Admin CRUD
const planAEliminar = ref(null)
const eliminando    = ref(false)
const showForm      = ref(false)
const editando      = ref(null)
const guardando     = ref(false)
const errorForm     = ref('')
const form = ref({ nombre: '', precio: '', duracion_dias: '', beneficios: [], incluye_wods_personalizados: false })

const formatPrecio = (v) => Number(v).toLocaleString('es-CO')

// Abre el modal y registra solicitud si el usuario es pendiente
const abrirAdquirir = async (plan) => {
  planAdquiriendo.value = plan
  if (isPendiente.value && planSolicitadoId.value !== plan.id) {
    try {
      await api.post(`/planes/${plan.id}/solicitar`)
      planSolicitadoId.value = plan.id
    } catch { /* silencioso: puede que ya esté registrado */ }
  }
}

// Genera el link de WhatsApp con mensaje prearmado
const whatsappUrl = (plan) => {
  const numero = adminTelefono.value
    ? adminTelefono.value.replace(/\D/g, '')
    : ''
  const nombre  = localStorage.getItem('userName') || ''
  const mensaje = `Hola! Quiero adquirir el plan *${plan.nombre}* - $${formatPrecio(plan.precio)} COP (${plan.duracion_dias} días).${nombre ? ` Mi nombre es ${nombre}.` : ''} Adjunto el comprobante de pago.`
  return `https://wa.me/${numero}?text=${encodeURIComponent(mensaje)}`
}

const fetchPlanes = async () => {
  loading.value = true
  try { planes.value = (await api.get('/planes/')).data }
  catch (e) { console.error(e) }
  finally { loading.value = false }
}

// ── Admin CRUD ────────────────────────────────────────────────
const abrirCrear = () => {
  editando.value = null
  form.value = { nombre: '', precio: '', duracion_dias: '', beneficios: [], incluye_wods_personalizados: false }
  errorForm.value = ''
  showForm.value = true
}

const abrirEditar = (plan) => {
  editando.value = plan
  form.value = {
    nombre: plan.nombre,
    precio: plan.precio,
    duracion_dias: plan.duracion_dias,
    beneficios: [...plan.beneficios],
    incluye_wods_personalizados: plan.incluye_wods_personalizados ?? false,
  }
  errorForm.value = ''
  showForm.value = true
}

const cerrarForm = () => { showForm.value = false; editando.value = null }

const agregarBeneficio  = () => { form.value.beneficios.push('') }
const eliminarBeneficio = (i) => { form.value.beneficios.splice(i, 1) }

const guardarPlan = async () => {
  guardando.value = true
  errorForm.value = ''
  const payload = {
    nombre: form.value.nombre,
    precio: form.value.precio,
    duracion_dias: form.value.duracion_dias,
    beneficios: form.value.beneficios.filter(b => b.trim()),
    incluye_wods_personalizados: form.value.incluye_wods_personalizados,
  }
  try {
    if (editando.value) {
      await api.patch(`/planes/${editando.value.id}`, payload)
    } else {
      await api.post('/planes/', payload)
    }
    cerrarForm()
    await fetchPlanes()
  } catch (e) {
    errorForm.value = e.response?.data?.detail || 'Error al guardar el plan.'
  } finally {
    guardando.value = false
  }
}

const confirmarEliminar = (plan) => { planAEliminar.value = plan }

const ejecutarEliminar = async () => {
  eliminando.value = true
  try {
    await api.delete(`/planes/${planAEliminar.value.id}`)
    planAEliminar.value = null
    await fetchPlanes()
  } catch (e) {
    alert(e.response?.data?.detail || 'Error al eliminar el plan.')
  } finally {
    eliminando.value = false
  }
}

// ── Métodos de pago ──────────────────────────────────────────
const fetchMetodosPago = async () => {
  try { metodosPago.value = (await api.get('/metodos-pago/')).data }
  catch (e) { console.error(e) }
}

const copiarCuenta = async (numero) => {
  try { await navigator.clipboard.writeText(numero) } catch {}
  const m = metodosPago.value.find(x => x.numero_cuenta === numero)
  if (m) {
    copiadoId.value = m.id
    setTimeout(() => { if (copiadoId.value === m.id) copiadoId.value = null }, 1500)
  }
}

const abrirMetodosPago = () => {
  metodoEditando.value = null
  formMetodo.value = { banco: '', tipo_cuenta: '', numero_cuenta: '' }
  errorMetodo.value = ''
  showMetodosModal.value = true
}

const abrirEditarMetodo = (m) => {
  metodoEditando.value = m
  formMetodo.value = { banco: m.banco, tipo_cuenta: m.tipo_cuenta, numero_cuenta: m.numero_cuenta }
  errorMetodo.value = ''
}

const cancelarEdicionMetodo = () => {
  metodoEditando.value = null
  formMetodo.value = { banco: '', tipo_cuenta: '', numero_cuenta: '' }
  errorMetodo.value = ''
}

const guardarMetodo = async () => {
  guardandoMetodo.value = true
  errorMetodo.value = ''
  try {
    if (metodoEditando.value) {
      await api.patch(`/metodos-pago/${metodoEditando.value.id}`, formMetodo.value)
    } else {
      await api.post('/metodos-pago/', formMetodo.value)
    }
    cancelarEdicionMetodo()
    await fetchMetodosPago()
  } catch (e) {
    errorMetodo.value = e.response?.data?.detail || 'Error al guardar el método.'
  } finally {
    guardandoMetodo.value = false
  }
}

const eliminarMetodo = async (m) => {
  if (!confirm(`¿Eliminar el método "${m.banco}"?`)) return
  try {
    await api.delete(`/metodos-pago/${m.id}`)
    await fetchMetodosPago()
  } catch (e) {
    alert(e.response?.data?.detail || 'Error al eliminar el método.')
  }
}

const moverMetodo = async (idx, delta) => {
  const j = idx + delta
  if (j < 0 || j >= metodosPago.value.length) return
  const a = metodosPago.value[idx]
  const b = metodosPago.value[j]
  // Intercambiar valores de orden y persistir.
  try {
    await Promise.all([
      api.patch(`/metodos-pago/${a.id}`, { orden: b.orden }),
      api.patch(`/metodos-pago/${b.id}`, { orden: a.orden }),
    ])
    await fetchMetodosPago()
  } catch (e) {
    alert('Error al reordenar.')
  }
}

onMounted(async () => {
  await fetchPlanes()
  fetchMetodosPago()
  try {
    const { data } = await api.get('/contacto')
    adminTelefono.value = data.telefono || ''
  } catch { /* silencioso */ }
  if (isPendiente.value) {
    try {
      const { data } = await api.get('/me')
      planSolicitadoId.value = data.plan_solicitado_id || null
    } catch { /* silencioso */ }
  }
})
</script>

<style scoped>
.animate-fade-in-up {
  animation: fadeInUp 0.4s ease-out;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
