import { ImageResponse } from 'next/og';
import { readFileSync } from 'fs';
import { join } from 'path';
import { getAllUnits, getAllCharas } from '@/lib/units';

export const alt = 'GジェネエターナルDB｜Gジェネ エターナル ユニット・キャラ・サポーター検索データベース';
export const size = { width: 1200, height: 630 };
export const contentType = 'image/png';

export default async function Image() {
  // Count data dynamically from JSON files
  const unitCount = getAllUnits().length;
  const charaCount = getAllCharas().length;

  let supporterCount = 0;
  try {
    const supPath = join(process.cwd(), 'public', 'supporters.json');
    const supporters = JSON.parse(readFileSync(supPath, 'utf8'));
    supporterCount = Array.isArray(supporters) ? supporters.length : 0;
  } catch { supporterCount = 0; }

  let itemCount = 0;
  try {
    const itemPath = join(process.cwd(), 'public', 'items.json');
    const items = JSON.parse(readFileSync(itemPath, 'utf8'));
    if (items && items.option_parts) {
      itemCount = items.option_parts.length;
    } else if (Array.isArray(items)) {
      itemCount = items.length;
    }
  } catch { itemCount = 0; }

  // Load font from Google Fonts
  let fontData;
  try {
    const fontRes = await fetch('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@900&display=swap');
    const css = await fontRes.text();
    const fontUrlMatch = css.match(/src:\s*url\(([^)]+)\)/);
    if (fontUrlMatch) {
      const fontFileRes = await fetch(fontUrlMatch[1]);
      fontData = await fontFileRes.arrayBuffer();
    }
  } catch {
    fontData = null;
  }

  const stats = [
    { num: unitCount, label: 'ユニット' },
    { num: charaCount, label: 'キャラ' },
    { num: supporterCount, label: 'サポーター' },
    { num: itemCount, label: 'アイテム' },
  ];

  const features = ['ユニット検索', 'キャラ検索', 'サポーター', 'アイテム', 'ダメージ計算', 'ステータス比較', 'ランキング', 'チーム編成'];

  const fontOptions = fontData ? [{
    name: 'NotoSansJP',
    data: fontData instanceof ArrayBuffer ? fontData : Buffer.from(fontData).buffer,
    style: 'normal',
    weight: 900,
  }] : [];

  return new ImageResponse(
    (
      <div style={{
        width: '1200px', height: '630px', display: 'flex', position: 'relative',
        fontFamily: fontData ? 'NotoSansJP, sans-serif' : 'sans-serif',
        background: '#0a0e17', color: '#fff', overflow: 'hidden',
      }}>
        {/* Top accent line */}
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '3px', background: 'linear-gradient(90deg, #ffd700 0%, #e8961e 40%, #d63031 70%, transparent 100%)', display: 'flex' }} />
        {/* Bottom accent line */}
        <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: '3px', background: 'linear-gradient(90deg, transparent, #d63031 30%, #e8961e 60%, #ffd700)', display: 'flex' }} />
        {/* Horizontal accent line */}
        <div style={{ position: 'absolute', top: '62%', left: 0, right: 0, height: '1px', background: 'linear-gradient(90deg, transparent, rgba(255,215,0,0.12) 20%, rgba(255,215,0,0.19) 50%, rgba(255,215,0,0.12) 80%, transparent)', display: 'flex' }} />

        {/* Main panel */}
        <div style={{ display: 'flex', flexDirection: 'column', padding: '45px 55px 40px 55px', width: '100%' }}>
          {/* Header */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '18px', marginBottom: '16px' }}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="https://yt3.googleusercontent.com/1fHhbDahgzj20gzAsBkKvdA_N5O7uQQ-xU3R8evoky8Nibz6G46Nif9IdfsP94SWavB0HZFI=s240-c-k-c0x00ffffff-no-rj"
              alt=""
              width="56"
              height="56"
              style={{ borderRadius: '50%', border: '2px solid #e8961e' }}
            />
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <div style={{ fontSize: '42px', fontWeight: 900, background: 'linear-gradient(135deg, #ffd700, #ffed4a 40%, #e8961e)', backgroundClip: 'text', color: 'transparent', lineHeight: 1.15, letterSpacing: '-0.5px', display: 'flex' }}>
                GジェネエターナルDB
              </div>
              <div style={{ fontSize: '13px', color: '#666', marginTop: '2px', letterSpacing: '1px', display: 'flex' }}>by MH GAMES</div>
            </div>
          </div>
          <div style={{ fontSize: '15px', color: '#7a7f90', marginBottom: '20px', display: 'flex' }}>
            Gジェネ エターナル 全レアリティ対応 総合データベース
          </div>

          {/* Stats */}
          <div style={{ display: 'flex', gap: '8px', marginBottom: '18px' }}>
            {stats.map((s) => (
              <div key={s.label} style={{
                display: 'flex', flexDirection: 'column', alignItems: 'center',
                background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,215,0,0.08)',
                borderRadius: '8px', padding: '10px 20px', flex: 1,
              }}>
                <div style={{ fontSize: '32px', fontWeight: 900, color: '#ffd700', lineHeight: 1.1, display: 'flex' }}>{s.num}</div>
                <div style={{ fontSize: '11px', color: '#5a5f70', fontWeight: 700, marginTop: '1px', display: 'flex' }}>{s.label}</div>
              </div>
            ))}
          </div>

          {/* Features */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '20px' }}>
            {features.map((f) => (
              <div key={f} style={{
                padding: '4px 10px', fontSize: '11px', fontWeight: 700, color: '#888',
                border: '1px solid rgba(255,255,255,0.06)', borderRadius: '3px',
                background: 'rgba(255,255,255,0.02)', display: 'flex',
              }}>{f}</div>
            ))}
          </div>

          {/* URL */}
          <div style={{ marginTop: 'auto', fontSize: '24px', fontWeight: 900, color: '#ffd700', display: 'flex' }}>gget-db.com</div>
        </div>
      </div>
    ),
    {
      ...size,
      fonts: fontOptions,
    }
  );
}
