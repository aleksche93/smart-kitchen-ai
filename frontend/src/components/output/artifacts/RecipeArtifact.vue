<template>
  <div ref="containerRef" class="space-y-4 relative">
    <!-- Recipe Title & Meta -->
    <div class="flex items-center justify-between">
      <h4 class="text-lg font-bold text-neoYellow">{{ recipe.name || 'Untitled Recipe' }}</h4>
      <div class="flex gap-2 text-[10px] uppercase tracking-wider text-slate-400">
        <span v-if="recipe.time || recipe.estimated_duration">⏱ {{ recipe.time || recipe.estimated_duration }}</span>
        <span v-if="recipe.difficulty || recipe.recipe_complexity">📊 {{ recipe.difficulty || recipe.recipe_complexity }}</span>
      </div>
    </div>

    <!-- Ingredients -->
    <div v-if="ingredients.length" class="space-y-2">
      <h5 class="text-xs uppercase tracking-widest text-slate-400 font-bold">Інгредієнти</h5>
      <div class="grid grid-cols-2 gap-1.5">
        <div v-for="(ing, i) in ingredients" :key="i"
             class="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-slate-800/60 border border-slate-700/40 text-sm text-slate-300">
          <span class="text-xs opacity-60">•</span>
          <span>{{ ing }}</span>
        </div>
      </div>
    </div>

    <!-- Instructions -->
    <div v-if="instructions.length" class="space-y-2">
      <h5 class="text-xs uppercase tracking-widest text-slate-400 font-bold">Кроки приготування</h5>
      <ol class="space-y-1.5 list-decimal list-inside text-sm text-slate-300">
        <li v-for="(step, i) in instructions" :key="i" class="leading-relaxed pl-1">{{ step }}</li>
      </ol>
    </div>

    <!-- Notes -->
    <p v-if="recipe.notes" class="text-xs italic text-slate-500 border-t border-slate-700/30 pt-2">{{ recipe.notes }}</p>

    <!-- Cook It! Button -->
    <div class="border-t border-slate-700/40 pt-3 mt-2">
      <!-- Post-cook feedback -->
      <Transition name="cook-result">
        <div v-if="cookResult" class="mb-2 px-3 py-2 rounded-lg text-xs space-y-0.5"
             :class="cookResult.type === 'success' ? 'bg-emerald-900/30 border border-emerald-700/40 text-emerald-300' : 'bg-amber-900/30 border border-amber-700/40 text-amber-300'">
          <p v-if="cookResult.deducted?.length" class="font-semibold">✅ Відраховано: {{ cookResult.deducted.join(', ') }}</p>
          <p v-if="cookResult.notFound?.length" class="opacity-70">⚠️ Не знайдено в холодильнику: {{ cookResult.notFound.join(', ') }}</p>
          <p v-if="cookResult.trollMessage" class="font-bold text-red-400 mt-1">{{ cookResult.trollMessage }}</p>
        </div>
      </Transition>

      <button
        ref="buttonRef"
        @click="handleCook"
        @mouseover="handleButtonHover"
        :disabled="cookLoading || cookDone"
        class="w-full py-2.5 px-4 rounded-xl text-sm font-bold flex items-center justify-center gap-2 transition-colors"
        :style="buttonStyle"
        :class="buttonClasses"
      >
        <span v-if="cookLoading" class="animate-spin text-base">⏳</span>
        <span v-else-if="cookDone">🍽️ Приготовлено!</span>
        <span v-else>🍳 Cook It! — Відрахувати інгредієнти</span>
      </button>
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

// Fleeing Button State
const isFleeing = ref(false)
const isAlarmLocked = ref(false)
const isShaking = ref(false)
const buttonTranslateX = ref(0)
const buttonTranslateY = ref(0)
const containerRef = ref(null)
const buttonRef = ref(null)
let fleeTimer = null

const buttonStyle = computed(() => {
  if (isFleeing.value) {
    return {
      transform: `translate(${buttonTranslateX.value}px, ${buttonTranslateY.value}px)`,
      transition: 'transform 0.15s ease-out'
    }
  }
  return {
    transform: 'translate(0px, 0px)',
    transition: 'transform 0.3s ease-out'
  }
})

const buttonClasses = computed(() => {
  if (cookDone.value) return 'bg-emerald-900/30 border border-emerald-700/40 text-emerald-400 cursor-default'
  if (cookLoading.value) return 'bg-slate-800/60 border border-slate-600/40 text-slate-400 cursor-wait'
  if (isAlarmLocked.value) {
    return `bg-slate-800/60 border border-red-500/50 text-red-400 cursor-not-allowed ${isShaking.value ? 'animate-shake' : ''}`
  }
  return 'bg-neoYellow/10 hover:bg-neoYellow/20 active:bg-neoYellow/30 border border-neoYellow/30 hover:border-neoYellow/50 text-neoYellow hover:shadow-[0_0_12px_rgba(250,204,21,0.2)] hover:-translate-y-0.5'
})

const startFleeing = (missingIngredients) => {
  isFleeing.value = true
  fleeTimer = setTimeout(() => {
    isFleeing.value = false
    isAlarmLocked.value = true
    buttonTranslateX.value = 0
    buttonTranslateY.value = 0
    
    // Display troll message via Toast/Result box
    cookResult.value = {
      ...cookResult.value,
      trollMessage: t('chef.troll.button_fleeing', { missing_ingredients: missingIngredients.join(', ') })
    }
  }, 10000)
}

const handleButtonHover = () => {
  if (!isFleeing.value || !buttonRef.value || !containerRef.value) return
  
  const containerRect = containerRef.value.getBoundingClientRect()
  const btnRect = buttonRef.value.getBoundingClientRect()
  
  // Calculate relative bounds within container
  const maxX = containerRect.width - btnRect.width
  const maxY = containerRect.height - btnRect.height
  
  // Target random position within container
  const targetX = Math.random() * maxX
  const targetY = Math.random() * maxY
  
  // Calculate offset from button's original un-transformed DOM position
  // btnRect includes current transform, so we need original offset
  // buttonRef.value.offsetLeft/offsetTop give position relative to offsetParent
  const originalX = buttonRef.value.offsetLeft
  const originalY = buttonRef.value.offsetTop
  
  buttonTranslateX.value = targetX - originalX
  buttonTranslateY.value = targetY - originalY
}

const handleCook = () => {
  if (cookLoading.value || cookDone.value || !ingredients.value.length) return
  
  if (isAlarmLocked.value) {
    // Trigger shake animation every time user clicks locked button
    isShaking.value = false
    setTimeout(() => { isShaking.value = true }, 50)
    return
  }
  if (isFleeing.value) return // Try catching me!

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
  
  if (result.status === 'error' || notFound.length > 0) {
    startFleeing(notFound)
  } else {
    cookDone.value = result.deducted?.length > 0
  }
}

onUnmounted(() => {
  if (fleeTimer) clearTimeout(fleeTimer)
})

defineExpose({ onCookResult })
</script>

<style scoped>
.cook-result-enter-active, .cook-result-leave-active {
  transition: all 0.3s ease;
}
.cook-result-enter-from, .cook-result-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px) rotate(-2deg); }
  75% { transform: translateX(5px) rotate(2deg); }
}
.animate-shake {
  animation: shake 0.3s ease-in-out;
}
</style>
