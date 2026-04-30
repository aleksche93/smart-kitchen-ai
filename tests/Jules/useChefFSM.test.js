import { test, expect } from './run.js';
import { useChefFSM, chefState } from '../src/composables/useChefFSM.js';

const { updateState } = useChefFSM();

test('updateState handles null apiResponse without changing state', () => {
  const initialState = { ...chefState };
  updateState(null);
  expect(chefState.emotionDisplay).toBe(initialState.emotionDisplay);
  expect(chefState.adviceText).toBe(initialState.adviceText);
});

test('updateState handles undefined apiResponse without changing state', () => {
  const initialState = { ...chefState };
  updateState(undefined);
  expect(chefState.emotionDisplay).toBe(initialState.emotionDisplay);
  expect(chefState.adviceText).toBe(initialState.adviceText);
});

test('updateState handles empty object without changing state', () => {
  const initialState = { ...chefState };
  updateState({});
  expect(chefState.emotionDisplay).toBe(initialState.emotionDisplay);
});

test('updateState handles missing chef_response without changing state', () => {
  const initialState = { ...chefState };
  updateState({ some_other_key: {} });
  expect(chefState.emotionDisplay).toBe(initialState.emotionDisplay);
});

test('updateState use fallbacks for missing chef_response fields', () => {
  updateState({ chef_response: {} });
  expect(chefState.emotionDisplay).toBe('IDLE');
  expect(chefState.adviceText).toBe('');
  expect(chefState.recipeText).toBe('');
  expect(chefState.toolCommands).toEqual([]);
});

test('updateState toggles danger-zone class for ANGRY emotion (case-insensitive)', () => {
  // Test with lowercase 'angry' to verify .toUpperCase() logic in code
  updateState({ chef_response: { emotion_displayed: 'angry' } });
  expect(global.document.documentElement.classList).toContain('danger-zone');
  
  updateState({ chef_response: { emotion_displayed: 'IDLE' } });
  expect(global.document.documentElement.classList).notToContain('danger-zone');
});

test('updateState toggles danger-zone class for CHAOTIC emotion (case-insensitive)', () => {
  // Test with 'Chaotic' to verify .toUpperCase() logic in code
  updateState({ chef_response: { emotion_displayed: 'Chaotic' } });
  expect(global.document.documentElement.classList).toContain('danger-zone');
});

test('updateState prioritizes recipe_options over recipe', () => {
  updateState({ 
    chef_response: { 
      recipe_options: 'Option A, Option B',
      recipe: 'Standard Recipe'
    } 
  });
  expect(chefState.recipeText).toBe('Option A, Option B');
});

test('updateState uses recipe if recipe_options is missing', () => {
  updateState({ 
    chef_response: { 
      recipe: 'Standard Recipe'
    } 
  });
  expect(chefState.recipeText).toBe('Standard Recipe');
});
