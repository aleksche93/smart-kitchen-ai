<template>
  <div class="space-y-4">
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
        </div>
      </Transition>

      <button
        @click="handleCook"
        :disabled="cookLoading || cookDone"
        class="w-full py-2.5 px-4 rounded-xl text-sm font-bold transition-all duration-200 flex items-center justify-center gap-2"
        :class="cookDone
          ? 'bg-emerald-900/30 border border-emerald-700/40 text-emerald-400 cursor-default'
          : cookLoading
            ? 'bg-slate-800/60 border border-slate-600/40 text-slate-400 cursor-wait'
            : 'bg-neoYellow/10 hover:bg-neoYellow/20 active:bg-neoYellow/30 border border-neoYellow/30 hover:border-neoYellow/50 text-neoYellow hover:shadow-[0_0_12px_rgba(250,204,21,0.2)] hover:-translate-y-0.5'"
      >
        <span v-if="cookLoading" class="animate-spin text-base">⏳</span>
        <span v-else-if="cookDone">🍽️ Приготовлено!</span>
        <span v-else>🍳 Cook It! — Відрахувати інгредієнти</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  data: { type: Object, required: true }
})

const emit = defineEmits(['cook'])

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

const handleCook = () => {
  if (cookLoading.value || cookDone.value || !ingredients.value.length) return
  cookLoading.value = true
  cookResult.value = null
  emit('cook', ingredients.value)
}

// Parent calls this via defineExpose after API completes
const onCookResult = (result) => {
  cookLoading.value = false
  cookResult.value = {
    type: result.not_found?.length === ingredients.value.length ? 'warn' : 'success',
    deducted: result.deducted || [],
    notFound: result.not_found || []
  }
  cookDone.value = result.deducted?.length > 0
}

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
</style>
