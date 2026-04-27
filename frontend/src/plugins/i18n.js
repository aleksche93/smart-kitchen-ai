import { reactive, inject } from 'vue'
import uk from '../locales/uk.json'
import en from '../locales/en.json'

const locales = { uk, en }

export const i18nState = reactive({
  locale: 'uk'
})

// Simple get with fallback
function getNestedValue(obj, path) {
  return path.split('.').reduce((acc, part) => acc && acc[part], obj)
}

function t(key, params = {}) {
  const translations = locales[i18nState.locale] || locales['uk']
  let text = getNestedValue(translations, key) || key
  
  // Replace {param} placeholders
  for (const [k, v] of Object.entries(params)) {
    text = text.replace(new RegExp(`{${k}}`, 'g'), v)
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
