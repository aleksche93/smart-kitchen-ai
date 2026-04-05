<template>
  <Card title="Chef's Advice" class="h-[60%] mb-4">
    <div v-if="chefState.adviceText || chefState.recipeText" class="space-y-4">
      <div v-if="chefState.adviceText" class="bg-slate-800/80 p-6 rounded-xl border border-slate-700/50">
        <h4 class="text-xs uppercase tracking-widest text-neoWheat mb-2 border-b border-slate-700 pb-1">Contextual Advice</h4>
        <p class="text-slate-300 leading-relaxed font-sans text-sm">{{ chefState.adviceText }}</p>
      </div>

      <div v-if="chefState.recipeText" class="bg-slate-900/80 p-6 rounded-xl border-l-4 border-neoWheat shadow-lg flex flex-col">
        <h4 class="text-xs uppercase tracking-widest text-neoWheat mb-2 pb-1">Generated Recipe</h4>
        <!-- JSON Structured Rendering -->
        <div v-if="parsedRecipe" class="prose prose-invert prose-sm max-w-none text-slate-300 mb-6">
          <h2 class="text-neoWheat border-b border-slate-700/50 pb-2 mb-4">{{ parsedRecipe.name || parsedRecipe.title || 'Custom Recipe' }}</h2>
          
          <template v-if="parsedRecipe.ingredients && parsedRecipe.ingredients.length">
            <h3 class="text-slate-400 uppercase tracking-widest text-xs mt-4 mb-2">Ingredients</h3>
            <ul class="my-2">
              <li v-for="(ing, i) in parsedRecipe.ingredients" :key="'ing'+i" class="my-1">{{ ing }}</li>
            </ul>
          </template>

          <template v-if="parsedRecipe.instructions && parsedRecipe.instructions.length">
            <h3 class="text-slate-400 uppercase tracking-widest text-xs mt-6 mb-2">Instructions</h3>
            <ol class="my-2">
              <li v-for="(inst, i) in parsedRecipe.instructions" :key="'inst'+i" class="my-1 text-slate-300">{{ inst }}</li>
            </ol>
          </template>
          
          <!-- Edge case: some LLMs return text inside a notes string -->
          <p v-if="parsedRecipe.notes" class="mt-4 italic text-slate-400">{{ parsedRecipe.notes }}</p>
        </div>
        
        <!-- Markdown Fallback -->
        <div v-else class="prose prose-invert prose-sm max-w-none text-slate-300 markdown-body mb-6" v-html="formatMarkdown(chefState.recipeText)"></div>
        
        <!-- B2C Action Stubs -->
        <!-- B2C Action Stubs -->
        <div class="mt-auto border-t border-slate-700/50 pt-4 flex flex-col relative">
          <!-- Toast Notification -->
          <Transition name="toast">
            <div v-if="activeToast" class="absolute -top-12 left-1/2 transform -translate-x-1/2 bg-green-600/90 backdrop-blur text-white px-4 py-1.5 rounded-full shadow-[0_0_15px_rgba(22,163,74,0.5)] text-xs font-bold pointer-events-none z-10 whitespace-nowrap flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
              {{ activeToast }}
            </div>
          </Transition>

          <div class="flex flex-wrap gap-2">
            <button @click="simulateAction('Recipe Saved')" class="flex-1 min-w-[120px] bg-slate-800 hover:bg-slate-700 active:bg-slate-600 border border-slate-600 text-slate-300 hover:text-neoWheat font-semibold py-2 px-3 rounded-lg text-xs transition-all transform hover:-translate-y-0.5 shadow-sm">
              💾 Save Recipe
            </button>
            <button @click="simulateAction('Added to Cart')" class="flex-1 min-w-[120px] bg-slate-800 hover:bg-slate-700 active:bg-slate-600 border border-slate-600 text-slate-300 hover:text-neoWheat font-semibold py-2 px-3 rounded-lg text-xs transition-all transform hover:-translate-y-0.5 shadow-sm">
              🛒 Add to Cart
            </button>
            <button @click="simulateAction('Oven Preheating...')" class="flex-1 min-w-[120px] bg-neoWheat/10 hover:bg-neoTerracotta/20 active:bg-neoTerracotta/30 border border-neoWheat/30 hover:border-neoTerracotta/50 text-neoWheat hover:text-neoTerracotta font-semibold py-2 px-3 rounded-lg text-xs transition-all transform hover:-translate-y-0.5 shadow-sm">
              🔥 Send to Smart Oven
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="h-full flex flex-col items-center justify-center text-slate-500 opacity-50 space-y-3">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
      <p>Awaiting operations...</p>
    </div>
  </Card>
</template>

<script setup>
import { computed, ref } from 'vue'
import Card from '../ui/Card.vue'
import { chefState } from '../../composables/useChefFSM'

const activeToast = ref(null)
let toastTimeout = null

const simulateAction = (msg) => {
  activeToast.value = msg
  if (toastTimeout) clearTimeout(toastTimeout)
  toastTimeout = setTimeout(() => { activeToast.value = null }, 2500)
}

const parsedRecipe = computed(() => {
  if (!chefState.recipeText) return null
  try {
    const data = JSON.parse(chefState.recipeText)
    return data
  } catch (e) {
    return null
  }
})

const formatMarkdown = (text) => {
  if (!text) return ''
  return text
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^\* (.*$)/gim, '<li>$1</li>')
    .replace(/<\/li>\n<li>/gim, '</li><li>') // clean up list newlines
    .replace(/\n/g, '<br/>') // simplistic line breakes for the rest
    .replace(/(<li>.*?<\/li>)/gim, '<ul>$1</ul>')
    .replace(/<\/ul><br\/><ul>/gim, '') // merge adjoining lists
}
</script>

<style>
.markdown-body strong {
  @apply text-slate-100 font-semibold;
}

.toast-enter-active, .toast-leave-active { 
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
}
.toast-enter-from { 
  opacity: 0; transform: translate(-50%, 10px) scale(0.9); 
}
.toast-leave-to { 
  opacity: 0; transform: translate(-50%, -10px) scale(0.9); 
}
</style>
