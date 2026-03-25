import './globals.css';
import Script from 'next/script';

export const metadata = {
  title: {
    default: 'GジェネエターナルDB｜Gジェネ エターナル ユニット・キャラ・サポーター検索データベース',
    template: '%s | GジェネエターナルDB',
  },
  description: 'Gジェネレーション エターナル（Gジェネ エターナル）の全ユニット・キャラクター・サポーターを網羅したデータベース。レアリティ・シリーズ・タイプ・デバフ効果など多彩なフィルタで検索可能。ステータス比較やスキル確認に。',
  keywords: ['Gジェネ エターナル', 'G Generation Eternal', 'GジェネエターナルDB', 'ユニット一覧', 'キャラクター', 'サポーター', 'データベース', 'ステータス', 'スキル', '攻略', '検索'],
  metadataBase: new URL('https://gget-db.com'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    title: 'GジェネエターナルDB｜ユニット・キャラ・サポーター検索データベース',
    description: 'Gジェネ エターナルの全ユニット・キャラクター・サポーターを網羅。レアリティ・シリーズ・デバフ効果など多彩なフィルタで検索可能。',
    type: 'website',
    url: 'https://gget-db.com/',
    siteName: 'GジェネエターナルDB by MH GAMES',
    locale: 'ja_JP',
    // OGP画像はopengraph-image.jsで動的生成（データ件数を自動反映）
  },
  twitter: {
    card: 'summary_large_image',
    site: '@mh_games_jp',
    title: 'GジェネエターナルDB｜ユニット・キャラ・サポーター検索',
    description: 'Gジェネ エターナルの全ユニット・キャラ・サポーターDB。多彩なフィルタで検索。',
    // Twitter画像もopengraph-image.jsで動的生成
  },
  robots: { index: true, follow: true },
  icons: {
    icon: [
      { url: '/favicon.svg', type: 'image/svg+xml' },
      { url: '/favicon-48x48.png', type: 'image/png', sizes: '48x48' },
      { url: '/favicon-192x192.png', type: 'image/png', sizes: '192x192' },
    ],
    apple: [{ url: '/favicon-192x192.png', sizes: '192x192' }],
  },
  other: { 'theme-color': '#0a0e17' },
};

export default function RootLayout({ children }) {
  return (
    <html lang="ja">
      <head>
        {/* Google Analytics */}
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=G-PHTSGSZ19J"
          strategy="afterInteractive"
        />
        <Script id="gtag-init" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-PHTSGSZ19J');
          `}
        </Script>
        {/* 忍者AdMax: クローラー審査用にscriptタグをSSR出力（beforeInteractiveでHTML直書き） */}
        <Script
          src="https://adm.shinobi.jp/s/f969299a5a7ac2147238c6e4c8abd0da"
          strategy="beforeInteractive"
        />
        <Script
          src="https://adm.shinobi.jp/s/986bd62e14794555eb77cbbbe051c274"
          strategy="beforeInteractive"
        />
        <Script
          src="https://adm.shinobi.jp/s/f97fde07eb5842af35cf10b3d4f042dc"
          strategy="beforeInteractive"
        />
        <Script
          src="https://adm.shinobi.jp/s/6b37984cfa9c490a4d625b9fcbbf94f4"
          strategy="beforeInteractive"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
