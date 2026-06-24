<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-900 px-4 py-8">
    <div class="max-w-md w-full bg-white rounded-xl shadow-lg overflow-hidden relative">
      <div class="absolute top-0 left-0 w-full h-2 bg-indigo-600"></div>

      <div class="text-center pt-10 pb-6 px-8">
        <div class="inline-flex items-center justify-center w-14 h-14 rounded-full bg-indigo-100 text-indigo-600 mb-3 shadow-sm">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h1 class="text-2xl font-extrabold text-gray-800 tracking-tight">Panel SuperAdmin</h1>
        <p class="text-sm text-gray-500 mt-1">Gestión de la plataforma</p>
      </div>

      <form @submit.prevent="handleLogin" class="px-8 pb-8 space-y-5">
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1.5">Correo Electrónico</label>
          <input v-model="email" type="email" required
            class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all text-sm"
            placeholder="super@ejemplo.com">
        </div>
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1.5">Contraseña</label>
          <input v-model="password" type="password" required
            class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all text-sm"
            placeholder="••••••••">
        </div>

        <div v-if="error" class="bg-red-50 text-red-600 text-sm p-3 rounded-lg border border-red-100 font-medium">
          {{ error }}
        </div>

        <button type="submit" :disabled="loading"
          class="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 text-white font-bold py-3 rounded-lg shadow-md transition-all flex items-center justify-center gap-2">
          <span v-if="loading" class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></span>
          {{ loading ? 'Autenticando...' : 'Ingresar' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import superApi from '../superApi'

const router = useRouter()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const handleLogin = async () => {
  error.value = ''
  loading.value = true
  try {
    const formData = new URLSearchParams()
    formData.append('username', email.value)
    formData.append('password', password.value)
    const { data } = await superApi.post('/superadmin/login', formData)
    localStorage.setItem('superToken', data.access_token)
    router.push('/superadmin')
  } catch (e) {
    error.value = e.response?.status === 401
      ? 'Credenciales incorrectas.'
      : 'Error al conectar con el servidor.'
  } finally {
    loading.value = false
  }
}
</script>
