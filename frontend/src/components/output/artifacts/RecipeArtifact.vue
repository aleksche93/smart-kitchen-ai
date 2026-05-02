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
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Object, required: true }
})

const recipe = computed(() => props.data || {})
const ingredients = computed(() => {
  const raw = recipe.value.ingredients
  return Array.isArray(raw) ? raw : []
})
const instructions = computed(() => {
  const raw = recipe.value.instructions
  return Array.isArray(raw) ? raw : []
})
</script>
