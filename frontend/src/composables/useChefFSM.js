import { reactive } from 'vue'
import { useChefStore } from '../stores/chefStore'

// Centralized state shared across components
export const chefState = reactive({
  emotionDisplay: 'IDLE', // fallback
  adviceText: '',
  recipeText: '',
  toolCommands: [],
  selectedIngredient: null
})

export function useChefFSM() {
  const updateState = (apiResponse) => {
    if (apiResponse && apiResponse.chef_response) {
      const chefResp = apiResponse.chef_response
      chefState.emotionDisplay = chefResp.emotion_displayed || 'IDLE'
      chefState.adviceText = chefResp.advice_text || ''
      chefState.recipeText = chefResp.recipe_options || chefResp.recipe || ''
      chefState.toolCommands = chefResp.tool_commands || []
      
      const chefStore = useChefStore()
      chefStore.setEmotion(chefState.emotionDisplay)
      
      // Flash danger state dynamically if angry
      if (chefState.emotionDisplay.toUpperCase() === 'ANGRY' || chefState.emotionDisplay.toUpperCase() === 'CHAOTIC') {
        document.documentElement.classList.add('danger-zone')
        chefStore.logThought("WARNING: Emotional threshold exceeded. Danger zone active.")
      } else {
        document.documentElement.classList.remove('danger-zone')
      }
    }
  }

  const resetState = () => {
    chefState.emotionDisplay = 'IDLE'
    chefState.adviceText = ''
    chefState.recipeText = ''
    chefState.toolCommands = []
    chefState.selectedIngredient = null
    document.documentElement.classList.remove('danger-zone')
    
    const chefStore = useChefStore()
    chefStore.reset()
  }

  return { chefState, updateState, resetState }
}
