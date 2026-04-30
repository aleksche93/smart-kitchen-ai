// Simple test runner for useChefFSM.js
import { useChefFSM, chefState } from '../src/composables/useChefFSM.js';

// Mock document
global.document = {
  documentElement: {
    classList: {
      add: (cls) => global.document.documentElement.classList._classes.add(cls),
      remove: (cls) => global.document.documentElement.classList._classes.delete(cls),
      contains: (cls) => global.document.documentElement.classList._classes.has(cls),
      _classes: new Set()
    }
  }
};

const tests = [];

export function test(name, fn) {
  tests.push({ name, fn });
}

export function expect(actual) {
  return {
    toBe(expected) {
      if (actual !== expected) {
        throw new Error(`Expected ${expected} but got ${actual}`);
      }
    },
    toEqual(expected) {
      if (JSON.stringify(actual) !== JSON.stringify(expected)) {
        throw new Error(`Expected ${JSON.stringify(expected)} but got ${JSON.stringify(actual)}`);
      }
    },
    toContain(cls) {
        if (!actual.contains(cls)) {
            throw new Error(`Expected classList to contain ${cls}`);
        }
    },
    notToContain(cls) {
        if (actual.contains(cls)) {
            throw new Error(`Expected classList NOT to contain ${cls}`);
        }
    }
  };
}

async function run() {
  await import('./useChefFSM.test.js');

  let passed = 0;
  let failed = 0;

  console.log('Running frontend tests...');
  for (const { name, fn } of tests) {
    try {
      const { resetState } = useChefFSM();
      resetState();
      
      await fn();
      console.log(`✅ ${name}`);
      passed++;
    } catch (err) {
      console.error(`❌ ${name}`);
      console.error(err.stack);
      failed++;
    }
  }

  console.log(`\nTests: ${passed} passed, ${failed} failed, ${tests.length} total`);
  process.exit(failed > 0 ? 1 : 0);
}

run();
