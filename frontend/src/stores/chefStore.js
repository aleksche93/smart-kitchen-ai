import { defineStore } from 'pinia'

export const useChefStore = defineStore('chef', {
  state: () => ({
    emotionDisplay: 'IDLE',
    thoughts: [],
    maxThoughts: 5,
    _idleInterval: null
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
    },
    startSarcasticEngine() {
      if (this._idleInterval) clearInterval(this._idleInterval)
      this._idleInterval = setInterval(() => {
        if (this.emotionDisplay === 'IDLE') {
          const idleThoughts = [
            'Polishing the virtual knives...',
            'Humming a ke-Ukrainian tune...',
            'Judging your fridge inventory...',
            'Waiting for a culinary challenge...',
            'Staring at a digital potato...'
          ]
          const randomThought = idleThoughts[Math.floor(Math.random() * idleThoughts.length)]
          this.logThought(`[IDLE_PROCESS] ${randomThought}`)
        }
      }, 12000)
    },
    stopSarcasticEngine() {
      if (this._idleInterval) {
        clearInterval(this._idleInterval)
        this._idleInterval = null
      }
    }
  }
})
