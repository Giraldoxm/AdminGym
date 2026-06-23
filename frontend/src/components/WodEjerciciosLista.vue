<template>
  <div v-if="ejercicios && ejercicios.length > 0" :class="dark ? 'space-y-2' : 'space-y-1.5'">
    <div
      v-for="(ej, idx) in ejercicios"
      :key="ej.ejercicio_id ?? idx"
      class="flex items-start gap-2 rounded-lg px-3 py-2"
      :class="dark ? 'bg-white/10' : 'bg-gray-50 border border-gray-100'"
    >
      <span class="text-xs font-bold flex-shrink-0 mt-0.5" :class="dark ? 'opacity-70' : 'text-gray-400'">{{ idx + 1 }}.</span>
      <div class="flex-1 min-w-0">
        <p class="font-semibold text-sm leading-tight" :class="dark ? 'text-white' : 'text-gray-800'">{{ ej.nombre }}</p>
        <p v-if="ej.descripcion" class="text-xs mt-0.5" :class="dark ? 'opacity-70' : 'text-gray-400'">{{ ej.descripcion }}</p>
        <div v-if="ej.rep_min || ej.rep_max || ej.rir != null || ej.porcentaje_rm != null || ej.tiempo_segundos" class="flex items-center gap-2 mt-1 flex-wrap">
          <span
            v-if="ej.rep_min || ej.rep_max"
            class="inline-flex items-center gap-0.5 text-xs font-semibold px-2 py-0.5 rounded-full"
            :class="dark ? 'bg-white/20 text-white' : 'bg-red-50 text-red-700'"
          >
            {{ ej.rep_min ?? '?' }}–{{ ej.rep_max ?? '?' }} reps
          </span>
          <span
            v-if="ej.porcentaje_rm != null"
            class="inline-flex items-center gap-0.5 text-xs font-semibold px-2 py-0.5 rounded-full"
            :class="dark ? 'bg-white/20 text-white' : 'bg-orange-50 text-orange-700'"
          >
            {{ ej.porcentaje_rm }}% 1RM
          </span>
          <span
            v-if="ej.tiempo_segundos"
            class="inline-flex items-center gap-0.5 text-xs font-semibold px-2 py-0.5 rounded-full"
            :class="dark ? 'bg-white/20 text-white' : 'bg-blue-50 text-blue-700'"
          >
            {{ formatTiempo(ej.tiempo_segundos) }}
          </span>
          <span
            v-if="ej.rir != null"
            class="inline-flex items-center gap-0.5 text-xs font-semibold px-2 py-0.5 rounded-full"
            :class="dark ? 'bg-white/10 text-white/80' : 'bg-gray-100 text-gray-600'"
          >
            RIR {{ ej.rir }}
          </span>
        </div>
        <p v-if="ej.notas" class="text-xs mt-0.5 whitespace-pre-line" :class="dark ? 'opacity-90' : 'text-gray-500'">{{ ej.notas }}</p>
      </div>
      <a
        v-if="ej.video_url"
        :href="ej.video_url"
        target="_blank"
        rel="noopener noreferrer"
        class="flex-shrink-0 inline-flex items-center gap-1 text-xs font-semibold rounded-md px-2 py-1 transition-colors"
        :class="dark ? 'bg-white/20 hover:bg-white/30 text-white' : 'bg-red-50 hover:bg-red-100 text-red-600'"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" /></svg>
        Video
      </a>
    </div>
  </div>
</template>

<script setup>
defineProps({
  ejercicios: { type: Array, default: () => [] },
  dark: { type: Boolean, default: false },
})

function formatTiempo(seg) {
  if (!seg) return ''
  const m = Math.floor(seg / 60)
  const s = seg % 60
  if (m === 0) return `${s}s`
  if (s === 0) return `${m}min`
  return `${m}:${String(s).padStart(2, '0')}`
}
</script>
