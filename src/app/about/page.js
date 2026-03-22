export const metadata = {
  title: 'このサイトについて',
  description: 'GジェネエターナルDBの運営者情報。MH GAMESが運営するGジェネ エターナルの非公式ファンサイトデータベースです。',
  alternates: {
    canonical: '/about',
  },
  openGraph: {
    title: 'このサイトについて | GジェネエターナルDB',
    description: 'GジェネエターナルDBの運営者情報。MH GAMESが運営するGジェネ エターナルの非公式ファンサイトデータベースです。',
    type: 'website',
    url: '/about',
    siteName: 'GジェネエターナルDB by MH GAMES',
    locale: 'ja_JP',
  },
};

export default function AboutPage() {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(180deg, #0a0e17 0%, #111827 100%)',
      color: '#e0ddd6',
      fontFamily: "'Segoe UI', sans-serif",
    }}>
      {/* Header */}
      <header style={{
        background: 'linear-gradient(135deg, #0e1016, #161a22)',
        borderBottom: '2px solid transparent',
        borderImage: 'linear-gradient(90deg, transparent, #e8961e, #d63031, transparent) 1',
        padding: '20px',
        textAlign: 'center',
      }}>
        <a href="/" style={{ textDecoration: 'none' }}>
          <h1 style={{
            fontSize: '1.4em',
            letterSpacing: '2px',
            background: 'linear-gradient(90deg, #f0a830, #ffd700, #e8961e)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>GジェネエターナルDB</h1>
          <p style={{ fontSize: '.75em', color: '#8a8d98', marginTop: '2px' }}>
            Gジェネ エターナル 全レアリティ対応データベース
          </p>
        </a>
      </header>

      {/* Content */}
      <main style={{ maxWidth: '720px', margin: '0 auto', padding: '40px 20px 80px' }}>

        <h2 style={{
          fontSize: '1.5em',
          fontWeight: 700,
          marginBottom: '32px',
          color: '#ffd700',
          borderBottom: '2px solid rgba(232, 150, 30, .3)',
          paddingBottom: '12px',
        }}>このサイトについて</h2>

        {/* 運営者情報 */}
        <section style={{ marginBottom: '40px' }}>
          <h3 style={{
            fontSize: '1.1em',
            fontWeight: 700,
            color: '#e8961e',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}>
            <span style={{
              display: 'inline-block',
              width: '4px',
              height: '20px',
              background: '#e8961e',
              borderRadius: '2px',
            }}></span>
            運営者情報
          </h3>

          <div style={{
            background: 'rgba(255,255,255,.03)',
            border: '1px solid rgba(255,255,255,.08)',
            borderRadius: '12px',
            padding: '24px',
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '16px',
              marginBottom: '20px',
            }}>
              <img
                src="https://yt3.googleusercontent.com/1fHhbDahgzj20gzAsBkKvdA_N5O7uQQ-xU3R8evoky8Nibz6G46Nif9IdfsP94SWavB0HZFI=s240-c-k-c0x00ffffff-no-rj"
                alt="MH GAMES"
                width="64"
                height="64"
                style={{
                  borderRadius: '50%',
                  border: '2px solid #e8961e',
                  flexShrink: 0,
                }}
              />
              <div>
                <div style={{ fontSize: '1.2em', fontWeight: 700 }}>MH GAMES</div>
                <div style={{ fontSize: '.85em', color: '#8a8d98', marginTop: '2px' }}>
                  ゲーム攻略・データベースサイト運営
                </div>
              </div>
            </div>

            <p style={{
              fontSize: '.95em',
              lineHeight: 1.8,
              color: '#c0bdb6',
              marginBottom: '20px',
            }}>
              当サイト「GジェネエターナルDB」は、バンダイナムコエンターテインメントのゲーム
              「SDガンダム ジージェネレーション エターナル」のユニット・キャラクター・サポーターの
              データを網羅したファンメイドの非公式データベースサイトです。
              ゲームを楽しむプレイヤーの皆さんの攻略・編成のお役に立てれば幸いです。
            </p>

            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
            }}>
              {/* YouTube */}
              <a
                href="https://www.youtube.com/@MH_GAMES_JP"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '14px 16px',
                  background: 'rgba(255, 0, 0, .08)',
                  border: '1px solid rgba(255, 0, 0, .2)',
                  borderRadius: '10px',
                  textDecoration: 'none',
                  color: '#e0ddd6',
                  transition: 'all .2s',
                }}
              >
                <span style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '40px',
                  height: '40px',
                  borderRadius: '10px',
                  background: '#ff0000',
                  color: '#fff',
                  fontWeight: 800,
                  fontSize: '.75em',
                  flexShrink: 0,
                }}>▶</span>
                <div>
                  <div style={{ fontWeight: 700, fontSize: '.95em' }}>YouTube - MH GAMES</div>
                  <div style={{ fontSize: '.8em', color: '#8a8d98' }}>
                    ゲーム実況・攻略動画を配信中
                  </div>
                </div>
              </a>

              {/* X (Twitter) */}
              <a
                href="https://x.com/mh_games_jp"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '14px 16px',
                  background: 'rgba(255, 255, 255, .03)',
                  border: '1px solid rgba(255, 255, 255, .1)',
                  borderRadius: '10px',
                  textDecoration: 'none',
                  color: '#e0ddd6',
                  transition: 'all .2s',
                }}
              >
                <span style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '40px',
                  height: '40px',
                  borderRadius: '10px',
                  background: '#000',
                  border: '1px solid #333',
                  color: '#fff',
                  fontWeight: 800,
                  fontSize: '1.1em',
                  flexShrink: 0,
                }}>𝕏</span>
                <div>
                  <div style={{ fontWeight: 700, fontSize: '.95em' }}>X (Twitter) - @mh_games_jp</div>
                  <div style={{ fontSize: '.8em', color: '#8a8d98' }}>
                    更新情報・お知らせを発信中。お問い合わせはDMへ
                  </div>
                </div>
              </a>

              {/* サイト */}
              <a
                href="https://gget-db.com"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '14px 16px',
                  background: 'rgba(232, 150, 30, .06)',
                  border: '1px solid rgba(232, 150, 30, .2)',
                  borderRadius: '10px',
                  textDecoration: 'none',
                  color: '#e0ddd6',
                  transition: 'all .2s',
                }}
              >
                <img
                  src="/favicon.svg"
                  alt="GジェネエターナルDB"
                  width="40"
                  height="40"
                  style={{
                    borderRadius: '10px',
                    flexShrink: 0,
                  }}
                />
                <div>
                  <div style={{ fontWeight: 700, fontSize: '.95em' }}>GジェネエターナルDB</div>
                  <div style={{ fontSize: '.8em', color: '#8a8d98' }}>
                    gget-db.com — ユニット・キャラ・サポーター検索
                  </div>
                </div>
              </a>
            </div>
          </div>
        </section>

        {/* 免責事項（軽く） */}
        <section style={{
          fontSize: '.8em',
          color: '#6a6d78',
          lineHeight: 1.7,
          borderTop: '1px solid rgba(255,255,255,.06)',
          paddingTop: '20px',
        }}>
          <p>
            当サイトはバンダイナムコエンターテインメントとは一切関係のない非公式ファンサイトです。
            掲載されている画像・データの著作権は各権利者に帰属します。
            データの正確性については可能な限り努力しておりますが、誤りがある場合は
            <a href="https://x.com/mh_games_jp" target="_blank" rel="noopener noreferrer" style={{ color: '#e8961e' }}>X (@mh_games_jp)</a> までご連絡ください。
          </p>
          <p style={{ marginTop: '8px' }}>
            © 2026 MH GAMES — GジェネエターナルDB by MH GAMES
          </p>
        </section>

        {/* トップへ戻る */}
        <div style={{ textAlign: 'center', marginTop: '40px' }}>
          <a href="/" style={{
            display: 'inline-block',
            padding: '10px 32px',
            background: 'rgba(232, 150, 30, .1)',
            border: '1px solid rgba(232, 150, 30, .3)',
            borderRadius: '8px',
            color: '#e8961e',
            fontWeight: 700,
            fontSize: '.9em',
            textDecoration: 'none',
          }}>← トップページに戻る</a>
        </div>
      </main>
    </div>
  );
}
