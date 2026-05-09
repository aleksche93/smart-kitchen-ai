import { reactive, inject } from 'vue'
import uk from '../locales/uk.json'
import en from '../locales/en.json'

const locales = { uk, en }

export const i18nState = reactive({
  locale: 'en'
})

// Simple get with fallback
function getNestedValue(obj, path) {
  return path.split('.').reduce((acc, part) => acc && acc[part], obj)
}

function t(key, params = {}) {
  const translations = locales[i18nState.locale] || locales['uk']
  let text = getNestedValue(translations, key) || key
  
  // Only interpolate if params is a valid object
  if (params !== null && typeof params === 'object' && !Array.isArray(params)) {
    for (const [k, v] of Object.entries(params)) {
      // Escape special characters in key for RegExp
      const escapedKey = k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
      text = text.replace(new RegExp(`{${escapedKey}}`, 'g'), v)
    }
  }
  return text
}

export const i18nPlugin = {
  install(app) {
    app.config.globalProperties.$t = t
    app.provide('i18n', { t, i18nState })
  }
}

// Composable to use inside script setup
export function useI18n() {
  return { t, i18nState }
}
