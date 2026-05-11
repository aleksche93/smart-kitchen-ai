<template>
  <div ref="containerRef" class="space-y-4 relative">
    <!-- Recipe Title & Meta -->
    <div class="flex items-center justify-between">
      <div class="flex flex-col">
        <h4 class="text-lg font-bold text-keYellow">{{ recipe.name || 'Untitled Recipe' }}</h4>
        <div v-if="recipe.harmony_score" class="flex items-center gap-1.5 mt-0.5">
          <div class="px-1.5 py-0.5 rounded text-[9px] font-black uppercase tracking-tighter shadow-sm"
               :class="harmonyClass">
            Harmony: {{ recipe.harmony_score }}
          </div>
          <span v-if="recipe.pairing_tips?.length" class="text-[9px] text-slate-500 italic">
            Try adding: {{ recipe.pairing_tips.join(', ') }}
          </span>
        </div>
      </div>
      <div class="flex gap-2 text-[10px] uppercase tracking-wider text-slate-400">
        <span v-if="recipe.time || recipe.estimated_duration">⏱ {{ recipe.time || recipe.estimated_duration }}</span>
        <span v-if="recipe.difficulty || recipe.recipe_complexity">📊 {{ recipe.difficulty || recipe.recipe_complexity }}</span>
      </div>
    </div>

    <!-- Sin-Sieve Audit Warning -->
    <Transition name="audit">
      <div v-if="recipe.audit?.has_issues" class="bg-amber-900/20 border border-amber-600/30 rounded-xl p-3 space-y-2">
        <div class="flex items-center gap-2 text-amber-400 font-bold text-xs uppercase tracking-widest">
          <span>⚠️ Sin-Sieve Audit ({{ recipe.audit.severity }})</span>
        </div>
        <ul class="text-xs text-amber-200/70 space-y-1 list-disc list-inside">
          <li v-for="(warn, i) in recipe.audit.warnings" :key="i">{{ warn }}</li>
        </ul>
      </div>
    </Transition>

    <!-- Ingredients -->
    <div v-if="ingredients.length" class="space-y-1">
      <h5 class="text-xs uppercase tracking-widest text-slate-400 font-bold">Ingredients</h5>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-1">  
        <div v-for="(ing, i) in ingredients" :key="i"
             class="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-slate-800/60 border border-slate-700/40 text-sm text-slate-300">
          <span class="text-xs opacity-60">•</span>
          <span>{{ ing }}</span>
        </div>
      </div>
    </div>

    <!-- Instructions -->
    <div v-if="instructions.length" class="space-y-2">
      <h5 class="text-xs uppercase tracking-widest text-slate-400 font-bold">Instructions</h5>
      <ol class="space-y-1.5 list-decimal list-inside text-sm text-slate-300">
        <li v-for="(step, i) in instructions" :key="i" class="leading-relaxed pl-1">{{ step }}</li>
      </ol>
    </div>

    <!-- Notes -->
    <p v-if="recipe.notes" class="text-xs italic text-slate-500 border-t border-slate-700/30 pt-2">{{ recipe.notes }}</p>

    <!-- Cook It! Button & Missing Items Feedback -->
    <div class="border-t border-slate-700/40 pt-3 mt-1 space-y-3">
      <!-- Phase 13.5: Transformed Missing Ingredients UI -->
      <Transition name="cook-result">
        <div v-if="cookResult" class="px-3 py-2 rounded-xl bg-slate-800/40 border border-slate-700/30">
          <p v-if="cookResult.deducted?.length" class="text-emerald-400/90 text-[11px] font-medium mb-2">
            ✅ {{ cookResult.deducted.join(', ') }}
          </p>
          
          <div v-if="cookResult.notFound?.length" class="space-y-2">
            <!-- Snarky Chef Comment -->
            <p class="text-red-400/90 text-[10px] font-black uppercase tracking-wider italic">
              "{{ $t('chef.troll.short_comment') || 'Good luck without these:' }}"
            </p>
            <!-- Missing Items Tags/Chips -->
            <div class="flex flex-wrap gap-1">
              <span v-for="(item, i) in cookResult.notFound" :key="i"
                    class="px-2 py-0.5 rounded-full bg-red-900/30 border border-red-500/20 text-[9px] font-bold text-red-300/80">
                {{ item }}
              </span>
            </div>
          </div>
        </div>
      </Transition>

    <div class="flex justify-end h-8" ref="buttonWrapperRef">
        <button
          ref="buttonRef"
          @click="handleCook"
          @mouseover="handleButtonHover"
          :disabled="cookLoading || cookDone"
          class="w-auto h-full px-3 rounded-md text-[10px] font-black uppercase tracking-widest flex items-center justify-center gap-1.5 transition-all shadow-sm relative"
          :style="buttonStyle"
          :class="buttonClasses"
        >
          <template v-if="cookLoading">
            <svg class="animate-spin h-3 w-3" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          </template>
          <span v-else-if="cookDone">🍽️ {{ $t('artifact.recipe.done') || 'Cooked' }}</span>
          <span v-else>🍳 {{ $t('artifact.recipe.cook_btn') || 'Cook It' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onUnmounted } from 'vue'
import { useI18n } from '../../../plugins/i18n'

const props = defineProps({
  data: { type: Object, required: true }
})

const emit = defineEmits(['cook'])
const { t } = useI18n()

const recipe = computed(() => props.data || {})
const ingredients = computed(() => {
  const raw = recipe.value.ingredients
  return Array.isArray(raw) ? raw : []
})
const instructions = computed(() => {
  const raw = recipe.value.instructions
  return Array.isArray(raw) ? raw : []
})

// Cook state
const cookLoading = ref(false)
const cookDone = ref(false)
const cookResult = ref(null)

const harmonyClass = computed(() => {
  const score = recipe.value.harmony_score || 0
  if (score >= 3.5) return 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
  if (score >= 2.5) return 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
  return 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
})

// Fleeing Button State
const isFleeing = ref(false)
const isAlarmLocked = ref(false)
const isShaking = ref(false)
const buttonTranslateX = ref(0)
const buttonTranslateY = ref(0)
const containerRef = ref(null)
const buttonRef = ref(null)
const buttonWrapperRef = ref(null)
let fleeTimer = null

const buttonStyle = computed(() => {
  if (isFleeing.value) {
    return {
      transform: `translate(${buttonTranslateX.value}px, ${buttonTranslateY.value}px)`,
      transition: 'transform 0.08s ease-out'
    }
  }
  return { transform: 'translate(0px, 0px)', transition: 'transform 0.3s ease-out' }
})

const buttonClasses = computed(() => {
  if (cookDone.value) return 'bg-emerald-900/30 border border-emerald-700/40 text-emerald-400 cursor-default'
  if (cookLoading.value) return 'bg-slate-800/60 border border-slate-600/40 text-slate-400 cursor-wait'
  if (isAlarmLocked.value) {
    return `bg-slate-800/60 border border-red-500/50 text-red-400 cursor-not-allowed ${isShaking.value ? 'animate-shake' : ''}`
  }
  return 'bg-keYellow/10 hover:bg-keYellow/20 active:bg-keYellow/30 border border-keYellow/30 hover:border-keYellow/50 text-keYellow hover:shadow-[0_0_12px_rgba(250,204,21,0.2)]'
})

const startFleeing = (missingIngredients) => {
  isFleeing.value = true
  fleeTimer = setTimeout(() => {
    isFleeing.value = false
    isAlarmLocked.value = true
    buttonTranslateX.value = 0
    buttonTranslateY.value = 0
  }, 8000)
}

const handleButtonHover = (e) => {
  if (!isFleeing.value || !buttonRef.value || !containerRef.value || !buttonWrapperRef.value) return
  const containerRect = containerRef.value.getBoundingClientRect()
  const wrapperRect = buttonWrapperRef.value.getBoundingClientRect()
  const btnRect = buttonRef.value.getBoundingClientRect()

  // Original static absolute position without current translations
  // Using wrapperRect prevents drift caused by measuring animating CSS transforms
  const origRight = wrapperRect.right
  const origLeft = origRight - btnRect.width
  const origTop = wrapperRect.top
  const origBottom = wrapperRect.bottom

  // Vector direction (away from cursor) + noise to prevent trapping
  const btnCenterX = btnRect.left + btnRect.width / 2
  const btnCenterY = btnRect.top + btnRect.height / 2
  let dx = btnCenterX - e.clientX + (Math.random() - 0.5) * 30
  let dy = btnCenterY - e.clientY + (Math.random() - 0.5) * 30

  const dist = Math.sqrt(dx * dx + dy * dy) || 1
  const fleeStep = 150 // Faster, longer jumps
  let newX = buttonTranslateX.value + (dx / dist) * fleeStep
  let newY = buttonTranslateY.value + (dy / dist) * fleeStep

  // Strict boundaries based on container layout (15px padding from edges)
  const minX = containerRect.left - origLeft + 15
  const maxX = containerRect.right - origRight - 15
  const maxY = containerRect.bottom - origBottom - 15
  const minY = Math.min(maxY, (containerRect.top + containerRect.height / 2) - origTop) // limit to bottom half

  buttonTranslateX.value = Math.max(minX, Math.min(newX, maxX))
  buttonTranslateY.value = Math.max(minY, Math.min(newY, maxY))
}

const handleCook = () => {
  if (cookLoading.value || cookDone.value || !ingredients.value.length) return
  if (isAlarmLocked.value) {
    isShaking.value = false
    setTimeout(() => { isShaking.value = true }, 50)
    return
  }
  if (isFleeing.value) return 
  cookLoading.value = true
  cookResult.value = null
  emit('cook', ingredients.value)
}

const onCookResult = (result) => {
  cookLoading.value = false
  const notFound = result.missing || result.not_found || []
  cookResult.value = {
    type: result.status === 'error' ? 'error' : (notFound.length === ingredients.value.length ? 'warn' : 'success'),
    deducted: result.deducted || [],
    notFound: notFound
  }
  if (result.status === 'error' || notFound.length > 0) startFleeing(notFound)
  else cookDone.value = result.deducted?.length > 0
}

onUnmounted(() => { if (fleeTimer) clearTimeout(fleeTimer) })
defineExpose({ onCookResult })
</script>

<style scoped>
.cook-result-enter-active, .cook-result-leave-active { transition: all 0.3s ease; }
.cook-result-enter-from, .cook-result-leave-to { opacity: 0; transform: translateY(-4px); }
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px) rotate(-2deg); }
  75% { transform: translateX(5px) rotate(2deg); }
}
.animate-shake { animation: shake 0.3s ease-in-out; }
.audit-enter-active, .audit-leave-active { transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1); }
.audit-enter-from, .audit-leave-to { opacity: 0; transform: scale(0.95) translateY(-10px); }
</style>
