import fs from 'fs';
import path from 'path';
import { spawnSync } from 'child_process';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const targetFile = path.resolve(__dirname, '../src/composables/useChefFSM.js');
const targetContent = fs.readFileSync(targetFile, 'utf8');

// Замінюємо Vue на локальний стаб
let mockedContent = targetContent.replace(/from\s+['"]vue['"]/g, "from '../libs/vue.js'");

// ВИПРАВЛЕННЯ: Мокаємо Pinia Store, щоб Node.js не падав при викликах chefStore.setEmotion()
mockedContent = mockedContent.replace(
  /import\s+\{\s*useChefStore\s*}\s+from\s+['"][^'"]+['"]/g,
  "const useChefStore = () => ({ setEmotion: () => {}, logThought: () => {}, reset: () => {} });"
);

const tmpFile = path.resolve(__dirname, 'useChefFSM.tmp.js');
fs.writeFileSync(tmpFile, mockedContent);

console.log("Running Zero-Build Vanilla Tests...");
const testScript = path.resolve(__dirname, 'useChefFSM.test.js');
const result = spawnSync('node', [testScript], { stdio: 'inherit' });

fs.unlinkSync(tmpFile);
process.exit(result.status);
