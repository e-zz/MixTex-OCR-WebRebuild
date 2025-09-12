import { createI18n } from 'vue-i18n'
import en from '../locales/en.js'
import zh from '../locales/zh.js'

// Get saved language or default to browser language
const savedLanguage = localStorage.getItem('language')
const browserLanguage = navigator.language.toLowerCase()
const defaultLanguage = savedLanguage || (browserLanguage.includes('zh') ? 'zh' : 'en')

const i18n = createI18n({
  legacy: false,
  locale: defaultLanguage,
  fallbackLocale: 'en',
  messages: {
    en,
    zh
  }
})

export default i18n