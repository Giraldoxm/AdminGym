<template>
  <div>
    <label class="block text-sm font-semibold text-gray-700 mb-1.5">Ejercicios</label>

    <!-- Filtro de categoría -->
    <div class="flex flex-wrap gap-1.5 mb-2">
      <button
        v-for="cat in ['', 'Cardio', 'Fuerza', 'Gimnasia', 'Olímpico', 'Otro']"
        :key="cat"
        type="button"
        @click="categoriaFiltro = cat"
        class="text-xs font-semibold px-2.5 py-1 rounded-full border transition-colors"
        :class="categoriaFiltro === cat
          ? 'bg-gray-800 text-white border-gray-800'
          : 'bg-white text-gray-400 border-gray-200 hover:border-gray-400'"
      >
        {{ cat || 'Todas' }}
      </button>
    </div>

    <!-- Selector + agregar -->
    <div class="flex gap-2 mb-3">
      <select
        v-model="seleccionado"
        class="flex-1 px-3 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all text-sm bg-white"
      >
        <option value="">Selecciona un ejercicio…</option>
        <option v-for="ej in disponibles" :key="ej.id" :value="ej.id">{{ ej.nombre }}</option>
      </select>
      <button
        type="button"
        @click="agregar"
        :disabled="!seleccionado"
        class="px-4 py-2.5 rounded-lg bg-gray-800 hover:bg-gray-900 text-white font-semibold text-sm transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
      >
        Agregar
      </button>
    </div>

    <p v-if="catalogo.length === 0" class="text-xs text-gray-400 italic mb-3">
      No hay ejercicios en el catálogo. Créalos en la sección <span class="font-semibold">Ejercicios</span>.
    </p>

    <!-- Lista de seleccionados -->
    <div v-if="items.length > 0" class="space-y-2">
      <div
        v-for="(it, idx) in items"
        :key="it.ejercicio_id"
        class="bg-gray-50 border border-gray-200 rounded-lg p-3"
      >
        <div class="flex items-center justify-between gap-2 mb-2">
          <div class="flex items-center gap-2 min-w-0">
            <span class="text-xs font-bold text-gray-400 w-5 flex-shrink-0">{{ idx + 1 }}.</span>
            <span class="font-semibold text-gray-800 text-sm truncate">{{ it.nombre }}</span>
            <span v-if="it.categoria" class="text-xs font-semibold px-1.5 py-0.5 rounded-full bg-gray-200 text-gray-500 flex-shrink-0">{{ it.categoria }}</span>
            <span v-if="it.descripcion" class="text-xs text-gray-400 truncate hidden sm:block">{{ it.descripcion }}</span>
            <span v-if="it.video_url" class="flex-shrink-0 inline-flex items-center text-red-500" title="Tiene video">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" /></svg>
            </span>
          </div>
          <div class="flex items-center gap-1 flex-shrink-0">
            <button type="button" @click="mover(idx, -1)" :disabled="idx === 0" class="p-1 rounded text-gray-400 hover:bg-gray-200 disabled:opacity-30" title="Subir">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" /></svg>
            </button>
            <button type="button" @click="mover(idx, 1)" :disabled="idx === items.length - 1" class="p-1 rounded text-gray-400 hover:bg-gray-200 disabled:opacity-30" title="Bajar">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
            </button>
            <button type="button" @click="quitar(idx)" class="p-1 rounded text-gray-400 hover:bg-red-100 hover:text-red-600" title="Quitar">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>
        </div>
        <!-- Rango de repeticiones + RIR -->
        <div class="flex gap-2 mb-2">
          <div class="flex items-center gap-1 flex-1">
            <input
              v-model.number="it.rep_min"
              type="number"
              min="1"
              max="999"
              placeholder="Reps mín"
              @input="emitir"
              class="w-full px-3 py-2 rounded-md border border-gray-200 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all text-sm text-center"
            />
            <span class="text-gray-400 font-bold flex-shrink-0">–</span>
            <input
              v-model.number="it.rep_max"
              type="number"
              min="1"
              max="999"
              placeholder="Reps máx"
              @input="emitir"
              class="w-full px-3 py-2 rounded-md border border-gray-200 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all text-sm text-center"
            />
          </div>
          <div class="flex items-center gap-1 w-28 flex-shrink-0">
            <span class="text-xs text-gray-400 font-semibold flex-shrink-0">RIR</span>
            <input
              v-model.number="it.rir"
              type="number"
              min="0"
              max="10"
              placeholder="–"
              @input="emitir"
              class="w-full px-3 py-2 rounded-md border border-gray-200 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all text-sm text-center"
            />
          </div>
        </div>
        <!-- %RM + Tiempo -->
        <div class="flex gap-2 mb-2">
          <div class="flex items-center gap-1 flex-1 min-w-0">
            <input
              v-model.number="it.porcentaje_rm"
              type="number"
              min="0"
              max="150"
              step="0.5"
              placeholder="% 1RM"
              @input="emitir"
              class="flex-1 min-w-0 px-3 py-2 rounded-md border border-gray-200 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all text-sm text-center"
            />
            <span class="text-xs text-gray-400 font-semibold flex-shrink-0">%RM</span>
          </div>
          <div class="flex items-center gap-1 flex-1 min-w-0">
            <span class="text-xs text-gray-400 font-semibold flex-shrink-0">T</span>
            <input
              v-model.number="it.tiempo_min"
              type="number"
              min="0"
              max="99"
              placeholder="mm"
              @input="emitir"
              class="flex-1 min-w-0 px-2 py-2 rounded-md border border-gray-200 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all text-sm text-center"
            />
            <span class="text-gray-300 font-bold flex-shrink-0">:</span>
            <input
              v-model.number="it.tiempo_seg"
              type="number"
              min="0"
              max="59"
              placeholder="ss"
              @input="emitir"
              class="flex-1 min-w-0 px-2 py-2 rounded-md border border-gray-200 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all text-sm text-center"
            />
          </div>
        </div>
        <input
          v-model="it.notas"
          type="text"
          placeholder="Notas: peso, esquema… (ej: 3 series @ 40kg)"
          @input="emitir"
          class="w-full px-3 py-2 rounded-md border border-gray-200 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all text-sm"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  catalogo: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue'])

function _expandir(e) {
  const t = e.tiempo_segundos ?? null
  return {
    ...e,
    tiempo_min: t != null ? Math.floor(t / 60) : null,
    tiempo_seg: t != null ? t % 60 : null,
  }
}

const items          = ref(props.modelValue.map(_expandir))
const categoriaFiltro = ref('')

watch(() => props.modelValue, (val) => {
  items.value = val.map(_expandir)
}, { deep: true })
const seleccionado = ref('')

const disponibles = computed(() => {
  let result = props.catalogo.filter(ej => !items.value.some(it => it.ejercicio_id === ej.id))
  if (categoriaFiltro.value) result = result.filter(ej => ej.categoria === categoriaFiltro.value)
  return result
})

function emitir() {
  const out = items.value.map(it => {
    const min = it.tiempo_min || 0
    const seg = it.tiempo_seg || 0
    const tiempo_segundos = (min > 0 || seg > 0) ? min * 60 + seg : null
    return { ...it, tiempo_segundos }
  })
  emit('update:modelValue', out)
}

function agregar() {
  if (!seleccionado.value) return
  const ej = props.catalogo.find(e => e.id === seleccionado.value)
  if (!ej) return
  items.value.push({ ejercicio_id: ej.id, nombre: ej.nombre, video_url: ej.video_url, descripcion: ej.descripcion || null, categoria: ej.categoria || null, notas: '', rep_min: null, rep_max: null, rir: null, porcentaje_rm: null, tiempo_min: null, tiempo_seg: null })
  seleccionado.value = ''
  emitir()
}

function quitar(idx) {
  items.value.splice(idx, 1)
  emitir()
}

function mover(idx, dir) {
  const destino = idx + dir
  if (destino < 0 || destino >= items.value.length) return
  const [el] = items.value.splice(idx, 1)
  items.value.splice(destino, 0, el)
  emitir()
}
</script>
