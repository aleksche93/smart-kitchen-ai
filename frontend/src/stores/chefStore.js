import { defineStore } from 'pinia'

export const useChefStore = defineStore('chef', {
  state: () => ({
    emotionDisplay: 'IDLE',
    thoughts: [],
    maxThoughts: 5
  }),
  actions: {
    setEmotion(emotion) {
      this.emotionDisplay = emotion || 'IDLE'
      this.logThought(`[FSM_TRANSITION] Emotion Shift -> ${this.emotionDisplay}`)
    },
    logThought(text) {
      this.thoughts.push({ id: Date.now() + Math.random(), text })
      if (this.thoughts.length > this.maxThoughts) {
        this.thoughts.shift()
      }
    },
    reset() {
      this.emotionDisplay = 'IDLE'
      this.thoughts = []
      this.logThought("System Reboot. Chef Memory Reset. [CLEAN]")
    }
  }
})
