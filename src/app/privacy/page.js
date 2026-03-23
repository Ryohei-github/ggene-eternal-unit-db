export const metadata = {
  title: 'プライバシーポリシー',
  description: 'GジェネエターナルDBのプライバシーポリシー。Google Analytics・Google AdSenseの利用、Cookieの取り扱いなどについて。',
  alternates: {
    canonical: '/privacy',
  },
  openGraph: {
    title: 'プライバシーポリシー | GジェネエターナルDB',
    description: 'GジェネエターナルDBのプライバシーポリシー。Google Analytics・Google AdSenseの利用、Cookieの取り扱いなどについて。',
    type: 'website',
    url: '/privacy',
    siteName: 'GジェネエターナルDB by MH GAMES',
    locale: 'ja_JP',
  },
};

const sectionStyle = {
  marginBottom: '36px',
};

const h3Style = {
  fontSize: '1.1em',
  fontWeight: 700,
  color: '#e8961e',
  marginBottom: '16px',
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
};

const barStyle = {
  display: 'inline-block',
  width: '4px',
  height: '20px',
  background: '#e8961e',
  borderRadius: '2px',
};

const pStyle = {
  fontSize: '.93em',
  lineHeight: 1.85,
  color: '#c0bdb6',
  marginBottom: '12px',
};

export default function PrivacyPage() {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(180deg, #0a0e17 0%, #111827 100%)',
      color: '#e0ddd6',
      fontFamily: "'Segoe UI', sans-serif",
    }}>
      {/* Header - SPAと同じ構成 */}
      <header className="header" role="banner">
        <div className="header-brand">
          <img
            className="header-icon"
            src="https://yt3.googleusercontent.com/1fHhbDahgzj20gzAsBkKvdA_N5O7uQQ-xU3R8evoky8Nibz6G46Nif9IdfsP94SWavB0HZFI=s240-c-k-c0x00ffffff-no-rj"
            alt="MH GAMES"
            width="36"
            height="36"
            loading="eager"
          />
          <h1><a href="/" style={{ textDecoration: 'none' }}>GジェネエターナルDB</a> <a href="https://www.youtube.com/@MH_GAMES_JP" target="_blank" className="sub-brand" style={{ textDecoration: 'none' }}>by MH GAMES</a></h1>
        </div>
        <p className="sub">Gジェネ エターナル 全レアリティ対応データベース</p>
        <nav className="header-links" aria-label="外部リンク">
          <a className="btn-yt" href="https://www.youtube.com/@MH_GAMES_JP?sub_confirmation=1" target="_blank" rel="noopener noreferrer">▶ チャンネル登録</a>
          <a className="btn-x" href="https://x.com/mh_games_jp" target="_blank" rel="noopener noreferrer">𝕏 ご意見はこちら</a>
          <a className="btn-about" href="/about">ℹ このサイトについて</a>
        </nav>
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
        }}>プライバシーポリシー</h2>

        <p style={{ ...pStyle, marginBottom: '32px' }}>
          GジェネエターナルDB（以下「当サイト」）は、ユーザーの個人情報およびプライバシーの保護に努めています。
          当サイトにおける情報の取り扱いについて、以下のとおり定めます。
        </p>

        {/* Google Analytics */}
        <section style={sectionStyle}>
          <h3 style={h3Style}>
            <span style={barStyle}></span>
            アクセス解析ツールについて
          </h3>
          <p style={pStyle}>
            当サイトでは、Googleによるアクセス解析ツール「Google Analytics」を使用しています。
            Google Analyticsはデータの収集のためにCookieを使用しています。
            このデータは匿名で収集されており、個人を特定するものではありません。
          </p>
          <p style={pStyle}>
            この機能はCookieを無効にすることで収集を拒否することができますので、
            お使いのブラウザの設定をご確認ください。
            Google Analyticsの利用規約およびプライバシーポリシーについては、
            <a href="https://marketingplatform.google.com/about/analytics/terms/jp/" target="_blank" rel="noopener noreferrer" style={{ color: '#e8961e' }}>Google アナリティクス利用規約</a>および
            <a href="https://policies.google.com/privacy?hl=ja" target="_blank" rel="noopener noreferrer" style={{ color: '#e8961e' }}>Googleプライバシーポリシー</a>をご覧ください。
          </p>
        </section>

        {/* Google AdSense */}
        <section style={sectionStyle}>
          <h3 style={h3Style}>
            <span style={barStyle}></span>
            広告配信について
          </h3>
          <p style={pStyle}>
            当サイトでは、第三者配信の広告サービス「Google AdSense（グーグルアドセンス）」を利用しています。
            Google AdSenseは、ユーザーの興味に応じた広告を表示するためにCookieを使用することがあります。
          </p>
          <p style={pStyle}>
            Googleが広告Cookieを使用することにより、ユーザーが当サイトや他のサイトにアクセスした際の
            情報に基づいて、適切な広告を表示できます。
            ユーザーは、<a href="https://www.google.com/settings/ads" target="_blank" rel="noopener noreferrer" style={{ color: '#e8961e' }}>広告設定</a>で
            パーソナライズ広告を無効にすることができます。
          </p>
          <p style={pStyle}>
            詳細については
            <a href="https://policies.google.com/technologies/ads?hl=ja" target="_blank" rel="noopener noreferrer" style={{ color: '#e8961e' }}>Google広告に関するポリシー</a>をご確認ください。
          </p>
        </section>

        {/* Cookie */}
        <section style={sectionStyle}>
          <h3 style={h3Style}>
            <span style={barStyle}></span>
            Cookieについて
          </h3>
          <p style={pStyle}>
            当サイトでは、上記のGoogle AnalyticsおよびGoogle AdSenseにおいてCookieを使用しています。
            Cookieとは、ウェブサイトがユーザーのブラウザに保存する小さなテキストファイルです。
          </p>
          <p style={pStyle}>
            ユーザーはブラウザの設定によりCookieの受け入れを拒否することができますが、
            その場合は当サイトの一部機能が正しく動作しない可能性があります。
          </p>
        </section>

        {/* 個人情報の取り扱い */}
        <section style={sectionStyle}>
          <h3 style={h3Style}>
            <span style={barStyle}></span>
            個人情報の取り扱いについて
          </h3>
          <p style={pStyle}>
            当サイトでは、お問い合わせの際にお名前やメールアドレスなどの個人情報を
            ご提供いただく場合があります。取得した個人情報は、お問い合わせへの回答や
            必要な情報をご連絡するためのみに利用し、それ以外の目的では使用しません。
          </p>
        </section>

        {/* 免責事項 */}
        <section style={sectionStyle}>
          <h3 style={h3Style}>
            <span style={barStyle}></span>
            免責事項
          </h3>
          <p style={pStyle}>
            当サイトに掲載されている情報の正確性には万全を期していますが、
            その内容の正確性・安全性を保証するものではありません。
            当サイトの情報を利用することで生じたいかなる損害についても、
            一切の責任を負いかねます。
          </p>
          <p style={pStyle}>
            当サイトからリンクやバナーなどで移動した外部サイトで提供される情報・サービスについても、
            一切の責任を負いません。
          </p>
        </section>

        {/* 著作権 */}
        <section style={sectionStyle}>
          <h3 style={h3Style}>
            <span style={barStyle}></span>
            著作権について
          </h3>
          <p style={pStyle}>
            当サイトは、バンダイナムコエンターテインメントの「SDガンダム ジージェネレーション エターナル」の
            非公式ファンサイトです。掲載されている画像・データの著作権は各権利者に帰属します。
            著作権や肖像権に関して問題がございましたら、
            <a href="https://x.com/mh_games_jp" target="_blank" rel="noopener noreferrer" style={{ color: '#e8961e' }}>X (@mh_games_jp)</a> の
            DMまでご連絡ください。
          </p>
        </section>

        {/* お問い合わせ */}
        <section style={sectionStyle}>
          <h3 style={h3Style}>
            <span style={barStyle}></span>
            お問い合わせ
          </h3>
          <p style={pStyle}>
            当サイトに関するお問い合わせは、
            <a href="https://x.com/mh_games_jp" target="_blank" rel="noopener noreferrer" style={{ color: '#e8961e' }}>X (@mh_games_jp)</a> の
            DMよりお願いいたします。
          </p>
        </section>

        {/* 改定 */}
        <section style={{
          fontSize: '.82em',
          color: '#6a6d78',
          lineHeight: 1.7,
          borderTop: '1px solid rgba(255,255,255,.06)',
          paddingTop: '20px',
        }}>
          <p>
            当サイトは、必要に応じて本プライバシーポリシーの内容を変更することがあります。
            変更後のプライバシーポリシーは、当ページに掲載した時点から効力を生じるものとします。
          </p>
          <p style={{ marginTop: '12px' }}>
            制定日：2026年3月23日
          </p>
          <p style={{ marginTop: '8px' }}>
            運営者：MH GAMES
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

      {/* Footer - SPAと同じ構成 */}
      <footer className="site-footer" role="contentinfo">
        <nav className="footer-links" aria-label="フッターリンク">
          <a href="https://www.youtube.com/@MH_GAMES_JP?sub_confirmation=1" target="_blank" rel="noopener noreferrer">▶ YouTube チャンネル登録</a>
          <a href="https://x.com/mh_games_jp" target="_blank" rel="noopener noreferrer">𝕏 公式X（ご意見はこちら）</a>
          <a href="/about">ℹ このサイトについて</a>
          <a href="/privacy">🔒 プライバシーポリシー</a>
        </nav>
        <p className="footer-copy">© 2026 MH GAMES — GジェネエターナルDB by MH GAMES｜当サイトはゲームの攻略情報を提供するファンサイトです</p>
      </footer>
    </div>
  );
}
