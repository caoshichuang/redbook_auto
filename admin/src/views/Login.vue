<template>
  <div class="antialiased min-vh-100 d-flex flex-column justify-content-center" style="background: linear-gradient(135deg, #1a2332 0%, #2d3f5c 50%, #1e3a5f 100%);">
    <div class="container container-tight py-4">
      <div class="text-center mb-4">
        <a href="." class="navbar-brand navbar-brand-autodark">
          <span style="font-size: 3rem;">⛵</span>
        </a>
      </div>

      <div class="card card-md shadow-lg" style="border: none; border-radius: 12px; overflow: hidden;">
        <div class="card-body" style="padding: 2.5rem;">
          <h2 class="h2 text-center mb-1 fw-bold" style="color: #1a2332;">{{ t('login.title') }}</h2>
          <p class="text-muted text-center mb-4" style="font-size: 0.875rem;">{{ t('login.subtitle') }}</p>

          <!-- 错误提示 -->
          <div v-if="errorMsg" class="alert alert-danger alert-dismissible mb-3" role="alert">
            <div class="d-flex">
              <div>
                <svg xmlns="http://www.w3.org/2000/svg" class="icon alert-icon" width="24" height="24" viewBox="0 0 24 24"
                  stroke-width="2" stroke="currentColor" fill="none">
                  <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
                  <circle cx="12" cy="12" r="9" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
              </div>
              <div>{{ errorMsg }}</div>
            </div>
            <button type="button" class="btn-close" @click="errorMsg = ''"></button>
          </div>

          <div class="mb-3">
            <label class="form-label" for="username">{{ t('login.username') }}</label>
            <input
              id="username"
              type="text"
              class="form-control form-control-lg"
              v-model="form.username"
              :placeholder="t('login.usernamePlaceholder')"
              autocomplete="username"
              @keyup.enter="handleLogin"
            />
          </div>

          <div class="mb-4">
            <label class="form-label" for="password">{{ t('login.password') }}</label>
            <input
              id="password"
              type="password"
              class="form-control form-control-lg"
              v-model="form.password"
              :placeholder="t('login.passwordPlaceholder')"
              autocomplete="current-password"
              @keyup.enter="handleLogin"
            />
          </div>

          <div class="form-footer">
            <button
              type="submit"
              class="btn btn-primary btn-lg w-100"
              :disabled="loading"
              @click="handleLogin"
              style="background: linear-gradient(135deg, #206bc4 0%, #1a56a0 100%); border: none; font-weight: 600; letter-spacing: 0.5px;"
            >
              <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
              {{ loading ? t('common.loading') : t('login.submit') }}
            </button>
          </div>
        </div>
      </div>

      <div class="text-center text-muted mt-3" style="font-size: 0.8rem; opacity: 0.7; color: #ccc !important;">
        FinanceSail &copy; {{ new Date().getFullYear() }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { authApi } from '../utils/api'

const router = useRouter()
const { t } = useI18n()
const loading = ref(false)
const errorMsg = ref('')

const form = reactive({
  username: '',
  password: ''
})

const handleLogin = async () => {
  if (!form.username || !form.password) {
    errorMsg.value = t('login.error')
    return
  }

  loading.value = true
  errorMsg.value = ''
  try {
    const res = await authApi.login(form.username, form.password)
    localStorage.setItem('token', res.access_token)
    router.push('/dashboard')
  } catch (error) {
    errorMsg.value = error.response?.data?.detail || t('login.error')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.card {
  backdrop-filter: blur(10px);
}

.form-control:focus {
  border-color: #206bc4;
  box-shadow: 0 0 0 0.25rem rgba(32, 107, 196, 0.15);
}
</style>
