import { createI18n } from 'vue-i18n'
import zh from './zh.js'
import en from './en.js'

const savedLocale = localStorage.getItem('locale') || 'zh'

export const i18n = createI18n({
  legacy: false,
  locale: savedLocale,
  fallbackLocale: 'en',
  messages: { zh, en }
})
