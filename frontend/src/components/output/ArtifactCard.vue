<template>
  <div
    class="artifact-card group relative transition-all duration-500 ease-out"
    :class="[isFocused ? 'scale-105 z-50' : 'hover:scale-[1.02]', typeColorClass]"
    :style="spatialStyle"
    @click="$emit('focus')"
  >
    <!-- Focus Mode: Backdrop Blur Overlay (показується тільки при фокусі) -->
    <Transition name="focus-glow">
      <div v-if="isFocused"
           class="absolute inset-0 rounded-2xl pointer-events-none"
           style="box-shadow: 0 0 60px var(--artifact-glow-color, rgba(250,204,21,0.2)), 0 0 120px var(--artifact-glow-color, rgba(250,204,21,0.05)); backdrop-filter: blur(2px);"
      />
    </Transition>

    <!-- Glow Ring (hover) -->
    <div class="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
         :class="glowClass"></div>

    <!-- Card Body -->
    <div class="relative bg-slate-900/90 backdrop-blur-xl rounded-2xl border overflow-hidden transition-all duration-300"
         @click.stop
         :class="isFocused ? `border-slate-500/60 shadow-2xl` : 'border-slate-700/50 shadow-lg'">

      <!-- Header -->
      <div class="flex items-center justify-between px-3 py-2 border-b border-slate-700/40">
        <div class="flex items-center gap-2">
          <span class="text-lg">{{ typeIcon }}</span>
          <div>
            <h3 class="text-sm font-bold text-slate-200 truncate">{{ artifact.title || 'Artifact' }}</h3>
            <span class="text-[10px] uppercase tracking-widest font-bold text-slate-400/80">{{ localizedType }}</span>
          </div>
        </div>
        <button v-if="isFocused" @click.stop="$emit('close')"
                class="text-slate-400 hover:text-keYellow hover:bg-slate-800/50 rounded-full transition-all duration-200 p-2 cursor-pointer">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Dynamic Polymorphic Content -->
      <div class="p-3 max-h-[420px] overflow-y-auto custom-scrollbar max-w-full break-words">
        <!-- Typed artifact component -->
        <component
          v-if="artifactComponent && artifact.data && !isDataMalformed"
          :is="artifactComponent"
          :data="artifact.data"
          :ref="el => { artifactComponentRef = el }"
          @cook="handleCook"
        />

        <!-- Graceful fallback: malformed / unsupported type -->
        <div v-else class="flex flex-col items-center justify-center py-6 text-slate-500 space-y-2">
          <span class="text-2xl">🤔</span>
          <p class="text-xs italic text-center">
            {{ isDataMalformed ? 'Дані артефакту пошкоджені або порожні' : `Тип "${artifact.artifact_type}" не підтримується` }}
          </p>
          <!-- Raw data dump для debug -->
          <details v-if="isDev" class="text-[10px] text-slate-600 max-w-full">
            <summary class="cursor-pointer">raw data</summary>
            <pre class="mt-1 text-left break-all whitespace-pre-wrap">{{ JSON.stringify(artifact.data, null, 2) }}</pre>
          </details>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, shallowRef, provide } from 'vue'
import RecipeArtifact from './artifacts/RecipeArtifact.vue'
import ShoppingListArtifact from './artifacts/ShoppingListArtifact.vue'
import WasteAlertArtifact from './artifacts/WasteAlertArtifact.vue'
import { useKitchenAPI } from '../../composables/useKitchenAPI'
import { useLayoutStore } from '../../stores/layoutStore'
import { useI18n } from '../../plugins/i18n'

const layoutStore = useLayoutStore()
const { t } = useI18n()

const props = defineProps({
  artifact: { type: Object, required: true },   // { artifact_type, title, data: {...} }
  rotationAngle: { type: Number, default: 0 },
  zIndex: { type: Number, default: 1 },
  isFocused: { type: Boolean, default: false }
})

const emit = defineEmits(['focus', 'close'])

// --- Polymorphic component map ---
const ARTIFACT_MAP = {
  RECIPE: RecipeArtifact,
  SHOPPING_LIST: ShoppingListArtifact,
  WASTE_ALERT: WasteAlertArtifact
}

const artifactComponent = computed(() => ARTIFACT_MAP[props.artifact?.artifact_type] || null)

// Ref до дочірнього компонента (для виклику onCookResult)
const artifactComponentRef = shallowRef(null)

// --- Localization Helpers ---
const localizedType = computed(() => {
  const i18nKey = `artifact.types.${props.artifact?.artifact_type}`
  const translation = t(i18nKey)
  return translation !== i18nKey ? translation : props.artifact?.artifact_type
})

provide('localizeKey', (key) => {
  if (!key) return ''
  const i18nKey = `artifact.keys.${key.toLowerCase()}`
  const translation = t(i18nKey)
  return translation !== i18nKey ? translation : key
})

// --- Type safety guard ---
const isDataMalformed = computed(() => {
  const d = props.artifact?.data
  return !d || typeof d !== 'object' || Array.isArray(d) || Object.keys(d).length === 0 || !!d.error
})

const isDev = computed(() => import.meta.env.DEV)

// --- Design tokens ---
const typeConfig = computed(() => {
  const configs = {
    RECIPE:        { icon: '🍽️', glow: 'shadow-[0_0_30px_rgba(250,204,21,0.25)]',   glowColor: 'rgba(250,204,21,0.4)' },
    SHOPPING_LIST: { icon: '🛒', glow: 'shadow-[0_0_30px_rgba(52,211,153,0.25)]',   glowColor: 'rgba(52,211,153,0.4)' },
    WASTE_ALERT:   { icon: '⚠️', glow: 'shadow-[0_0_30px_rgba(248,113,113,0.25)]',  glowColor: 'rgba(248,113,113,0.4)' },
    PREP_SCHEDULE: { icon: '📋', glow: 'shadow-[0_0_30px_rgba(96,165,250,0.25)]',   glowColor: 'rgba(96,165,250,0.4)' },
    TASK_LIST:     { icon: '✅', glow: 'shadow-[0_0_30_rgba(192,132,252,0.25)]',  glowColor: 'rgba(192,132,252,0.4)' }
  }
  return configs[props.artifact?.artifact_type] || configs.RECIPE
})

const typeIcon = computed(() => typeConfig.value.icon)
const typeColorClass = computed(() => '')
const glowClass = computed(() => typeConfig.value.glow)

// --- Spatial 2.5D transform + Zoom-In mount animation ---
const spatialStyle = computed(() => ({
  transform: props.isFocused 
    ? 'perspective(1200px) scale(1.1) rotateX(2deg)' 
    : `perspective(800px) rotateY(${props.rotationAngle}deg) scale(1)`,
  zIndex: props.isFocused ? 100 : props.zIndex,
  transition: 'transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1), z-index 0.3s',
  '--artifact-glow-color': typeConfig.value.glowColor,
  animation: props.isFocused ? 'none' : 'artifactZoomIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) both'
}))

// --- Cook handler: calls API, then notifies child via defineExpose ---
const { cookRecipe } = useKitchenAPI()

const handleCook = async (ingredients) => {
  try {
    const result = await cookRecipe(ingredients)
    // Передаємо результат назад до RecipeArtifact для feedback UI
    if (artifactComponentRef.value?.onCookResult) {
      artifactComponentRef.value.onCookResult(result)
    }
  } catch (err) {
    if (artifactComponentRef.value?.onCookResult) {
      artifactComponentRef.value.onCookResult({ deducted: [], not_found: ingredients, error: err.message })
    }
  }
}
</script>

<style scoped>
@keyframes artifactZoomIn {
  from { opacity: 0; transform: perspective(800px) scale(0.85) rotateY(var(--init-angle, 0deg)); }
  to   { opacity: 1; transform: perspective(800px) scale(1)    rotateY(var(--init-angle, 0deg)); }
}

.focus-glow-enter-active, .focus-glow-leave-active {
  transition: opacity 0.3s ease;
}
.focus-glow-enter-from, .focus-glow-leave-to {
  opacity: 0;
}

.custom-scrollbar::-webkit-scrollbar { width: 3px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: #334155; border-radius: 4px; }
</style>
