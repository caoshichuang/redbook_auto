<template>
  <div class="page">
    <!-- 侧边栏 navbar-vertical -->
    <aside class="navbar navbar-vertical navbar-expand-lg" data-bs-theme="dark">
      <div class="container-fluid">
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#sidebar-menu">
          <span class="navbar-toggler-icon"></span>
        </button>
        <h1 class="navbar-brand navbar-brand-autodark">
          <a href="/" class="d-flex align-items-center gap-2">
            <span style="font-size:1.4rem;">⛵</span>
            <span>FinanceSail</span>
          </a>
        </h1>
        <div class="collapse navbar-collapse" id="sidebar-menu">
          <ul class="navbar-nav pt-lg-3">
            <li v-for="item in menuItems" :key="item.path" class="nav-item">
              <router-link :to="item.path" class="nav-link" :class="{ active: isActive(item.path) }">
                <span class="nav-link-icon d-md-none d-lg-inline-block">
                  <svg xmlns="http://www.w3.org/2000/svg" class="icon" width="24" height="24" viewBox="0 0 24 24"
                    stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
                    <path :d="item.iconPath" />
                    <path v-if="item.iconPath2" :d="item.iconPath2" />
                  </svg>
                </span>
                <span class="nav-link-title">{{ t(item.i18nKey) }}</span>
              </router-link>
            </li>
          </ul>
        </div>
      </div>
    </aside>

    <!-- 主体区域 -->
    <div class="page-wrapper">
      <!-- 顶部 header -->
      <header class="navbar navbar-expand-md d-none d-lg-flex d-print-none">
        <div class="container-xl">
          <div class="navbar-nav flex-row order-md-last ms-auto gap-2 align-items-center">
            <!-- 语言切换按钮 -->
            <button class="btn btn-ghost-secondary btn-sm" @click="toggleLocale">
              {{ locale === 'zh' ? 'EN' : '中文' }}
            </button>
            <!-- 用户下拉 -->
            <div class="nav-item dropdown">
              <a href="#" class="nav-link d-flex lh-1 text-reset p-0" data-bs-toggle="dropdown">
                <span class="avatar avatar-sm" style="background-image: url()">
                  <svg xmlns="http://www.w3.org/2000/svg" class="icon" width="24" height="24" viewBox="0 0 24 24"
                    stroke-width="2" stroke="currentColor" fill="none">
                    <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
                    <circle cx="12" cy="7" r="4" />
                    <path d="M6 21v-2a4 4 0 0 1 4 -4h4a4 4 0 0 1 4 4v2" />
                  </svg>
                </span>
                <div class="d-none d-xl-block ps-2">
                  <div>Admin</div>
                  <div class="mt-1 small text-secondary">Administrator</div>
                </div>
              </a>
              <div class="dropdown-menu dropdown-menu-end dropdown-menu-arrow">
                <a class="dropdown-item text-danger" href="#" @click.prevent="handleLogout">
                  <svg xmlns="http://www.w3.org/2000/svg" class="icon dropdown-item-icon text-danger me-2" width="24" height="24" viewBox="0 0 24 24"
                    stroke-width="2" stroke="currentColor" fill="none">
                    <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
                    <path d="M14 8v-2a2 2 0 0 0 -2 -2h-7a2 2 0 0 0 -2 2v12a2 2 0 0 0 2 2h7a2 2 0 0 0 2 -2v-2" />
                    <path d="M7 12h14l-3 -3m0 6l3 -3" />
                  </svg>
                  {{ t('nav.logout') }}
                </a>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- 页面内容 -->
      <div class="page-body">
        <div class="container-xl">
          <router-view />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { i18n } from '../i18n/index.js'

const route = useRoute()
const router = useRouter()
const { t, locale } = useI18n()

const menuItems = [
  {
    path: '/dashboard',
    i18nKey: 'nav.dashboard',
    iconPath: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6'
  },
  {
    path: '/users',
    i18nKey: 'nav.users',
    iconPath: 'M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2',
    iconPath2: 'M9 7 a4 4 0 1 0 8 0 a4 4 0 0 0 -8 0'
  },
  {
    path: '/content',
    i18nKey: 'nav.content',
    iconPath: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z',
    iconPath2: 'M14 2v6h6M16 13H8M16 17H8M10 9H8'
  },
  {
    path: '/distribution',
    i18nKey: 'nav.distribution',
    iconPath: 'M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8',
    iconPath2: 'M16 6l-4-4-4 4M12 2v13'
  },
  {
    path: '/subscriptions',
    i18nKey: 'nav.subscriptions',
    iconPath: 'M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9',
    iconPath2: 'M13.73 21a2 2 0 0 1-3.46 0'
  },
  {
    path: '/config',
    i18nKey: 'nav.config',
    iconPath: 'M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z',
    iconPath2: 'M12 15 a3 3 0 1 0 6 0 a3 3 0 0 0 -6 0'
  },
  {
    path: '/logs',
    i18nKey: 'nav.logs',
    iconPath: 'M3 12h18M3 6h18M3 18h18'
  }
]

const isActive = (path) => {
  return route.path === path || route.path.startsWith(path + '/')
}

const toggleLocale = () => {
  const newLocale = locale.value === 'zh' ? 'en' : 'zh'
  i18n.global.locale.value = newLocale
  localStorage.setItem('locale', newLocale)
}

const handleLogout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
.page {
  min-height: 100vh;
}

.navbar-brand {
  font-size: 1rem;
  font-weight: 700;
}

.navbar-brand a {
  text-decoration: none;
  color: inherit;
}
</style>
