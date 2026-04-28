import { ref } from 'vue'

export function useTypewriter() {
  const displayText = ref('')
  let isTyping = false
  let currentToken = Symbol()

  const sleep = (ms) => new Promise(r => setTimeout(r, ms))

  const type = async (text, options = {}) => {
    isTyping = true
    const {
      minDelay = 30,
      maxDelay = 120,
      mistakeProbability = 0.05
    } = options

    const myToken = Symbol()
    currentToken = myToken
    
    displayText.value = ''
    
    const words = text.split(' ')
    
    for (let i = 0; i < words.length; i++) {
      if (currentToken !== myToken) return // Aborted

      const word = words[i]
      const isMistake = Math.random() < mistakeProbability

      if (isMistake && word.length > 3) {
        // Type a mistake
        const mistakeLen = Math.floor(Math.random() * 2) + 2 // 2-3 chars
        const gibberish = "xqzvw".charAt(Math.floor(Math.random() * 5))
        
        for (let j = 0; j < mistakeLen; j++) {
          if (currentToken !== myToken) return
          displayText.value += gibberish
          await sleep(Math.random() * (maxDelay - minDelay) + minDelay)
        }
        
        // Pause and realize mistake
        await sleep(300 + Math.random() * 200)
        
        // Backspace
        for (let j = 0; j < mistakeLen; j++) {
          if (currentToken !== myToken) return
          displayText.value = displayText.value.slice(0, -1)
          await sleep(50 + Math.random() * 50)
        }
        
        // Slight pause before typing correct word
        await sleep(150 + Math.random() * 100)
      }

      // Type correct word
      for (let j = 0; j < word.length; j++) {
        if (currentToken !== myToken) return
        displayText.value += word[j]
        await sleep(Math.random() * (maxDelay - minDelay) + minDelay)
      }
      
      // Add space if not last word
      if (i < words.length - 1) {
        if (currentToken !== myToken) return
        displayText.value += ' '
        await sleep(Math.random() * (maxDelay - minDelay) + minDelay)
      }
    }
    
    isTyping = false
  }

  const abort = () => {
    currentToken = Symbol()
    isTyping = false
  }

  return {
    displayText,
    isTyping,
    type,
    abort
  }
}
