/**
 * generate-build-meta.mjs
 * ビルド時に public/build-meta.json を生成し、
 * フロントエンドのキャッシュバスターに使用するタイムスタンプを提供する。
 */
import { writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const now = new Date();
const meta = {
  v: String(now.getTime()),
  builtAt: now.toISOString(),
};

const outPath = resolve(__dirname, '..', 'public', 'build-meta.json');
writeFileSync(outPath, JSON.stringify(meta, null, 2) + '\n', 'utf-8');
console.log(`[build-meta] generated ${outPath}  v=${meta.v}  builtAt=${meta.builtAt}`);
