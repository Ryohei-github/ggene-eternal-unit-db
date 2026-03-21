import { getAllCharas, getCharaById } from '@/lib/units';

// Generate all character pages at build time
export async function generateStaticParams() {
  const charas = getAllCharas();
  return charas.map((c) => ({
    id: String(c.id),
  }));
}

// Dynamic metadata for each character page
export async function generateMetadata({ params }) {
  const { id } = await params;
  const chara = getCharaById(id);
  if (!chara) {
    return { title: 'キャラが見つかりません' };
  }

  const stats = chara.normal?.stats || {};
  const series = (chara.series || []).join('、');
  const description = `${chara.name}(${chara.rarity})のステータス・スキル・アビリティ詳細。射撃:${stats.shooting || '-'} 格闘:${stats.melee || '-'} 覚醒:${stats.awakening || '-'}。${series ? 'シリーズ: ' + series + '。' : ''}${chara.sp_stats ? 'SP化後ステータスあり。' : ''}Gジェネ エターナルDBで詳しく確認。`;

  return {
    title: `${chara.name}(${chara.rarity})`,
    description,
    alternates: {
      canonical: `/charas/${id}`,
    },
    openGraph: {
      title: `${chara.name}(${chara.rarity}) | GジェネエターナルDB`,
      description,
      type: 'article',
      url: `/charas/${id}`,
      images: chara.image ? [{ url: chara.image }] : [],
      siteName: 'GジェネエターナルDB by MH GAMES',
      locale: 'ja_JP',
    },
    twitter: {
      card: 'summary',
      site: '@mh_games_jp',
      title: `${chara.name}(${chara.rarity}) | GジェネエターナルDB`,
      description,
    },
  };
}

export default async function CharaPage({ params }) {
  const { id } = await params;
  const chara = getCharaById(id);

  if (!chara) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: '#fff' }}>
        <h1>キャラが見つかりません</h1>
        <a href="/" style={{ color: '#4fc3f7' }}>トップページに戻る</a>
      </div>
    );
  }

  const stats = chara.normal?.stats || {};
  const skills = chara.normal?.skills || [];
  const abilities = chara.normal?.abilities || [];
  const spStats = chara.sp_stats || null;
  const spSkills = chara.sp_skills || null;
  const spAbilities = chara.sp_abilities || null;
  const lv100Stats = chara.lv100_stats || null;
  const isUR = chara.rarity === 'UR';

  // Determine max levels based on rarity
  let baseLv, spLv;
  if (chara.rarity === 'SR') { baseLv = 80; spLv = 100; }
  else if (chara.rarity === 'SSR') { baseLv = 90; spLv = 100; }
  else if (chara.rarity === 'R') { baseLv = 70; spLv = 100; }
  else { baseLv = 100; spLv = null; } // UR

  // JSON-LD structured data
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    name: `${chara.name}(${chara.rarity})`,
    headline: `${chara.name}(${chara.rarity}) - GジェネエターナルDB`,
    description: `${chara.name}のステータス・スキル・アビリティ詳細`,
    url: `https://gget-db.com/charas/${id}`,
    image: chara.image ? `https://gget-db.com${chara.image}` : undefined,
    author: { '@type': 'Organization', name: 'MH GAMES', url: 'https://www.youtube.com/@MH_GAMES_JP' },
    publisher: { '@type': 'Organization', name: 'GジェネエターナルDB', url: 'https://gget-db.com' },
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <div className="unit-detail-ssg">
        {/* Back link */}
        <div style={{ padding: '12px 16px' }}>
          <a href="/" style={{ color: '#4fc3f7', textDecoration: 'none', fontSize: '14px' }}>
            ← トップページに戻る
          </a>
        </div>

        {/* Character header */}
        <div className="unit-detail-header">
          {chara.image && (
            <img
              src={chara.image}
              alt={chara.name}
              className="unit-detail-image"
              width={120}
              height={120}
              loading="eager"
            />
          )}
          <div className="unit-detail-info">
            <h1 className="unit-detail-name">{chara.name}</h1>
            <div className="unit-detail-meta">
              <span className={`rarity-badge rarity-${chara.rarity}`}>{chara.rarity}</span>
              <span className="type-badge">{chara.type}</span>
            </div>
            {chara.series && chara.series.length > 0 && (
              <div className="unit-detail-series">
                {chara.series.map((s, i) => (
                  <span key={i} className="series-tag">{s}</span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Stats comparison table */}
        <section className="unit-detail-section">
          <h2>ステータス</h2>
          <div className="limit-break-table-wrap">
            <table className="limit-break-table">
              <thead>
                <tr>
                  <th style={{ textAlign: 'left' }}>状態</th>
                  <th>射撃</th>
                  <th>格闘</th>
                  <th>覚醒</th>
                  <th>守備</th>
                  <th>反応</th>
                  <th>SP</th>
                </tr>
              </thead>
              <tbody>
                {/* Base stats row */}
                <tr>
                  <td style={{ textAlign: 'left', color: '#90caf9', fontWeight: 600 }}>
                    {isUR ? 'Lv100' : `Lv${baseLv}`}
                  </td>
                  <td>{stats.shooting?.toLocaleString() || '-'}</td>
                  <td>{stats.melee?.toLocaleString() || '-'}</td>
                  <td>{stats.awakening?.toLocaleString() || '-'}</td>
                  <td>{stats.defense?.toLocaleString() || '-'}</td>
                  <td>{stats.reaction?.toLocaleString() || '-'}</td>
                  <td>{stats.sp || '-'}</td>
                </tr>
                {/* SP化 stats row (non-UR only) */}
                {!isUR && spStats && (
                  <tr className="limit-break-max">
                    <td style={{ textAlign: 'left', fontWeight: 600 }}>
                      Lv{spLv} SP化
                    </td>
                    <td>{spStats.shooting?.toLocaleString() || '-'}</td>
                    <td>{spStats.melee?.toLocaleString() || '-'}</td>
                    <td>{spStats.awakening?.toLocaleString() || '-'}</td>
                    <td>{spStats.defense?.toLocaleString() || '-'}</td>
                    <td>{spStats.reaction?.toLocaleString() || '-'}</td>
                    <td>{spStats.sp || '-'}</td>
                  </tr>
                )}
                {/* UR Lv100 stats row */}
                {isUR && lv100Stats && (
                  <tr className="limit-break-max">
                    <td style={{ textAlign: 'left', fontWeight: 600 }}>
                      Lv100(参考値)
                    </td>
                    <td>{lv100Stats.shooting?.toLocaleString() || '-'}</td>
                    <td>{lv100Stats.melee?.toLocaleString() || '-'}</td>
                    <td>{lv100Stats.awakening?.toLocaleString() || '-'}</td>
                    <td>{lv100Stats.defense?.toLocaleString() || '-'}</td>
                    <td>{lv100Stats.reaction?.toLocaleString() || '-'}</td>
                    <td>{lv100Stats.sp || '-'}</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        {/* Skills section */}
        {skills.length > 0 && (
          <section className="unit-detail-section">
            <h2>スキル{!isUR && spSkills ? '（通常）' : ''}</h2>
            <div className="abilities-list">
              {skills.map((sk, i) => (
                <div key={i} className="ability-item">
                  <span className="ability-name">{sk.name}</span>
                  <span className="ability-desc">SP:{sk.sp_cost} / {sk.effect}</span>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* SP化 Skills section */}
        {!isUR && spSkills && spSkills.length > 0 && (
          <section className="unit-detail-section chara-sp-section">
            <h2>スキル（SP化後）</h2>
            <div className="abilities-list">
              {spSkills.map((sk, i) => (
                <div key={i} className="ability-item sp-enhanced">
                  <span className="ability-name">{sk.name}</span>
                  <span className="ability-desc">SP:{sk.sp_cost} / {sk.effect}</span>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Abilities section */}
        {abilities.length > 0 && (
          <section className="unit-detail-section">
            <h2>アビリティ{!isUR && spAbilities ? '（通常）' : ''}</h2>
            <div className="abilities-list">
              {abilities.map((ab, i) => (
                <div key={i} className="ability-item">
                  <span className="ability-name">{ab.name}</span>
                  <span className="ability-desc">{ab.desc}{ab.condition ? ` [${ab.condition}]` : ''}</span>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* SP化 Abilities section */}
        {!isUR && spAbilities && spAbilities.length > 0 && (
          <section className="unit-detail-section chara-sp-section">
            <h2>アビリティ（SP化後）</h2>
            <div className="abilities-list">
              {spAbilities.map((ab, i) => (
                <div key={i} className="ability-item sp-enhanced">
                  <span className="ability-name">{ab.name}</span>
                  <span className="ability-desc">{ab.desc}{ab.condition ? ` [${ab.condition}]` : ''}</span>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Tags section */}
        {chara.tags && chara.tags.length > 0 && (
          <section className="unit-detail-section">
            <h2>タグ</h2>
            <div className="tags-list">
              {chara.tags.map((tag, i) => (
                <span key={i} className="unit-tag">{tag}</span>
              ))}
            </div>
          </section>
        )}

        {/* Additional info */}
        <section className="unit-detail-section">
          <h2>その他</h2>
          <div className="other-info">
            {chara.acquire && <div><span className="info-label">入手方法:</span> {chara.acquire}</div>}
            {chara.normal?.combat_power && <div><span className="info-label">戦闘力:</span> {chara.normal.combat_power.toLocaleString()}</div>}
          </div>
        </section>
      </div>
    </>
  );
}
