#!/usr/bin/env node
/**
 * generate-ogp.mjs
 * ビルド時にJSONデータを読み取り、OGP画像(1200x630)を自動生成する
 * satori + @resvg/resvg-js でPNG化
 *
 * データが更新されるたびに next build 前に実行され、
 * 最新の件数が OGP 画像に反映される
 */
import satori from 'satori';
import { Resvg } from '@resvg/resvg-js';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');

// ── データ件数を読み取り ───────────────────────────
const allData = JSON.parse(readFileSync(join(ROOT, 'public/units.json'), 'utf8'));
const supporters = JSON.parse(readFileSync(join(ROOT, 'public/supporters.json'), 'utf8'));
const optionParts = JSON.parse(readFileSync(join(ROOT, 'public/option_parts.json'), 'utf8'));

// spa.html と同じロジック
const unitCount = allData.filter(u => {
  const tags = u.tags || [];
  if (tags.includes('キャラ')) return false;
  const s = u.normal?.stats;
  return s && (s.hp > 0 || s.attack > 0 || s.defense > 0 || s.en > 0);
}).length;
const charaCount = allData.filter(u => (u.tags || []).includes('キャラ')).length;
const supporterCount = supporters.length;
const itemCount = optionParts.length;

console.log(`[generate-ogp] Units=${unitCount}, Characters=${charaCount}, Supporters=${supporterCount}, Items=${itemCount}`);

// ── フォント読み込み ─────────────────────────────
// Orbitron (英数字・ラベル用)
const orbitronPath = join(ROOT, 'node_modules/@fontsource/orbitron/files/orbitron-latin-700-normal.woff');
const orbitronBold = readFileSync(orbitronPath);

// 日本語フォント: システムフォント or Google Fonts からフェッチ
async function loadJapaneseFont() {
  // 1. DroidSansFallbackFull (Ubuntu/Vercel build環境に存在)
  const droidPath = '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf';
  if (existsSync(droidPath)) {
    console.log('[generate-ogp] Using DroidSansFallbackFull.ttf');
    return readFileSync(droidPath);
  }
  // 2. macOS: ヒラギノ角ゴシック
  const hiraPath = '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc';
  if (existsSync(hiraPath)) {
    console.log('[generate-ogp] Using Hiragino Kaku Gothic W6');
    return readFileSync(hiraPath);
  }
  // 3. Google Fonts からフェッチ (Vercel build等ネットワーク接続時)
  // ※ Variable Font は satori 非対応のため Static 版を使用
  const fontUrls = [
    'https://raw.githubusercontent.com/google/fonts/main/ofl/notosansjp/static/NotoSansJP-Bold.ttf',
    'https://github.com/google/fonts/raw/main/ofl/notosansjp/static/NotoSansJP-Bold.ttf',
  ];
  for (const url of fontUrls) {
    try {
      console.log(`[generate-ogp] Fetching Noto Sans JP from ${new URL(url).hostname}...`);
      const res = await fetch(url, { redirect: 'follow' });
      if (res.ok) {
        const buf = Buffer.from(await res.arrayBuffer());
        if (buf.length > 100000) return buf; // sanity check
      }
    } catch (e) {
      console.warn(`[generate-ogp] Font fetch failed: ${e.message}`);
    }
  }
  throw new Error('No Japanese font available');
}

async function main() {
  const jpFont = await loadJapaneseFont();

  const fonts = [
    { name: 'Orbitron', data: orbitronBold, weight: 700, style: 'normal' },
    { name: 'JP', data: jpFont, weight: 400, style: 'normal' },
  ];

  // ── OGP デザイン ────────────────────────────────
  const features = ['Tier表作成', 'ステータス比較', 'ダメージ計算', 'チーム編成', 'ランキング'];
  const stats = [
    { num: unitCount.toLocaleString(), label: 'UNITS' },
    { num: charaCount.toLocaleString(), label: 'CHARACTERS' },
    { num: supporterCount.toLocaleString(), label: 'SUPPORTERS' },
    { num: itemCount.toLocaleString(), label: 'ITEMS' },
  ];

  const element = {
    type: 'div',
    props: {
      style: {
        width: 1200, height: 630, display: 'flex', flexDirection: 'column',
        fontFamily: 'JP', background: '#060a14', color: '#fff',
        position: 'relative', overflow: 'hidden',
      },
      children: [
        // Top accent bar
        { type: 'div', props: { style: {
          position: 'absolute', top: 0, left: 0, right: 0, height: 4,
          background: 'linear-gradient(90deg, #0066ff 0%, #00aaff 25%, #ffd700 50%, #ff6600 75%, transparent 100%)',
        }}},
        // Bottom accent bar
        { type: 'div', props: { style: {
          position: 'absolute', bottom: 0, left: 0, right: 0, height: 4,
          background: 'linear-gradient(90deg, transparent 0%, #ff6600 25%, #ffd700 50%, #00aaff 75%, #0066ff 100%)',
        }}},
        // Left accent line
        { type: 'div', props: { style: {
          position: 'absolute', top: 4, bottom: 4, left: 0, width: 3,
          background: 'linear-gradient(180deg, #0066ff, #00aaff 30%, transparent 70%)',
        }}},
        // Corner bracket top-left
        { type: 'div', props: { style: {
          position: 'absolute', top: 20, left: 20, width: 40, height: 40,
          borderTop: '2px solid rgba(0,170,255,0.3)', borderLeft: '2px solid rgba(0,170,255,0.3)',
        }}},
        // Corner bracket bottom-right
        { type: 'div', props: { style: {
          position: 'absolute', bottom: 20, right: 20, width: 40, height: 40,
          borderBottom: '2px solid rgba(255,215,0,0.3)', borderRight: '2px solid rgba(255,215,0,0.3)',
        }}},
        // Main content
        { type: 'div', props: {
          style: {
            display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
            height: '100%', padding: '50px 60px',
          },
          children: [
            // ─── Top: Title section ───
            { type: 'div', props: {
              style: { display: 'flex', flexDirection: 'column' },
              children: [
                { type: 'div', props: {
                  style: { fontFamily: 'Orbitron', fontSize: 11, fontWeight: 700, color: '#00aaff', letterSpacing: 4, opacity: 0.7, marginBottom: 8 },
                  children: 'DATABASE',
                }},
                { type: 'div', props: {
                  style: { fontFamily: 'Orbitron', fontSize: 52, fontWeight: 700, color: '#ffffff', letterSpacing: -1, lineHeight: 1.1 },
                  children: 'GGET-DB',
                }},
                { type: 'div', props: {
                  style: { fontFamily: 'JP', fontSize: 18, fontWeight: 400, color: '#6a90b8', marginTop: 6, letterSpacing: 2 },
                  children: 'Gジェネ エターナル 総合データベース',
                }},
                { type: 'div', props: {
                  style: { fontFamily: 'Orbitron', fontSize: 13, color: '#4a6080', marginTop: 4, letterSpacing: 1 },
                  children: 'GUNDAM G-GENERATION ETERNAL \u2014 ALL RARITY UNIT & CHARACTER DATABASE',
                }},
              ],
            }},
            // ─── Middle: Stats bar ───
            { type: 'div', props: {
              style: {
                display: 'flex', justifyContent: 'space-between',
                borderTop: '1px solid rgba(0,102,255,0.2)',
                borderBottom: '1px solid rgba(0,102,255,0.12)',
                padding: '8px 0',
              },
              children: stats.map((s, i) => ({
                type: 'div', props: {
                  style: {
                    display: 'flex', flexDirection: 'column', alignItems: 'center',
                    flex: 1, padding: '14px 8px',
                    borderRight: i < stats.length - 1 ? '1px solid rgba(255,255,255,0.04)' : 'none',
                  },
                  children: [
                    { type: 'div', props: {
                      style: { fontFamily: 'Orbitron', fontSize: 42, fontWeight: 700, color: '#ffd700', lineHeight: 1 },
                      children: s.num,
                    }},
                    { type: 'div', props: {
                      style: { fontFamily: 'Orbitron', fontSize: 12, fontWeight: 700, color: '#5580a0', marginTop: 4, letterSpacing: 2 },
                      children: s.label,
                    }},
                  ],
                },
              })),
            }},
            // ─── Bottom: Features + URL ───
            { type: 'div', props: {
              style: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' },
              children: [
                // Feature tags
                { type: 'div', props: {
                  style: { display: 'flex', flexWrap: 'wrap', gap: 8 },
                  children: features.map(f => ({
                    type: 'div', props: {
                      style: {
                        padding: '5px 14px', fontSize: 11, fontWeight: 400, color: '#6aa0cc',
                        border: '1px solid rgba(0,170,255,0.15)', borderRadius: 2,
                        background: 'rgba(0,100,200,0.06)', letterSpacing: 0.5,
                        borderLeft: '3px solid rgba(0,136,255,0.4)',
                      },
                      children: f,
                    },
                  })),
                }},
                // URL area
                { type: 'div', props: {
                  style: { display: 'flex', flexDirection: 'column', alignItems: 'flex-end' },
                  children: [
                    { type: 'div', props: {
                      style: { fontFamily: 'Orbitron', fontSize: 22, fontWeight: 700, color: '#ffd700', letterSpacing: 1 },
                      children: 'gget-db.com',
                    }},
                    { type: 'div', props: {
                      style: { fontFamily: 'JP', fontSize: 10, color: '#4a6080', marginTop: 2, letterSpacing: 1 },
                      children: 'by MH GAMES',
                    }},
                  ],
                }},
              ],
            }},
          ],
        }},
      ],
    },
  };

  // ── SVG → PNG ──────────────────────────────
  const svg = await satori(element, { width: 1200, height: 630, fonts });
  const resvg = new Resvg(svg, { fitTo: { mode: 'width', value: 1200 } });
  const pngBuffer = resvg.render().asPng();

  const outPath = join(ROOT, 'public/assets/ogp.png');
  writeFileSync(outPath, pngBuffer);
  console.log(`[generate-ogp] Saved: ${outPath} (1200x630, ${(pngBuffer.length / 1024).toFixed(0)}KB)`);
}

main().catch(err => {
  console.error('[generate-ogp] Error:', err);
  process.exit(1);
});
