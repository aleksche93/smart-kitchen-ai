<template>
  <Card title="Chef's Advice" class="h-[60%] mb-4 flex flex-col overflow-hidden">
    <div v-if="chefState.adviceText || chefState.recipeText" class="flex-1 flex flex-col min-h-0 space-y-4">
      <div v-if="chefState.adviceText" class="bg-slate-800/80 p-4 rounded-xl border border-slate-700/50 shrink-0">
        <h4 class="text-xs uppercase tracking-widest text-neoWheat mb-2 border-b border-slate-700 pb-1">Contextual Advice</h4>
        <p class="text-slate-300 leading-relaxed font-sans text-sm">{{ chefState.adviceText }}</p>
      </div>

      <div v-if="chefState.recipeText" class="bg-slate-900/80 p-4 rounded-xl border-l-4 border-neoWheat shadow-lg flex flex-col min-h-0 flex-1">
        <h4 class="text-xs uppercase tracking-widest text-neoWheat mb-3 pb-1 shrink-0">Recipe Options</h4>
        
        <!-- Multi-Option Structured Rendering -->
        <div v-if="parsedRecipes.length > 0" class="flex-1 flex flex-col min-h-0">
          
          <!-- Interactive Recipe Cards -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-4 shrink-0 min-w-0">
            <button 
              v-for="(recipe, idx) in parsedRecipes" 
              :key="'card'+idx"
              @click="selectedRecipeIndex = idx"
              :class="['text-left px-3 py-2 rounded-lg border transition-all cursor-pointer select-none overflow-hidden flex flex-col', 
                       selectedRecipeIndex === idx ? 'bg-slate-800/80 border-neoWheat shadow-[0_0_15px_rgba(253,224,71,0.15)]' : 'bg-transparent border-slate-700 hover:bg-slate-800/50']"
            >
              <div class="flex w-full items-start justify-between min-w-0 gap-2 mb-1">
                <div class="flex gap-1.5 text-[10px] uppercase tracking-wider opacity-80 font-bold text-slate-400 min-w-0 overflow-hidden items-center">
                  <span class="truncate block" v-if="recipe.time">⏱ {{ recipe.time }}</span>
                  <span class="shrink-0 block" v-if="recipe.time && recipe.difficulty">•</span>
                  <span class="truncate block" v-if="recipe.difficulty">📊 {{ recipe.difficulty }}</span>
                </div>
                <!-- Dynamic Icons with Micro-Animation -->
                <span class="text-sm shrink-0 drop-shadow-md" :class="{'animate-pulse scale-110 transition-transform': selectedRecipeIndex === idx, 'opacity-50 grayscale': selectedRecipeIndex !== idx}">
                  {{ idx === 0 ? '⚡' : (idx === 1 ? '🥘' : '🎨') }}
                </span>
              </div>
              <div class="font-bold text-sm w-full leading-tight line-clamp-2 hyphens-auto break-words" :class="selectedRecipeIndex === idx ? 'text-neoWheat' : 'text-slate-400'">{{ recipe.name || 'Recipe Option' }}</div>
            </button>
          </div>

          <!-- Accordion View - Active Recipe -->
          <div :key="'accordion_view_' + selectedRecipeIndex" class="flex-1 overflow-y-auto pr-2 custom-scrollbar flex flex-col gap-3">
            
            <!-- Ingredients Accordion (Open by default) -->
            <details v-if="activeRecipe.ingredients && activeRecipe.ingredients.length" open class="group bg-slate-800 rounded-lg border border-slate-700 overflow-hidden transition-all duration-300">
              <summary class="flex items-center justify-between px-4 py-3 cursor-pointer select-none list-none [&::-webkit-details-marker]:hidden focus:outline-none hover:bg-slate-700/50 transition-colors">
                <h3 class="text-slate-300 uppercase tracking-widest text-xs font-bold">Ingredients</h3>
                <svg class="w-4 h-4 text-slate-400 group-open:rotate-180 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </summary>
              <div class="px-4 pb-4 pt-1 bg-slate-800/50">
                <ul class="space-y-1 list-disc list-inside text-sm text-slate-300">
                  <li v-for="(ing, i) in activeRecipe.ingredients" :key="'ing'+i" class="pl-1">{{ ing }}</li>
                </ul>
              </div>
            </details>

            <!-- Instructions Accordion (Closed by default) -->
            <details v-if="activeRecipe.instructions && activeRecipe.instructions.length" class="group bg-slate-800 rounded-lg border border-slate-700 overflow-hidden transition-all duration-300">
              <summary class="flex items-center justify-between px-4 py-3 cursor-pointer select-none list-none [&::-webkit-details-marker]:hidden focus:outline-none hover:bg-slate-700/50 transition-colors">
                <h3 class="text-slate-300 uppercase tracking-widest text-xs font-bold">Instructions</h3>
                <svg class="w-4 h-4 text-slate-400 group-open:rotate-180 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </summary>
              <div class="px-4 pb-4 pt-1 bg-slate-800/50">
                <ol class="space-y-2 list-decimal list-inside text-sm text-slate-300">
                  <li v-for="(inst, i) in activeRecipe.instructions" :key="'inst'+i" class="pl-1 leading-relaxed">{{ inst }}</li>
                </ol>
              </div>
            </details>
            
            <!-- Notes -->
            <div v-if="activeRecipe.notes" class="px-4 py-3 bg-slate-800/30 rounded-lg border border-slate-700/50">
              <p class="italic text-xs text-slate-400">{{ activeRecipe.notes }}</p>
            </div>

          </div>
        </div>
        
        <!-- Markdown Fallback (Legacy) -->
        <div v-else class="flex-1 overflow-y-auto pr-2 custom-scrollbar prose prose-invert prose-sm max-w-none text-slate-300 markdown-body mb-2" v-html="formatMarkdown(chefState.recipeText)"></div>
        
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

const selectedRecipeIndex = ref(0)

const parsedRecipes = computed(() => {
  if (!chefState.recipeText) return []
  let data
  if (typeof chefState.recipeText === 'object') {
    data = chefState.recipeText
  } else {
    try {
      data = JSON.parse(chefState.recipeText)
    } catch (e) {
      return []
    }
  }
  // Safe extraction map for array payload or legacy objects
  if (Array.isArray(data)) return data
  return data.recipe_options || (data.recipe ? [data.recipe] : [data])
})

const activeRecipe = computed(() => {
  return parsedRecipes.value[selectedRecipeIndex.value] || {}
})

const formatMarkdown = (text) => {
  if (!text || typeof text !== 'string') return ''
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
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
.hide-scrollbar {
  -ms-overflow-style: none; 
  scrollbar-width: none;  
}
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #334155; 
  border-radius: 4px;
}
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
