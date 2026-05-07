import { reactive } from 'vue'
import { useChefStore } from '../stores/chefStore'

// Centralized state shared across components
export const chefState = reactive({
  emotionDisplay: 'IDLE', // fallback
  chatMessage: '',
  recipeText: '',
  toolCommands: [],
  selectedIngredient: null,
  showMagicTrigger: false
})

export function useChefFSM() {
  const updateState = (apiResponse) => {
    if (apiResponse && apiResponse.chef_response) {
      const chefResp = apiResponse.chef_response
      chefState.emotionDisplay = chefResp.emotion_displayed || 'IDLE'
      chefState.chatMessage = chefResp.chat_message || ''
      chefState.recipeText = chefResp.technical_data?.recipe_options || ''
      chefState.toolCommands = chefResp.technical_data?.tool_commands || []
      chefState.showMagicTrigger = false
      
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
    chefState.chatMessage = ''
    chefState.recipeText = ''
    chefState.toolCommands = []
    chefState.selectedIngredient = null
    chefState.showMagicTrigger = false
    document.documentElement.classList.remove('danger-zone')
    
    const chefStore = useChefStore()
    chefStore.reset()
  }

  const fetchChefState = async () => {
    try {
      const resp = await fetch('http://localhost:8000/api/v1/chef/state')
      if (resp.ok) {
        const data = await resp.json()
        if (data.status === 'success') {
          chefState.emotionDisplay = data.current_state || 'IDLE'
          const chefStore = useChefStore()
          chefStore.setEmotion(chefState.emotionDisplay)
          
          if (chefState.emotionDisplay.toUpperCase() === 'ANGRY' || chefState.emotionDisplay.toUpperCase() === 'CHAOTIC') {
            document.documentElement.classList.add('danger-zone')
          }
        }
      }
    } catch (e) {
      console.warn("Failed to fetch Chef FSM state", e)
    }
  }

  return { chefState, updateState, resetState, fetchChefState }
}
