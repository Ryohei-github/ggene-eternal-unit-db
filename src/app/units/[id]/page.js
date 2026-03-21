import { getAllUnits, getUnitById } from '@/lib/units';
import UnitDetailClient from './UnitDetailClient';

// Generate all unit pages at build time
export async function generateStaticParams() {
  const units = getAllUnits();
  return units.map((unit) => ({
    id: String(unit.id),
  }));
}

// Dynamic metadata for each unit page
export async function generateMetadata({ params }) {
  const { id } = await params;
  const unit = getUnitById(id);
  if (!unit) {
    return { title: 'ユニットが見つかりません' };
  }

  const stats = unit.normal?.stats || {};
  const series = (unit.series || []).join('、');
  const description = `${unit.name}のステータス・武装・スキル詳細。HP:${stats.hp || '-'} 攻撃:${stats.attack || '-'} 防御:${stats.defense || '-'}。${series ? 'シリーズ: ' + series + '。' : ''}Gジェネ エターナルDBで詳しく確認。`;

  return {
    title: `${unit.name}`,
    description,
    alternates: {
      canonical: `/units/${id}`,
    },
    openGraph: {
      title: `${unit.name} | GジェネエターナルDB`,
      description,
      type: 'article',
      url: `/units/${id}`,
      images: unit.image ? [{ url: unit.image }] : [],
      siteName: 'GジェネエターナルDB by MH GAMES',
      locale: 'ja_JP',
    },
    twitter: {
      card: 'summary',
      site: '@mh_games_jp',
      title: `${unit.name} | GジェネエターナルDB`,
      description,
    },
  };
}

export default async function UnitPage({ params }) {
  const { id } = await params;
  const unit = getUnitById(id);

  if (!unit) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: '#fff' }}>
        <h1>ユニットが見つかりません</h1>
        <a href="/" style={{ color: '#4fc3f7' }}>トップページに戻る</a>
      </div>
    );
  }

  const stats = unit.normal?.stats || {};
  const terrain = unit.normal?.terrain || {};
  const abilities = unit.normal?.abilities || [];
  const weapons = unit.normal_weapons || [];
  const mechanism = unit.normal?.mechanism || '';
  const statsByStar = unit.stats_by_star || [];

  // JSON-LD structured data for this unit
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    name: unit.name,
    headline: `${unit.name} - GジェネエターナルDB`,
    description: `${unit.name}のステータス・武装・スキル詳細`,
    url: `https://gget-db.com/units/${id}`,
    image: unit.image ? `https://gget-db.com${unit.image}` : undefined,
    author: {
      '@type': 'Organization',
      name: 'MH GAMES',
      url: 'https://www.youtube.com/@MH_GAMES_JP',
    },
    publisher: {
      '@type': 'Organization',
      name: 'GジェネエターナルDB',
      url: 'https://gget-db.com',
    },
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

        {/* Unit header */}
        <div className="unit-detail-header">
          {unit.image && (
            <img
              src={unit.image}
              alt={unit.name}
              className="unit-detail-image"
              width={120}
              height={120}
              loading="eager"
            />
          )}
          <div className="unit-detail-info">
            <h1 className="unit-detail-name">{unit.name}</h1>
            <div className="unit-detail-meta">
              <span className={`rarity-badge rarity-${unit.rarity}`}>{unit.rarity}</span>
              <span className="type-badge">{unit.type}</span>
              {mechanism && <span className="mechanism-badge">{mechanism}</span>}
            </div>
            {unit.series && unit.series.length > 0 && (
              <div className="unit-detail-series">
                {unit.series.map((s, i) => (
                  <span key={i} className="series-tag">{s}</span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Stats section */}
        <section className="unit-detail-section">
          <h2>ステータス</h2>
          <div className="stats-grid">
            <div className="stat-item"><span className="stat-label">HP</span><span className="stat-value">{stats.hp?.toLocaleString() || '-'}</span></div>
            <div className="stat-item"><span className="stat-label">EN</span><span className="stat-value">{stats.en?.toLocaleString() || '-'}</span></div>
            <div className="stat-item"><span className="stat-label">攻撃</span><span className="stat-value">{stats.attack?.toLocaleString() || '-'}</span></div>
            <div className="stat-item"><span className="stat-label">防御</span><span className="stat-value">{stats.defense?.toLocaleString() || '-'}</span></div>
            <div className="stat-item"><span className="stat-label">機動</span><span className="stat-value">{stats.mobility || '-'}</span></div>
            <div className="stat-item"><span className="stat-label">運動</span><span className="stat-value">{stats.agility?.toLocaleString() || '-'}</span></div>
          </div>
        </section>

        {/* Limit Break Stats section */}
        {statsByStar.length > 0 && (
          <section className="unit-detail-section">
            <h2>限界突破ステータス</h2>
            <div className="limit-break-table-wrap">
              <table className="limit-break-table">
                <thead>
                  <tr>
                    <th>★</th>
                    <th>Lv</th>
                    <th>HP</th>
                    <th>EN</th>
                    <th>攻撃</th>
                    <th>防御</th>
                    <th>機動</th>
                    <th>運動</th>
                  </tr>
                </thead>
                <tbody>
                  {statsByStar.map((s, i) => (
                    <tr key={i} className={s.star === 3 ? 'limit-break-max' : ''}>
                      <td className="lb-star">{'★'.repeat(s.star) || '−'}</td>
                      <td>{s.lv}</td>
                      <td>{s.hp?.toLocaleString()}</td>
                      <td>{s.en?.toLocaleString()}</td>
                      <td>{s.attack?.toLocaleString()}</td>
                      <td>{s.defense?.toLocaleString()}</td>
                      <td>{s.mobility}</td>
                      <td>{s.agility?.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {/* Terrain section */}
        <section className="unit-detail-section">
          <h2>地形適性</h2>
          <div className="terrain-grid">
            {Object.entries(terrain).map(([key, val]) => (
              <div key={key} className="terrain-item">
                <span className="terrain-label">{key}</span>
                <span className={`terrain-value terrain-${val === '◎' ? 'ss' : val === '◯' ? 's' : val === '△' ? 'b' : 'none'}`}>{val}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Abilities section */}
        {abilities.length > 0 && (
          <section className="unit-detail-section">
            <h2>アビリティ</h2>
            <div className="abilities-list">
              {abilities.map((ab, i) => (
                <div key={i} className="ability-item">
                  <span className="ability-name">{ab.name}</span>
                  <span className="ability-desc">{ab.desc}</span>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Weapons section */}
        {weapons.length > 0 && (
          <section className="unit-detail-section">
            <h2>武装</h2>
            <div className="weapons-table-wrap">
              <table className="weapons-table">
                <thead>
                  <tr>
                    <th>武装名</th>
                    <th>属性</th>
                    <th>種別</th>
                    <th>射程</th>
                    <th>威力</th>
                    <th>EN</th>
                    <th>命中</th>
                    <th>CT</th>
                    <th>効果</th>
                  </tr>
                </thead>
                <tbody>
                  {weapons.map((w, i) => (
                    <tr key={i}>
                      <td>{w.name}</td>
                      <td>{w.attribute}</td>
                      <td>{w.weapon_type}</td>
                      <td>{w.range}</td>
                      <td>{w.power}</td>
                      <td>{w.en}</td>
                      <td>{w.hit}</td>
                      <td>{w.critical}</td>
                      <td className="weapon-effect">{w.effect || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {/* Tags section */}
        {unit.tags && unit.tags.length > 0 && (
          <section className="unit-detail-section">
            <h2>タグ</h2>
            <div className="tags-list">
              {unit.tags.map((tag, i) => (
                <span key={i} className="unit-tag">{tag}</span>
              ))}
            </div>
          </section>
        )}

        {/* Additional info */}
        <section className="unit-detail-section">
          <h2>その他</h2>
          <div className="other-info">
            {unit.obtain && <div><span className="info-label">入手方法:</span> {unit.acquire || unit.obtain}</div>}
            {unit.normal?.combat_power && <div><span className="info-label">戦闘力:</span> {unit.normal.combat_power.toLocaleString()}</div>}
          </div>
        </section>

        {/* Client-side interactive features */}
        <UnitDetailClient unit={unit} />
      </div>
    </>
  );
}
