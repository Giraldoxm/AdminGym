// Tipos de ejercicio:
// - barra            → peso + reps → 1RM (fórmulas)
// - corporal_lastre  → peso corporal (de salud) + lastre opcional + reps → 1RM
// - reps             → solo repeticiones máximas (sin 1RM)
// - leger            → nivel + palier (sin peso ni reps, sin 1RM)
export const EJERCICIOS_MARCAS = [
  { nombre: 'Back Squat',      tipo: 'barra' },
  { nombre: 'Deadlift',        tipo: 'barra' },
  { nombre: 'Clean',           tipo: 'barra' },
  { nombre: 'Clean and Jerk',  tipo: 'barra' },
  { nombre: 'Snatch',          tipo: 'barra' },
  { nombre: 'Bench Press',     tipo: 'barra' },
  { nombre: 'Press Militar',   tipo: 'barra' },
  { nombre: 'Dominadas',       tipo: 'corporal_lastre' },
  { nombre: 'Push Up',         tipo: 'reps' },
  { nombre: 'Air Squat',       tipo: 'reps' },
  { nombre: 'Sit Up',          tipo: 'reps' },
  { nombre: 'Test de Léger',   tipo: 'leger' },
]

export function tipoDe(nombre) {
  const e = EJERCICIOS_MARCAS.find(x => x.nombre === nombre)
  return e ? e.tipo : 'barra'
}
