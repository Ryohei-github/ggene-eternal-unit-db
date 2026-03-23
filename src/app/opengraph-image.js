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

  const cards = [
    { name: 'シャア専用ザクII(THE ORIGIN版)(EX)', series: '機動戦士ガンダム THE ORIGIN', atk: '16,740', hp: '90,720', def: '9,538', rarity: 'UR', headerColor: 'linear-gradient(90deg, #ffd700, #e8961e)' },
    { name: 'Zガンダム(EX)', series: '機動戦士Zガンダム', atk: '15,774', hp: '100,396', def: '8,568', rarity: 'UR', headerColor: 'linear-gradient(90deg, #ffd700, #e8961e)' },
    { name: 'ガンダム・キマリスヴィダール', series: '機動戦士ガンダム 鉄血のオルフェンズ', atk: '12,340', hp: '78,500', def: '7,210', rarity: 'SSR', headerColor: 'linear-gradient(90deg, #c0c0c0, #94a3b8)' },
  ];

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

        {/* Left panel */}
        <div style={{ display: 'flex', flexDirection: 'column', padding: '45px 0 40px 55px', width: '820px' }}>
          {/* Header */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '16px' }}>
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

        {/* Right panel */}
        <div style={{
          display: 'flex', flexDirection: 'column', justifyContent: 'center',
          padding: '35px 40px 35px 30px', width: '380px', gap: '8px',
          borderLeft: '1px solid rgba(255,255,255,0.024)',
        }}>
          <div style={{ fontSize: '10px', color: '#3a3f50', fontWeight: 700, letterSpacing: '2px', marginBottom: '2px', display: 'flex' }}>DATABASE PREVIEW</div>
          {cards.map((card) => (
            <div key={card.name} style={{
              display: 'flex', flexDirection: 'column',
              background: '#111318', borderRadius: '6px', overflow: 'hidden',
              border: '1px solid #1a1d25',
            }}>
              <div style={{ height: '4px', background: card.headerColor, display: 'flex' }} />
              <div style={{ padding: '10px 14px', display: 'flex', flexDirection: 'column' }}>
                <div style={{ fontSize: '13px', fontWeight: 900, color: '#e0e0e0', marginBottom: '4px', display: 'flex' }}>{card.name}</div>
                <div style={{ fontSize: '10px', color: '#555', marginBottom: '8px', display: 'flex' }}>{card.series}</div>
                <div style={{ display: 'flex', gap: '12px' }}>
                  {[
                    { val: card.atk, lbl: '攻撃力' },
                    { val: card.hp, lbl: 'HP' },
                    { val: card.def, lbl: '防御力' },
                  ].map((st) => (
                    <div key={st.lbl} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                      <div style={{ fontSize: '14px', fontWeight: 900, color: '#ccc', display: 'flex' }}>{st.val}</div>
                      <div style={{ fontSize: '8px', color: '#444', fontWeight: 700, display: 'flex' }}>{st.lbl}</div>
                    </div>
                  ))}
                </div>
                <div style={{ display: 'flex', gap: '4px', marginTop: '6px' }}>
                  <span style={{ fontSize: '8px', padding: '1px 5px', borderRadius: '2px', fontWeight: 700, background: 'rgba(255,215,0,0.13)', color: '#ffd700', display: 'flex' }}>{card.rarity}</span>
                  <span style={{ fontSize: '8px', padding: '1px 5px', borderRadius: '2px', fontWeight: 700, background: 'rgba(214,48,49,0.13)', color: '#ff6b6b', display: 'flex' }}>攻撃</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    ),
    {
      ...size,
      fonts: fontOptions,
    }
  );
}
