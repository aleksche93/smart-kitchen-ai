import assert from 'assert';
import { useChefFSM, chefState } from './useChefFSM.tmp.js';

// Mock Browser DOM locally for Node environment
global.document = {
  documentElement: {
    classList: {
      _classes: new Set(),
      add(c) { this._classes.add(c); },
      remove(c) { this._classes.delete(c); },
      contains(c) { return this._classes.has(c); }
    }
  }
};

async function runTests() {
   console.log("Testing useChefFSM Transitions...");
   const { updateState, resetState } = useChefFSM();
   
   // Test Reset Logic
   resetState();
   assert.strictEqual(chefState.emotionDisplay, 'IDLE', "Reset should default emotion to IDLE");
   assert.strictEqual(global.document.documentElement.classList.contains('danger-zone'), false, "Danger zone must be disabled on reset");
   console.log(" - ✅ State Reset Passed");
   
   // Test Update ANGRY Logic (Validation)
   updateState({
       chef_response: {
           emotion_displayed: 'ANGRY',
           chat_message: 'Stop adding ketchup to pasta!', // Використовуємо правильний ключ
           technical_data: { recipe_options: [] }
       }
   });
   
   assert.strictEqual(chefState.emotionDisplay, 'ANGRY', "Emotion must map dynamically");
   assert.strictEqual(chefState.chatMessage, 'Stop adding ketchup to pasta!', "Chat message mapped correctly"); // Перевіряємо chatMessage
   assert.strictEqual(global.document.documentElement.classList.contains('danger-zone'), true, "App must shift to danger-zone upon ANGRY");
   console.log(" - ✅ Stateful transition into ANGRY passed");

   // Test Revert IDLE
   updateState({
    chef_response: {
        emotion_displayed: 'IDLE',
        chat_message: 'That is acceptable.',
        technical_data: { recipe_options: [] }
    }
   });
   assert.strictEqual(global.document.documentElement.classList.contains('danger-zone'), false, "Must relax danger-zone");
   console.log(" - ✅ Stateful rollback into IDLE passed");
   
   console.log("ALL TESTS PASSED ✨");
}

runTests().catch(err => {
    console.error("Test execution failed!", err);
    process.exit(1);
});
