<template>
  <div v-if="ejercicio" class="animate-fade-in-up">

    <!-- Header -->
    <div class="flex items-center gap-3 mb-6">
      <RouterLink :to="{ name: 'Marcas' }"
        class="flex items-center gap-1.5 text-sm font-semibold text-gray-400 hover:text-gray-700 transition-colors">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
        Mis Marcas
      </RouterLink>
      <span class="text-gray-200">/</span>
      <h2 class="text-2xl font-extrabold text-gray-900 truncate">{{ ejercicio }}</h2>
    </div>

    <!-- Skeleton -->
    <div v-if="cargando" class="space-y-5">
      <div class="bg-gray-100 rounded-2xl h-28 animate-pulse"></div>
      <div class="bg-gray-100 rounded-2xl h-72 animate-pulse"></div>
      <div class="bg-gray-100 rounded-2xl h-64 animate-pulse"></div>
    </div>

    <template v-else>

      <!-- Resumen + botón -->
      <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 mb-5 flex items-start justify-between gap-4">
        <div class="flex gap-6 flex-wrap">

          <!-- ── barra / corporal_lastre ── -->
          <template v-if="esTipoPeso">
            <div>
              <p class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-1">Último 1RM</p>
              <p class="text-4xl font-black text-gray-900 leading-none" v-if="ultimoRM">
                {{ ultimoRM }}<span class="text-lg font-semibold text-gray-400 ml-1">{{ ultimaUnidad }}</span>
              </p>
              <p v-else class="text-4xl font-black text-gray-300">—</p>
            </div>
            <div v-if="mejorRM && !ultimoEsPR">
              <p class="text-xs font-bold uppercase tracking-widest text-amber-500 mb-1">Mejor 1RM (PR)</p>
              <p class="text-4xl font-black text-amber-600 leading-none">
                {{ mejorRM }}<span class="text-lg font-semibold text-amber-400 ml-1">{{ ultimaUnidad }}</span>
              </p>
            </div>
            <div v-if="ultimoEsPR && registros.length > 0">
              <p class="text-xs font-bold uppercase tracking-widest text-amber-500 mb-1">Estado</p>
              <span class="inline-block text-xs font-black px-3 py-1.5 rounded-full bg-amber-100 text-amber-700">PR Actual</span>
            </div>
          </template>

          <!-- ── reps ── -->
          <template v-else-if="tipo === 'reps'">
            <div>
              <p class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-1">Última marca</p>
              <p class="text-4xl font-black text-gray-900 leading-none" v-if="ultimaReps">
                {{ ultimaReps }}<span class="text-lg font-semibold text-gray-400 ml-1">reps</span>
              </p>
              <p v-else class="text-4xl font-black text-gray-300">—</p>
            </div>
            <div v-if="mejorReps && mejorReps !== ultimaReps">
              <p class="text-xs font-bold uppercase tracking-widest text-amber-500 mb-1">PR (max reps)</p>
              <p class="text-4xl font-black text-amber-600 leading-none">
                {{ mejorReps }}<span class="text-lg font-semibold text-amber-400 ml-1">reps</span>
              </p>
            </div>
            <div v-if="mejorReps === ultimaReps && registros.length > 0">
              <p class="text-xs font-bold uppercase tracking-widest text-amber-500 mb-1">Estado</p>
              <span class="inline-block text-xs font-black px-3 py-1.5 rounded-full bg-amber-100 text-amber-700">PR Actual</span>
            </div>
          </template>

          <!-- ── leger ── -->
          <template v-else-if="tipo === 'leger'">
            <div>
              <p class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-1">Último nivel</p>
              <p class="text-4xl font-black text-gray-900 leading-none" v-if="ultimoLeger">
                {{ ultimoLeger.nivel }}<span class="text-lg font-semibold text-gray-400">.{{ ultimoLeger.palier }}</span>
              </p>
              <p v-else class="text-4xl font-black text-gray-300">—</p>
            </div>
            <div v-if="mejorLeger && (mejorLeger.nivel !== ultimoLeger?.nivel || mejorLeger.palier !== ultimoLeger?.palier)">
              <p class="text-xs font-bold uppercase tracking-widest text-amber-500 mb-1">PR</p>
              <p class="text-4xl font-black text-amber-600 leading-none">
                {{ mejorLeger.nivel }}<span class="text-lg font-semibold text-amber-400">.{{ mejorLeger.palier }}</span>
              </p>
            </div>
            <div v-if="mejorLeger && ultimoLeger && mejorLeger.nivel === ultimoLeger.nivel && mejorLeger.palier === ultimoLeger.palier">
              <p class="text-xs font-bold uppercase tracking-widest text-amber-500 mb-1">Estado</p>
              <span class="inline-block text-xs font-black px-3 py-1.5 rounded-full bg-amber-100 text-amber-700">PR Actual</span>
            </div>
          </template>

        </div>
        <!-- Botón: reps / léger -->
        <button v-if="!esTipoPeso" @click="abrirModal"
          class="shrink-0 flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-5 rounded-xl shadow-sm transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4"/>
          </svg>
          Registrar
        </button>
      </div>

      <!-- Panel agregar serie (barra / corporal_lastre) -->
      <div v-if="esTipoPeso" class="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 mb-5">

        <!-- Header: título + unidad -->
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-sm font-bold text-gray-700 uppercase tracking-wide">Agregar serie</h3>
          <div class="flex gap-0.5 bg-gray-100 rounded-lg p-0.5">
            <button type="button" @click="quickUnidad = 'kg'"
              :class="quickUnidad === 'kg' ? 'bg-red-600 text-white' : 'text-gray-500'"
              class="px-2.5 py-1 rounded-md text-xs font-bold transition-all">kg</button>
            <button type="button" @click="quickUnidad = 'lbs'"
              :class="quickUnidad === 'lbs' ? 'bg-red-600 text-white' : 'text-gray-500'"
              class="px-2.5 py-1 rounded-md text-xs font-bold transition-all">lbs</button>
          </div>
        </div>

        <!-- Peso corporal (Dominadas) -->
        <div v-if="tipo === 'corporal_lastre'" class="mb-3 bg-gray-50 border border-gray-100 rounded-xl p-3">
          <p class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-1">Tu peso corporal</p>
          <template v-if="pesoCorporalAuto">
            <p class="text-base font-black text-gray-800">
              {{ quickUnidad === 'lbs' ? round1(pesoCorporalAuto * KG_PER_LB) : pesoCorporalAuto }} {{ quickUnidad }}
            </p>
            <p class="text-xs text-gray-400 mt-0.5">Base de cada serie. El lastre se suma encima.</p>
          </template>
          <template v-else>
            <input v-model.number="quickPesoCorporal" type="number" step="0.1" min="1"
              placeholder="Tu peso en kg"
              class="w-full px-3 py-2 rounded-lg border border-gray-300 bg-white text-gray-900 focus:ring-2 focus:ring-red-500 outline-none font-semibold">
            <p class="text-xs text-gray-400 mt-1">Sin registros en Mi Salud — ingrésalo aquí</p>
          </template>
        </div>

        <!-- Inputs peso + reps -->
        <div class="flex gap-2 items-end">
          <div class="flex-1">
            <label class="block text-xs font-semibold text-gray-500 mb-1">
              {{ tipo === 'corporal_lastre' ? 'Lastre adicional' : 'Peso' }}
            </label>
            <input v-model.number="quickPeso" type="number" step="0.5" min="0"
              :placeholder="tipo === 'corporal_lastre' ? '0 (sin lastre)' : 'Ej: 80'"
              @keydown.enter.prevent="quickGuardar"
              class="w-full px-3 py-2.5 rounded-xl border border-gray-300 bg-white text-gray-900 focus:ring-2 focus:ring-red-500 outline-none font-bold text-lg">
          </div>
          <div class="w-[72px]">
            <label class="block text-xs font-semibold text-gray-500 mb-1">Reps</label>
            <input v-model.number="quickReps" type="number" min="1" max="36" placeholder="5"
              @keydown.enter.prevent="quickGuardar"
              class="w-full px-3 py-2.5 rounded-xl border border-gray-300 bg-white text-gray-900 focus:ring-2 focus:ring-red-500 outline-none font-bold text-lg">
          </div>
          <button type="button" @click="quickGuardar" :disabled="quickGuardando"
            class="h-[46px] px-4 bg-gray-900 hover:bg-gray-700 disabled:opacity-40 text-white rounded-xl font-bold text-xl transition-colors shrink-0">
            <span v-if="quickGuardando" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white inline-block align-middle"></span>
            <span v-else>+</span>
          </button>
        </div>

        <!-- Error -->
        <div v-if="quickError" class="mt-2 text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg p-2">
          {{ quickError }}
        </div>

        <!-- Series de hoy -->
        <div v-if="seriesDeHoy.length" class="mt-3 border-t border-gray-50 pt-3">
          <p class="text-xs font-bold text-gray-400 uppercase tracking-wide mb-2">
            Hoy · {{ seriesDeHoy.length }} serie{{ seriesDeHoy.length !== 1 ? 's' : '' }}
          </p>
          <div class="space-y-1">
            <div v-for="r in seriesDeHoy" :key="r.id"
              class="flex items-center justify-between text-sm px-2 py-1.5 rounded-lg bg-gray-50">
              <span class="font-semibold text-gray-800">
                {{ r.peso }} {{ r.unidad }} × {{ r.repeticiones }} reps
              </span>
              <span class="text-xs font-bold text-red-500">{{ r.rm_calculado }} 1RM</span>
            </div>
          </div>
        </div>

      </div>

      <!-- Gráfica (con tabs para ejercicios de peso) -->
      <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 mb-4">

        <!-- Tabs + toggle kg/lbs — solo para barra/corporal_lastre -->
        <div v-if="esTipoPeso" class="flex items-center justify-between gap-2 mb-4 flex-wrap">
          <div class="flex gap-1 bg-gray-100 rounded-xl p-1">
            <button @click="activeChartTab = 'rm'"
              :class="activeChartTab === 'rm' ? 'bg-white shadow text-gray-900' : 'text-gray-500'"
              class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all">1RM</button>
            <button @click="activeChartTab = 'peso'"
              :class="activeChartTab === 'peso' ? 'bg-white shadow text-gray-900' : 'text-gray-500'"
              class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all">Peso</button>
            <button @click="activeChartTab = 'volumen'"
              :class="activeChartTab === 'volumen' ? 'bg-white shadow text-gray-900' : 'text-gray-500'"
              class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all">Volumen</button>
          </div>
          <div v-if="registrosPorDia.length >= 2" class="flex gap-1">
            <button @click="chartUnit = 'kg'"
              :class="chartUnit === 'kg' ? 'bg-red-600 text-white' : 'bg-gray-100 text-gray-500'"
              class="px-3 py-1.5 rounded-full text-xs font-bold transition-colors">kg</button>
            <button @click="chartUnit = 'lbs'"
              :class="chartUnit === 'lbs' ? 'bg-red-600 text-white' : 'bg-gray-100 text-gray-500'"
              class="px-3 py-1.5 rounded-full text-xs font-bold transition-colors">lbs</button>
          </div>
        </div>

        <!-- Descripción dinámica según tab -->
        <div v-if="esTipoPeso" class="mb-3">
          <template v-if="activeChartTab === 'rm'">
            <p class="text-xs font-semibold text-gray-700">1RM estimado</p>
            <p class="text-xs text-gray-400 mt-0.5">El peso máximo que podrías levantar en una sola repetición, calculado a partir de tus series. El punto dorado es tu mejor marca.</p>
          </template>
          <template v-else-if="activeChartTab === 'peso'">
            <p class="text-xs font-semibold text-gray-700">Peso cargado por sesión</p>
            <p class="text-xs text-gray-400 mt-0.5">El peso real que levantaste en cada registro. Te muestra si estás progresando en carga a lo largo del tiempo.</p>
          </template>
          <template v-else>
            <p class="text-xs font-semibold text-gray-700">Volumen por sesión</p>
            <p class="text-xs text-gray-400 mt-0.5">Peso × Repeticiones de cada sesión. Refleja el esfuerzo total: puedes hacer menos peso con más reps y aun así tener más volumen. La barra dorada es tu máximo.</p>
          </template>
        </div>

        <!-- Canvas único -->
        <div v-if="registros.length >= 2" class="relative h-56">
          <canvas ref="chartCanvas"></canvas>
        </div>
        <div v-else class="h-24 flex flex-col items-center justify-center text-gray-400 text-sm gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-gray-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"/>
          </svg>
          <span>Agrega al menos 2 registros para ver la gráfica</span>
        </div>
      </div>

      <!-- Acordeón: Peso por reps -->
      <template v-if="esTipoPeso && registros.length > 0">
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden mb-4">
          <button @click="mostrarRepMax = !mostrarRepMax"
            class="w-full flex items-center justify-between px-5 py-3.5 hover:bg-gray-50 transition-colors">
            <div class="text-left">
              <p class="text-sm font-semibold text-gray-700">Peso máximo por repeticiones</p>
              <p class="text-xs text-gray-400 mt-0.5">¿Cuánto puedo levantar si hago N reps?</p>
            </div>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400 transition-transform shrink-0 ml-3"
              :class="mostrarRepMax ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </button>
          <template v-if="mostrarRepMax">
            <div class="border-t border-gray-100 px-5 py-2 text-xs text-gray-400">
              Basado en tu último 1RM: <strong>{{ ultimoRM }} {{ ultimaUnidad }}</strong>. Si entrenas a cierto número de reps, este es el peso aproximado que deberías manejar.
            </div>
            <table class="min-w-full">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-5 py-2.5 text-left text-xs font-bold text-gray-400 uppercase tracking-wider">Reps</th>
                  <th class="px-5 py-2.5 text-right text-xs font-bold text-red-500 uppercase tracking-wider">Peso estimado</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-50">
                <tr v-for="fila in tablaRepMax" :key="fila.reps"
                  :class="fila.reps === 1 ? 'bg-red-50' : 'hover:bg-gray-50'" class="transition-colors">
                  <td class="px-5 py-2.5">
                    <span class="flex items-center gap-1.5">
                      <span class="text-sm font-black text-gray-900">{{ fila.reps }}</span>
                      <span v-if="fila.reps === 1" class="text-xs font-bold px-1.5 py-0.5 rounded-full bg-red-100 text-red-600">1RM</span>
                    </span>
                  </td>
                  <td class="px-5 py-2.5 text-right">
                    <span class="text-sm font-black text-red-600">{{ fila.promedio }}</span>
                    <span class="text-xs text-gray-400 ml-1">{{ ultimaUnidad }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </template>
        </div>
      </template>

      <!-- Historial -->
      <div class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h3 class="font-bold text-gray-800">Historial</h3>
          <span class="text-xs text-gray-400">{{ registros.length }} registros</span>
        </div>
        <div v-if="registros.length === 0" class="px-6 py-12 text-center text-gray-400 text-sm">
          Sin registros. Presiona <strong>Registrar</strong> para añadir tu primera marca.
        </div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-100">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-3 py-2.5 sm:px-5 sm:py-3 text-left text-xs font-bold text-gray-400 uppercase tracking-wider">Fecha</th>
                <th class="px-3 py-2.5 sm:px-5 sm:py-3 text-left text-xs font-bold text-gray-400 uppercase tracking-wider">{{ encabezadoMedicion }}</th>
                <th v-if="esTipoPeso" class="px-3 py-2.5 sm:px-5 sm:py-3 text-left text-xs font-bold text-gray-400 uppercase tracking-wider">1RM</th>
                <th class="hidden sm:table-cell px-5 py-3 text-left text-xs font-bold text-gray-400 uppercase tracking-wider">Notas</th>
                <th class="px-2 py-2.5 sm:px-5 sm:py-3"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="r in [...registros].reverse()" :key="r.id"
                class="hover:bg-gray-50 transition-colors group">
                <td class="px-3 py-2.5 sm:px-5 sm:py-3.5 text-sm font-medium text-gray-700 whitespace-nowrap">
                  {{ formatFecha(r.fecha) }}
                </td>
                <td class="px-3 py-2.5 sm:px-5 sm:py-3.5">
                  <!-- barra / corporal_lastre con series -->
                  <template v-if="esTipoPeso">
                    <template v-if="r.series && r.series.length > 0">
                      <!-- Mejor serie (la de mayor rm_calculado) -->
                      <div class="text-sm font-semibold text-gray-800">
                        {{ r.series.reduce((b, s) => s.rm_calculado > (b?.rm_calculado ?? -Infinity) ? s : b, null)?.peso }}
                        {{ r.unidad }} ×
                        {{ r.series.reduce((b, s) => s.rm_calculado > (b?.rm_calculado ?? -Infinity) ? s : b, null)?.repeticiones }} reps
                        <span class="text-xs text-gray-400 font-normal">(mejor)</span>
                      </div>
                      <!-- Expandir series -->
                      <button v-if="r.series.length > 1" type="button"
                        @click="registrosExpandidos.has(r.id) ? registrosExpandidos.delete(r.id) : registrosExpandidos.add(r.id); registrosExpandidos = new Set(registrosExpandidos)"
                        class="text-xs text-red-500 font-semibold mt-0.5 hover:underline">
                        {{ registrosExpandidos.has(r.id) ? 'Ocultar series' : `+ ${r.series.length - 1} series más` }}
                      </button>
                      <div v-if="registrosExpandidos.has(r.id)" class="mt-1.5 space-y-0.5">
                        <div v-for="(s, si) in r.series" :key="si" class="text-xs text-gray-500 break-words">
                          <span class="font-medium">{{ si + 1 }}.</span>
                          {{ s.peso }} {{ r.unidad }} × {{ s.repeticiones }}r
                          <span class="text-red-400">→ {{ s.rm_calculado }}</span>
                        </div>
                      </div>
                    </template>
                    <!-- Registro antiguo sin series -->
                    <template v-else>
                      <span class="text-sm font-bold text-gray-900">{{ r.peso }} {{ r.unidad }}</span>
                      <span class="text-gray-400 mx-1">×</span>
                      <span class="text-sm font-bold text-gray-900">{{ r.repeticiones }}</span>
                      <span class="text-xs text-gray-400 ml-1">reps</span>
                    </template>
                  </template>
                  <!-- reps -->
                  <template v-else-if="tipo === 'reps'">
                    <span class="text-sm font-bold text-gray-900">{{ r.repeticiones }}</span>
                    <span class="text-xs text-gray-400 ml-1">reps</span>
                  </template>
                  <!-- leger -->
                  <template v-else-if="tipo === 'leger'">
                    <span class="text-sm font-bold text-gray-900">Nivel {{ r.nivel }}</span>
                    <span class="text-xs text-gray-400 ml-1">· palier {{ r.palier }}</span>
                  </template>
                </td>
                <td v-if="esTipoPeso" class="px-3 py-2.5 sm:px-5 sm:py-3.5 whitespace-nowrap">
                  <span class="text-sm font-black text-red-600">{{ r.rm_calculado }} {{ r.unidad }}</span>
                  <span v-if="esRegistroPR(r)"
                    class="ml-1 text-xs font-bold px-1.5 py-0.5 rounded-full bg-amber-100 text-amber-700">PR</span>
                </td>
                <td class="hidden sm:table-cell px-5 py-3.5 text-sm text-gray-400 max-w-[180px] truncate">{{ r.notas || '—' }}</td>
                <td class="px-2 py-2.5 sm:px-5 sm:py-3.5 text-right whitespace-nowrap">
                  <div class="flex items-center justify-end gap-1">
                    <button @click="abrirModalEditar(r)"
                      class="p-1.5 text-gray-400 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-all">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M15.232 5.232l3.536 3.536M9 11l6-6 3 3-6 6H9v-3z"/>
                      </svg>
                    </button>
                    <button @click="eliminar(r)"
                      class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </template>

    <!-- Modal: registrar -->
    <div v-if="mostrarModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm flex flex-col max-h-[90vh]">
        <div class="p-5 border-b border-gray-100 flex items-center justify-between shrink-0">
          <div>
            <h3 class="text-lg font-bold text-gray-800">{{ editandoId !== null ? 'Editar Marca' : 'Registrar Marca' }}</h3>
            <p class="text-sm text-gray-500">{{ ejercicio }}</p>
          </div>
          <button @click="cerrarModal" class="p-2 rounded-lg hover:bg-gray-100 text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <form @submit.prevent="guardar" class="p-5 space-y-4 overflow-y-auto">

          <!-- ── barra / corporal_lastre: series de entrenamiento ── -->
          <template v-if="esTipoPeso">

            <!-- Unidad -->
            <div class="flex items-center justify-between">
              <span class="text-sm font-semibold text-gray-700">Unidad</span>
              <div class="flex gap-1 bg-gray-100 rounded-lg p-0.5">
                <button type="button" @click="formUnidad = 'kg'"
                  :class="formUnidad === 'kg' ? 'bg-white shadow text-gray-900' : 'text-gray-500'"
                  class="px-3 py-1 rounded-md text-xs font-bold transition-all">kg</button>
                <button type="button" @click="formUnidad = 'lbs'"
                  :class="formUnidad === 'lbs' ? 'bg-white shadow text-gray-900' : 'text-gray-500'"
                  class="px-3 py-1 rounded-md text-xs font-bold transition-all">lbs</button>
              </div>
            </div>

            <!-- Peso corporal (solo Dominadas) -->
            <div v-if="tipo === 'corporal_lastre'" class="bg-gray-50 border border-gray-100 rounded-xl p-3">
              <p class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-1">Tu peso corporal</p>
              <template v-if="pesoCorporalAuto">
                <p class="text-lg font-black text-gray-800">{{ pesoCorporalAuto }} kg
                  <span v-if="formUnidad === 'lbs'" class="text-sm font-normal text-gray-400 ml-1">(≈ {{ round1(pesoCorporalAuto * KG_PER_LB) }} lbs)</span>
                </p>
                <p class="text-xs text-gray-400 mt-0.5">Tomado de Mi Salud — base de cada serie. El lastre se suma encima.</p>
              </template>
              <template v-else>
                <input v-model.number="formPesoCorporal" type="number" step="0.1" min="1"
                  placeholder="Tu peso en kg"
                  class="w-full px-3 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none font-semibold mt-1">
                <p class="text-xs text-gray-400 mt-1">Sin registros en Mi Salud — ingrésalo aquí</p>
              </template>
            </div>

            <!-- Series registradas -->
            <div v-if="formSeries.length > 0">
              <p class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-2">Series de la sesión</p>
              <div class="space-y-1.5">
                <div v-for="(s, i) in seriesConRM" :key="i"
                  :class="mejorSerie && s.rm !== null && s.rm === mejorSerie.rm ? 'border-amber-300 bg-amber-50' : 'border-gray-100 bg-gray-50'"
                  class="flex items-center gap-2 px-3 py-2 rounded-xl border text-sm">
                  <span class="text-xs font-bold text-gray-400 w-4">{{ i + 1 }}</span>
                  <span class="flex-1 font-semibold text-gray-800">
                    {{ s.peso }} {{ formUnidad }}
                    <span class="text-gray-400 font-normal mx-1">×</span>
                    {{ s.reps }} reps
                  </span>
                  <span v-if="s.rm" class="text-xs font-bold text-red-500 shrink-0">{{ s.rm }} 1RM</span>
                  <span v-if="mejorSerie && s.rm !== null && s.rm === mejorSerie.rm" class="text-amber-500 shrink-0">★</span>
                  <button type="button" @click="modalQuitarSerie(i)" class="p-1 text-gray-300 hover:text-red-400 transition-colors shrink-0">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- Agregar serie -->
            <div class="flex gap-2 items-end">
              <div class="flex-1">
                <label class="block text-xs font-semibold text-gray-500 mb-1">
                  {{ tipo === 'corporal_lastre' ? 'Lastre adicional' : 'Peso' }}
                </label>
                <input v-model.number="formNuevaPeso" type="number" step="0.5" min="0"
                  :placeholder="tipo === 'corporal_lastre' ? '0' : 'Ej: 80'"
                  :autofocus="formSeries.length === 0"
                  @keydown.enter.prevent="modalAgregarSerie"
                  class="w-full px-3 py-2.5 rounded-xl border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none font-bold text-lg">
              </div>
              <div class="w-[72px]">
                <label class="block text-xs font-semibold text-gray-500 mb-1">Reps</label>
                <input v-model.number="formNuevaReps" type="number" min="1" max="36"
                  placeholder="5"
                  @keydown.enter.prevent="modalAgregarSerie"
                  class="w-full px-3 py-2.5 rounded-xl border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none font-bold text-lg">
              </div>
              <button type="button" @click="modalAgregarSerie"
                class="h-[46px] px-4 bg-gray-900 hover:bg-gray-700 text-white rounded-xl font-bold text-xl transition-colors shrink-0">+</button>
            </div>
            <p class="text-xs text-gray-400 -mt-1">Presiona <strong>+</strong> o <kbd class="px-1 py-0.5 bg-gray-100 rounded">Enter</kbd> para agregar cada serie.</p>

            <!-- Mejor 1RM de la sesión -->
            <div v-if="mejorSerie && mejorSerie.rm" class="bg-red-50 border border-red-100 rounded-xl p-3 flex items-center justify-between">
              <div>
                <p class="text-xs font-bold uppercase tracking-widest text-red-400">Mejor 1RM de la sesión</p>
                <p class="text-2xl font-black text-red-600 mt-0.5">{{ mejorSerie.rm }} {{ formUnidad }}</p>
              </div>
              <span v-if="esPR" class="text-xs font-black px-2 py-1 rounded-full bg-amber-100 text-amber-700">¡Nuevo PR!</span>
            </div>

          </template>

          <!-- ── reps ── -->
          <div v-else-if="tipo === 'reps'">
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">Repeticiones</label>
            <input v-model.number="formReps" type="number" min="1" required autofocus
              placeholder="Ej: 20"
              class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none font-bold text-2xl">
          </div>

          <!-- ── léger ── -->
          <div v-else-if="tipo === 'leger'" class="space-y-3">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1.5">Nivel <span class="text-gray-400 font-normal">(1–23)</span></label>
              <input v-model.number="formNivel" type="number" min="1" max="23" required autofocus
                placeholder="Ej: 10"
                class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none font-bold text-2xl">
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1.5">Palier <span class="text-gray-400 font-normal">(1–20)</span></label>
              <input v-model.number="formPalier" type="number" min="1" max="20" required
                placeholder="Ej: 5"
                class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none font-bold text-2xl">
            </div>
          </div>

          <!-- Fecha -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">Fecha</label>
            <input v-model="formFecha" type="date" required
              class="block w-full min-w-0 appearance-none px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none">
          </div>

          <!-- Notas -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">
              Notas <span class="text-gray-400 font-normal">(opcional)</span>
            </label>
            <textarea v-model="formNotas" rows="2" placeholder="Observaciones..."
              class="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 outline-none resize-none text-sm">
            </textarea>
          </div>

          <div v-if="errorForm" class="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg p-3">
            {{ errorForm }}
          </div>

          <div class="flex gap-3 pt-1">
            <button type="button" @click="cerrarModal"
              class="flex-1 py-2.5 rounded-xl border border-gray-300 text-gray-600 font-semibold hover:bg-gray-50 transition-colors">
              Cancelar
            </button>
            <button type="submit" :disabled="guardando"
              class="flex-1 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white font-bold transition-colors disabled:opacity-50 flex items-center justify-center gap-2">
              <span v-if="guardando" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
              {{ guardando ? 'Guardando...' : 'Guardar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { Chart } from 'chart.js/auto'
import api from '../api'
import { tipoDe } from '../data/ejerciciosMarcas'

const route  = useRoute()
const router = useRouter()

// ── Estado ─────────────────────────────────────────────────────
const registros        = ref([])
const cargando         = ref(true)
const mostrarModal     = ref(false)
const editandoId       = ref(null)   // null = crear, int = editar ese id
const guardando        = ref(false)
const errorForm        = ref('')
const formPeso         = ref('')
const formUnidad       = ref('kg')
const formReps         = ref('')
const formPesoCorporal = ref('')
const formPesoAdicional = ref('')
const formNivel         = ref('')
const formPalier        = ref('')
const formFecha         = ref(new Date().toISOString().slice(0, 10))
const formNotas         = ref('')
const pesoCorporalAuto  = ref(null)
// Series: lista de sets de la sesión (barra/corporal_lastre) — solo para modal reps/leger legacy
const formSeries        = ref([])
const formNuevaPeso     = ref('')
const formNuevaReps     = ref('')
const registrosExpandidos = ref(new Set())
// Peso corporal "congelado" del registro que se edita (en su unidad). Preserva el
// snapshot histórico en vez de recalcular con el peso corporal actual.
const corporalBaseEdit  = ref(null)

const ejercicio = computed(() => route.params.ejercicio || null)
const tipo      = computed(() => ejercicio.value ? tipoDe(ejercicio.value) : 'barra')
const esTipoPeso = computed(() => tipo.value === 'barra' || tipo.value === 'corporal_lastre')

// ── Quick add (barra / corporal_lastre) ───────────────────────
const quickPeso         = ref('')
const quickReps         = ref('')
const quickUnidad       = ref('kg')
const quickPesoCorporal = ref('')
const quickError        = ref('')
const quickGuardando    = ref(false)

const seriesDeHoy = computed(() => {
  const hoy = new Date().toISOString().slice(0, 10)
  return registros.value.filter(r => r.fecha === hoy)
})

async function quickGuardar() {
  const reps = Number(quickReps.value)
  if (!reps || reps < 1) { quickError.value = 'Ingresa las repeticiones.'; return }

  let pesoTotal
  let lastre = null
  if (tipo.value === 'barra') {
    const p = Number(quickPeso.value)
    if (!p || p <= 0) { quickError.value = 'Ingresa el peso.'; return }
    pesoTotal = p
  } else {
    const corporalKg = Number(pesoCorporalAuto.value || quickPesoCorporal.value)
    if (!corporalKg) { quickError.value = 'Ingresa tu peso corporal primero.'; return }
    const corp = quickUnidad.value === 'lbs' ? round1(corporalKg * KG_PER_LB) : corporalKg
    lastre = Number(quickPeso.value) || 0
    pesoTotal = round1(corp + lastre)
  }

  quickGuardando.value = true
  quickError.value = ''
  try {
    await api.post('/marcas/', {
      ejercicio: ejercicio.value,
      fecha: new Date().toISOString().slice(0, 10),
      unidad: quickUnidad.value,
      series: [{ peso: pesoTotal, repeticiones: reps }],
      ...(lastre !== null ? { peso_adicional: lastre } : {}),
    })
    quickPeso.value = ''
    quickReps.value = ''
    await cargar()
  } catch (e) {
    const d = e.response?.data?.detail
    quickError.value = Array.isArray(d) ? d[0].msg : (d || 'Error al guardar.')
  } finally {
    quickGuardando.value = false
  }
}

const tituloGrafica = computed(() => {
  if (tipo.value === 'reps')  return 'Evolución de repeticiones'
  if (tipo.value === 'leger') return 'Evolución del nivel'
  return 'Evolución del 1RM'
})

const encabezadoMedicion = computed(() => {
  if (tipo.value === 'reps')  return 'Repeticiones'
  if (tipo.value === 'leger') return 'Nivel · palier'
  return 'Peso × Reps'
})

// ── Chart ──────────────────────────────────────────────────────
const chartCanvas    = ref(null)
const chartUnit      = ref('kg')
const activeChartTab = ref('rm')   // 'rm' | 'peso' | 'volumen'
const mostrarRepMax = ref(false)
let instanciaChart   = null

function destruirChart() {
  if (instanciaChart) { instanciaChart.destroy(); instanciaChart = null }
}

function _lineChart(canvas, labels, valores, label, suffix, color, highlights) {
  return new Chart(canvas, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label,
        data: valores,
        borderColor: color,
        backgroundColor: color + '18',
        borderWidth: 2.5,
        pointBackgroundColor: highlights.map(h => h ? '#f59e0b' : color),
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 5,
        pointHoverRadius: 7,
        fill: true,
        tension: 0.35,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 400 },
      plugins: {
        legend: { display: false },
        tooltip: { mode: 'index', intersect: false, callbacks: { label: ctx => ` ${ctx.parsed.y}${suffix}` } },
      },
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 11 }, maxTicksLimit: 8, maxRotation: 30 } },
        y: {
          grid: { color: '#f3f4f6' },
          ticks: { font: { size: 11 }, callback: v => `${v}${suffix}` },
          suggestedMin: Math.max(0, Math.min(...valores) - (Math.min(...valores) > 10 ? 5 : 1)),
          suggestedMax: Math.max(...valores) + (Math.max(...valores) > 10 ? 5 : 1),
        },
      },
    },
  })
}

function renderChart() {
  destruirChart()
  if (!chartCanvas.value) return

  if (tipo.value === 'reps') {
    if (registros.value.length < 2) return
    const labels = registros.value.map(r => formatFecha(r.fecha))
    const valores = registros.value.map(r => r.repeticiones)
    const maxR = Math.max(...valores)
    instanciaChart = _lineChart(chartCanvas.value, labels, valores, 'Repeticiones', '', '#f87171', valores.map(v => v === maxR))
    return
  }
  if (tipo.value === 'leger') {
    if (registros.value.length < 2) return
    const labels = registros.value.map(r => formatFecha(r.fecha))
    const valores = registros.value.map(r => Number(`${r.nivel || 0}.${String(r.palier || 0).padStart(2, '0')}`))
    const maxV = Math.max(...valores)
    instanciaChart = _lineChart(chartCanvas.value, labels, valores, 'Nivel', '', '#f87171', valores.map(v => v === maxV))
    return
  }

  // barra / corporal_lastre — una entrada por día (mejor RM del día)
  if (registrosPorDia.value.length < 2) return
  const labels = registrosPorDia.value.map(r => formatFecha(r.fecha))
  const suffix = ` ${chartUnit.value}`

  if (activeChartTab.value === 'rm') {
    const valores = registrosPorDia.value.map(r => {
      const kg = toKg(r.rm_calculado, r.unidad)
      return round1(chartUnit.value === 'lbs' ? fromKg(kg, 'lbs') : kg)
    })
    const prKg = mejorRMkg.value
    const highlights = registrosPorDia.value.map(r => Math.abs(toKg(r.rm_calculado, r.unidad) - prKg) < 0.01)
    instanciaChart = _lineChart(chartCanvas.value, labels, valores, `1RM estimado (${chartUnit.value})`, suffix, '#f87171', highlights)

  } else if (activeChartTab.value === 'peso') {
    const valores = registrosPorDia.value.map(r => {
      const kg = toKg(r.peso, r.unidad)
      return round1(chartUnit.value === 'lbs' ? fromKg(kg, 'lbs') : kg)
    })
    const maxVal = Math.max(...valores)
    instanciaChart = _lineChart(chartCanvas.value, labels, valores, `Peso cargado (${chartUnit.value})`, suffix, '#60a5fa', valores.map(v => Math.abs(v - maxVal) < 0.01))

  } else {
    // volumen: suma de (peso × reps) de TODAS las series de TODOS los registros del día
    const mapa = new Map()
    for (const r of registros.value) {
      const volKg = (r.series && r.series.length)
        ? r.series.reduce((sum, s) => sum + toKg(s.peso, r.unidad) * s.repeticiones, 0)
        : toKg(r.peso, r.unidad) * (r.repeticiones || 1)
      mapa.set(r.fecha, (mapa.get(r.fecha) || 0) + volKg)
    }
    const fechas = [...mapa.keys()].sort()
    labels.length = 0
    labels.push(...fechas.map(formatFecha))
    const valores = fechas.map(f => {
      const kg = mapa.get(f)
      return round1(chartUnit.value === 'lbs' ? fromKg(kg, 'lbs') : kg)
    })
    const maxVal = Math.max(...valores)
    instanciaChart = new Chart(chartCanvas.value, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: `Volumen (${chartUnit.value})`,
          data: valores,
          backgroundColor: valores.map(v => Math.abs(v - maxVal) < 0.01 ? '#f59e0bcc' : '#f87171aa'),
          borderColor:     valores.map(v => Math.abs(v - maxVal) < 0.01 ? '#d97706' : '#f87171'),
          borderWidth: 1.5,
          borderRadius: 6,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 400 },
        plugins: {
          legend: { display: false },
          tooltip: { mode: 'index', intersect: false, callbacks: { label: ctx => ` ${ctx.parsed.y}${suffix}` } },
        },
        scales: {
          x: { grid: { display: false }, ticks: { font: { size: 11 }, maxTicksLimit: 8, maxRotation: 30 } },
          y: {
            grid: { color: '#f3f4f6' },
            ticks: { font: { size: 11 }, callback: v => `${v}${suffix}` },
            suggestedMin: 0,
            suggestedMax: maxVal + Math.ceil(maxVal * 0.1),
          },
        },
      },
    })
  }
}

watch([chartUnit, activeChartTab], async () => {
  if (registros.value.length < 2) return
  await nextTick(); await nextTick()
  renderChart()
})

watch(registros, async () => {
  await nextTick(); await nextTick()
  renderChart()
})

// ── Helpers ────────────────────────────────────────────────────
const formatFecha = (f) =>
  new Date(f + 'T12:00:00').toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })

const KG_PER_LB = 2.20462

function toKg(valor, unidad) {
  return unidad === 'lbs' ? valor / KG_PER_LB : valor
}
function fromKg(valorKg, unidad) {
  return unidad === 'lbs' ? valorKg * KG_PER_LB : valorKg
}
function round1(v) { return Math.round(v * 10) / 10 }

// ── PRs por tipo ───────────────────────────────────────────────

// Agrupa por fecha tomando el mejor rm del día — usado solo para la gráfica
const registrosPorDia = computed(() => {
  if (!esTipoPeso.value) return registros.value
  const mapa = new Map()
  for (const r of registros.value) {
    const prev = mapa.get(r.fecha)
    if (!prev || toKg(r.rm_calculado, r.unidad) > toKg(prev.rm_calculado, prev.unidad)) {
      mapa.set(r.fecha, r)
    }
  }
  return [...mapa.values()].sort((a, b) => (a.fecha < b.fecha ? -1 : 1))
})

const ultimoRM     = computed(() => registrosPorDia.value.length && registrosPorDia.value[registrosPorDia.value.length - 1].rm_calculado)
const ultimaUnidad = computed(() => registrosPorDia.value.length ? registrosPorDia.value[registrosPorDia.value.length - 1].unidad : 'kg')

const mejorRMkg = computed(() =>
  registros.value.length
    ? Math.max(...registros.value.filter(r => r.rm_calculado != null).map(r => toKg(r.rm_calculado, r.unidad)))
    : null
)
const mejorRM = computed(() =>
  mejorRMkg.value !== null && mejorRMkg.value !== -Infinity ? round1(fromKg(mejorRMkg.value, ultimaUnidad.value)) : null
)

const ultimaReps = computed(() => registros.value.length ? registros.value[registros.value.length - 1].repeticiones : null)
const mejorReps  = computed(() =>
  registros.value.length ? Math.max(...registros.value.map(r => r.repeticiones || 0)) : null
)

const ultimoLeger = computed(() => {
  if (!registros.value.length) return null
  const r = registros.value[registros.value.length - 1]
  return { nivel: r.nivel, palier: r.palier }
})
const mejorLeger = computed(() => {
  if (!registros.value.length) return null
  return registros.value.reduce((a, b) => {
    if ((b.nivel || 0) !== (a.nivel || 0)) return (b.nivel || 0) > (a.nivel || 0) ? b : a
    return (b.palier || 0) > (a.palier || 0) ? b : a
  })
})

function esRegistroPR(r) {
  if (!esTipoPeso.value) return false
  return mejorRMkg.value !== null && Math.abs(toKg(r.rm_calculado, r.unidad) - mejorRMkg.value) < 0.01
}

// ¿El último día (mejor RM del día más reciente) es también el PR histórico?
// Comparación en kg con tolerancia para evitar falsos negativos por redondeo kg↔lbs.
const ultimoEsPR = computed(() => {
  if (!registrosPorDia.value.length || mejorRMkg.value === null) return false
  const ult = registrosPorDia.value[registrosPorDia.value.length - 1]
  return Math.abs(toKg(ult.rm_calculado, ult.unidad) - mejorRMkg.value) < 0.01
})

// ── Fórmulas 1RM ──────────────────────────────────────────────
function calc1RM(w, r) {
  if (r === 1) return round1(w)
  const vals = [
    w * (36 / (37 - r)),
    w * (1 + r / 30),
    (100 * w) / (101.3 - 2.67123 * r),
    w * (1 + 0.025 * r),
    w * Math.pow(r, 0.1),
    (100 * w) / (52.2 + 41.9 * Math.exp(-0.055 * r)),
    (100 * w) / (48.8 + 53.8 * Math.exp(-0.075 * r)),
  ]
  return Math.round(vals.reduce((a, b) => a + b) / vals.length * 10) / 10
}

function calcPesoParaReps(rm, r) {
  if (r === 1) return Array(7).fill(round1(rm))
  const vals = [
    rm * (37 - r) / 36,
    rm / (1 + r / 30),
    rm * (101.3 - 2.67123 * r) / 100,
    rm / (1 + 0.025 * r),
    rm / Math.pow(r, 0.1),
    rm * (52.2 + 41.9 * Math.exp(-0.055 * r)) / 100,
    rm * (48.8 + 53.8 * Math.exp(-0.075 * r)) / 100,
  ]
  return vals.map(v => Math.round(v * 10) / 10)
}

const tablaRepMax = computed(() => {
  if (!esTipoPeso.value || !ultimoRM.value) return []
  const rm = ultimoRM.value
  return Array.from({ length: 10 }, (_, i) => {
    const r = i + 1
    const vals = calcPesoParaReps(rm, r)
    const promedio = Math.round(vals.reduce((a, b) => a + b) / vals.length * 10) / 10
    return { reps: r, promedio }
  })
})

// ── Helpers de series (barra / corporal_lastre) ───────────────
const corporalConvertido = computed(() => {
  if (tipo.value !== 'corporal_lastre') return 0
  // Editando: usar el peso corporal congelado del registro (ya en su unidad).
  if (corporalBaseEdit.value !== null) return corporalBaseEdit.value
  const corporalKg = Number(pesoCorporalAuto.value || formPesoCorporal.value) || 0
  return formUnidad.value === 'lbs' ? round1(corporalKg * KG_PER_LB) : corporalKg
})

const seriesConRM = computed(() =>
  formSeries.value.map(s => {
    const peso = tipo.value === 'corporal_lastre'
      ? round1(corporalConvertido.value + (s.lastre || 0))
      : s.peso
    const rm = peso > 0 && s.reps > 0 ? calc1RM(peso, s.reps) : null
    return { ...s, peso, rm }
  })
)

const mejorSerie = computed(() =>
  seriesConRM.value.reduce(
    (best, s) => (!best || (s.rm !== null && (best.rm === null || s.rm > best.rm))) ? s : best,
    null
  )
)

function modalAgregarSerie() {
  const reps = Number(formNuevaReps.value)
  if (!reps || reps < 1) return
  if (tipo.value === 'barra') {
    const peso = Number(formNuevaPeso.value)
    if (!peso || peso <= 0) return
    formSeries.value.push({ peso, reps })
  } else {
    formSeries.value.push({ lastre: Number(formNuevaPeso.value) || 0, reps })
  }
  formNuevaPeso.value = ''
  formNuevaReps.value = ''
}

function modalQuitarSerie(i) {
  formSeries.value.splice(i, 1)
}

// ── Preview 1RM en modal ───────────────────────────────────────
const previewRM = computed(() => mejorSerie.value?.rm ?? null)

const esPR = computed(() => {
  if (!previewRM.value) return false
  if (mejorRMkg.value === null) return true
  return toKg(previewRM.value, formUnidad.value) > mejorRMkg.value
})

// ── API ────────────────────────────────────────────────────────
async function cargar() {
  if (!ejercicio.value) return
  cargando.value = true
  try {
    const { data } = await api.get(`/marcas/${encodeURIComponent(ejercicio.value)}`)
    registros.value = data
  } finally {
    cargando.value = false
  }
}

async function cargarPesoCorporal() {
  if (tipo.value !== 'corporal_lastre') return
  try {
    const { data } = await api.get('/salud/peso')
    if (Array.isArray(data) && data.length) {
      // último por fecha
      const ord = [...data].sort((a, b) => (a.fecha < b.fecha ? -1 : 1))
      const ultimo = ord[ord.length - 1]
      pesoCorporalAuto.value = ultimo.peso_kg || null
    }
  } catch { /* silencioso */ }
}

function abrirModal() {
  errorForm.value = ''
  corporalBaseEdit.value = null
  mostrarModal.value = true
}

function cerrarModal() {
  mostrarModal.value = false
  editandoId.value = null
  corporalBaseEdit.value = null
  formSeries.value = []
  formNuevaPeso.value = ''
  formNuevaReps.value = ''
  formReps.value = ''
  formPesoCorporal.value = ''
  formNivel.value = ''
  formPalier.value = ''
  formNotas.value = ''
  errorForm.value = ''
  quickError.value = ''
}

function abrirModalEditar(r) {
  editandoId.value = r.id
  formFecha.value = r.fecha
  formNotas.value = r.notas || ''
  formUnidad.value = r.unidad || 'kg'
  formSeries.value = []
  corporalBaseEdit.value = null

  if (esTipoPeso.value) {
    // Registros legacy (sin series) → tratarlos como una única serie peso×reps.
    const series = (r.series && r.series.length)
      ? r.series
      : (r.peso != null && r.repeticiones != null
          ? [{ peso: r.peso, repeticiones: r.repeticiones }]
          : [])

    if (tipo.value === 'corporal_lastre') {
      // Peso corporal del snapshot = peso total − lastre del registro. Si el
      // registro no guardó lastre (legacy), caer al peso corporal actual de Mi Salud.
      let corp = null
      if (r.peso != null && r.peso_adicional != null) {
        corp = round1(r.peso - r.peso_adicional)   // ya en r.unidad
      } else if (pesoCorporalAuto.value) {
        const k = Number(pesoCorporalAuto.value)
        corp = formUnidad.value === 'lbs' ? round1(k * KG_PER_LB) : k
      }
      corporalBaseEdit.value = corp
      const base = corp ?? 0
      formSeries.value = series.map(s => ({ lastre: Math.max(0, round1(s.peso - base)), reps: s.repeticiones }))
    } else {
      formSeries.value = series.map(s => ({ peso: s.peso, reps: s.repeticiones }))
    }
  } else if (tipo.value === 'reps') {
    formReps.value = r.repeticiones
  } else if (tipo.value === 'leger') {
    formNivel.value = r.nivel
    formPalier.value = r.palier
  }

  errorForm.value = ''
  mostrarModal.value = true
}

async function guardar() {
  guardando.value = true
  errorForm.value = ''
  try {
    const payload = {
      ejercicio: ejercicio.value,
      fecha: formFecha.value,
      notas: formNotas.value || null,
      unidad: formUnidad.value,
    }

    if (tipo.value === 'barra' || tipo.value === 'corporal_lastre') {
      if (formSeries.value.length === 0) {
        errorForm.value = 'Agrega al menos una serie antes de guardar.'
        return
      }
      payload.series = seriesConRM.value.map(s => ({ peso: s.peso, repeticiones: s.reps }))
      if (tipo.value === 'corporal_lastre' && mejorSerie.value) {
        // Lastre de la mejor serie (la que define el rm_calculado del registro)
        payload.peso_adicional = Number(mejorSerie.value.lastre) || 0
      }
    } else if (tipo.value === 'reps') {
      payload.repeticiones = Number(formReps.value)
    } else if (tipo.value === 'leger') {
      payload.nivel  = Number(formNivel.value)
      payload.palier = Number(formPalier.value)
    }

    if (editandoId.value !== null) {
      await api.patch(`/marcas/${editandoId.value}`, payload)
    } else {
      await api.post('/marcas/', payload)
    }
    cerrarModal()
    await cargar()
  } catch (e) {
    const d = e.response?.data?.detail
    errorForm.value = Array.isArray(d) ? d[0].msg : (d || 'Error al guardar.')
  } finally {
    guardando.value = false
  }
}

async function eliminar(r) {
  if (!confirm(`¿Eliminar el registro del ${formatFecha(r.fecha)}?`)) return
  try {
    await api.delete(`/marcas/${r.id}`)
    await cargar()
  } catch (e) {
    alert(e.response?.data?.detail || 'Error al eliminar.')
  }
}

// ── Ciclo de vida ──────────────────────────────────────────────
onMounted(() => {
  if (!ejercicio.value) { router.replace({ name: 'Marcas' }); return }
  cargar()
  cargarPesoCorporal()
})

watch(
  () => route.params.ejercicio,
  () => {
    destruirChart()
    registros.value = []
    pesoCorporalAuto.value = null
    formFecha.value = new Date().toISOString().slice(0, 10)
    quickPeso.value = ''
    quickReps.value = ''
    quickError.value = ''
    cargar()
    cargarPesoCorporal()
  }
)

onUnmounted(destruirChart)
</script>

<style scoped>
.animate-fade-in-up { animation: fadeInUp 0.35s ease-out; }
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
