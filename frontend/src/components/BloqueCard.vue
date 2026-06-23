<template>
  <div class="border border-gray-100 rounded-2xl overflow-hidden bg-white shadow-sm">

    <!-- Header accordion -->
    <button
      @click="abierto = !abierto"
      class="w-full px-5 py-4 flex items-center justify-between gap-3 hover:bg-gray-50 transition-colors text-left">
      <div class="flex items-center gap-3 min-w-0">
        <h3 class="text-base font-extrabold text-gray-900 truncate">{{ bloque.bloque }}</h3>
        <span class="bg-red-100 text-red-700 font-black text-xs px-2.5 py-0.5 rounded-full whitespace-nowrap flex-shrink-0">
          {{ visibles.length }} {{ visibles.length === 1 ? 'persona' : 'personas' }}
        </span>
      </div>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-4 w-4 text-gray-400 transition-transform duration-200 flex-shrink-0"
        :class="abierto ? 'rotate-180' : ''"
        fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- Body -->
    <div v-if="abierto" class="border-t border-gray-50">
      <ul class="divide-y divide-gray-50">
        <li
          v-for="a in visibles"
          :key="a.usuario_id + a.hora_exacta"
          class="px-5 py-2.5 flex items-center justify-between gap-2">
          <span class="text-sm text-gray-700 font-medium truncate">{{ a.nombre }}</span>
          <span class="text-xs font-bold text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full whitespace-nowrap">
            {{ a.hora_exacta }}
          </span>
        </li>
      </ul>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  bloque:   { type: Object, required: true },
  busqueda: { type: String, default: '' },
})

const abierto = ref(false)

const visibles = computed(() => {
  const q = props.busqueda.trim().toLowerCase()
  return q
    ? props.bloque.asistentes.filter(a => a.nombre.toLowerCase().includes(q))
    : props.bloque.asistentes
})
</script>
