# GジェネエターナルDB 技術仕様書

**サイト名:** GジェネエターナルDB by MH GAMES
**URL:** https://gget-db.com
**リポジトリ:** https://github.com/Ryohei-github/ggene-eternal-unit-db
**概要:** Gジェネレーション エターナルの全ユニット・キャラクター・サポーターを網羅したデータベースサイト

---

## 1. 技術スタック

| 項目 | 技術 |
|---|---|
| フレームワーク | Next.js 16 (App Router) + Turbopack |
| ホスティング | Vercel |
| データベース | Supabase (CMS用のみ) |
| フロントエンド | Vanilla JS (SPA, ~5900行の単一HTMLファイル) |
| アナリティクス | Google Analytics (G-PHTSGSZ19J) |
| 広告 | 忍者AdMax |
| バージョン管理 | GitHub → Vercel 自動デプロイ |

---

## 2. Vercel プロジェクト情報

| 項目 | 値 |
|---|---|
| プロジェクト名 | mh-dev-gget-db |
| プロジェクトID | prj_4fNmGCjuBjvPnUkI8EEqNCucUllf |
| チームID | team_KcVgx54lZzv1G748ekkgc9Yv |
| 本番ドメイン | gget-db.com |
| エイリアス | mh-dev-gget-db.vercel.app, ggene-eternal-unit-db.vercel.app (両方gget-db.comにリダイレクト) |

### 環境変数 (Vercel)

- `ADMIN_PASSWORD` — CMS管理画面のログインパスワード
- `GITHUB_TOKEN` — CMSからGitHub Contents APIでJSONを更新するためのトークン
- `SUPABASE_URL` — Supabase REST APIのURL
- `SUPABASE_SERVICE_ROLE_KEY` — Supabaseサービスロールキー

---

## 3. ディレクトリ構造

```
ggene-eternal-unit-db/
├── .vercel/project.json          # Vercelプロジェクト設定
├── vercel.json                   # セキュリティヘッダー、リダイレクト設定
├── next.config.mjs               # Next.js設定 (Turbopack有効)
├── package.json                  # 依存: next, react, react-dom (all latest)
│
├── src/                          # Next.js App Router (SSG用)
│   ├── app/
│   │   ├── layout.js             # RootLayout: メタデータ、GA
│   │   ├── page.js               # トップページ: spa.htmlをfetch→DOM注入
│   │   ├── globals.css           # SSG詳細ページ用CSS
│   │   ├── sitemap.js            # 動的サイトマップ生成
│   │   ├── robots.js             # robots.txt生成
│   │   ├── units/[id]/
│   │   │   ├── page.js           # ユニット詳細SSGページ (SEO用)
│   │   │   └── UnitDetailClient.js
│   │   └── charas/[id]/
│   │       └── page.js           # キャラ詳細SSGページ (SEO用)
│   └── lib/
│       └── units.js              # units.jsonの読込・フィルタユーティリティ
│
├── api/                          # Vercel Serverless Functions
│   ├── data.js                   # 公開API: units.json, supporters.json等を配信
│   ├── save.js                   # CMS用: GitHub Contents APIでJSON更新
│   ├── supporters.js             # CMS用: SupabaseのCRUD
│   ├── _lib/auth.js              # 認証ヘルパー (Bearer token + Supabase client)
│   ├── auth.js                   # 認証エンドポイント
│   ├── characters.js             # CMS用キャラCRUD
│   └── units.js                  # CMS用ユニットCRUD
│
├── public/
│   ├── spa.html                  # ★ メインSPA (~5900行, 全機能を内包)
│   ├── units.json                # ★ ユニット+キャラの統合データ (1448件)
│   ├── supporters.json           # ★ サポーターデータ (70件)
│   ├── translations_en.json      # 英語翻訳辞書
│   ├── characters.json           # キャラ専用データ (SSG/CMS用)
│   ├── cms-2228452ce1f04c71.html # CMS管理画面 (noindex)
│   ├── favicon.svg               # ファビコン
│   ├── ads.txt                   # 忍者AdMax ads.txt
│   ├── assets/
│   │   ├── ogp.png               # OGP画像
│   │   ├── type_icons/           # タイプアイコン (攻撃/支援/耐久)
│   │   ├── weapon_icons/         # 武装アイコン
│   │   ├── ui_elements/          # UI素材
│   │   └── map_weapon/           # 武装マップ画像
│   └── unit-images/              # ユニット・キャラ・サポーター画像 (1166枚)
│       ├── mh-games-unit-{N}.png       # ユニット画像
│       ├── mh-games-chara-{N}.png      # キャラ画像
│       └── mh-games-supporter-{N}.png  # サポーター画像
```

---

## 4. アーキテクチャ概要

### 二層構造

1. **Next.js App Router (SSG)** — SEOクローラー向け
   - `/units/{id}`, `/charas/{id}` はビルド時にSSG (Static Site Generation)
   - `generateStaticParams` で全ユニット・キャラのページを静的生成
   - メタデータ、OGP、JSON-LD構造化データを各ページに付与
   - サイトマップ (`/sitemap.xml`) も動的生成

2. **SPA (spa.html)** — ユーザー向けメインUI
   - トップページ (`page.js`) が `/spa.html` をfetchし、DOMに注入して実行
   - 全UI・検索・フィルタ・比較・ティアリストなどの機能を単一HTMLに内包
   - Vanilla JS (ライブラリ不使用)、CSS-in-HTML

### データフロー

```
[ブラウザ] → page.js → fetch('/spa.html') → DOM注入
                      → fetch('/api/data?type=units') → units.json
                      → fetch('/api/data?type=supporters') → supporters.json
```

---

## 5. データ仕様

### 5.1 units.json (ユニット+キャラ統合ファイル)

1448件の配列。ユニット(987件)とキャラ(461件)が混在。`tags`に`キャラ`を含むかで区別。

#### ユニット構造

```json
{
  "id": 1,
  "name": "ガンダム試作3号機(EX)",
  "image": "/unit-images/mh-games-unit-1.png",
  "rarity": "UR",              // UR, ULT, SSR, SR, R, N
  "type": "攻撃",              // 攻撃, 支援, 耐久
  "obtain": "シロー・アマダ",   // 獲得キャラクター名 (キャラとの紐付け)
  "acquire": "ガシャ",          // 入手方法: ガシャ, 開発, イベント
  "series": ["機動戦士ガンダム0083 STARDUST MEMORY"],
  "tags": ["エース機", "試作機", ...],
  "normal": {
    "combat_power": 12345,
    "mechanism": "可変",        // 機構: 可変, 換装, 合体 等
    "terrain": { "宇宙": "◎", "空中": "◯", "地上": "△", "水中": "×" },
    "stats": { "hp": 5000, "en": 300, "attack": 450, "defense": 350, "mobility": 80, "agility": 400 },
    "abilities": [{ "name": "...", "desc": "..." }]
  },
  "normal_weapons": [
    { "name": "ビームサーベル", "attribute": "ビーム", "weapon_type": "格闘",
      "range": "1", "power": "3200", "en": "20", "hit": "85%", "critical": "8%", "effect": "..." }
  ],
  "stats_by_star": [
    { "star": 0, "lv": 1, "hp": 3000, "en": 200, "attack": 300, "defense": 200, "mobility": 70, "agility": 300 },
    { "star": 1, "lv": 20, ... },
    { "star": 2, "lv": 30, ... },
    { "star": 3, "lv": 40, ... }
  ],
  "transformed": {              // 変形後データ (79ユニットのみ)
    "stats": { ... },
    "terrain": { ... },
    "stats_by_star": [...]
  },
  "transformed_weapons": [...]
}
```

#### キャラクター構造

```json
{
  "id": 343,
  "name": "シン・アスカ(攻撃)",
  "image": "/unit-images/mh-games-chara-343.png",
  "rarity": "UR",              // UR, SSR, SR, R
  "type": "攻撃",              // 攻撃, 支援, 耐久
  "obtain": "",
  "acquire": "ガシャ",          // ガシャ, スカウト, イベント, 配布
  "series": ["機動戦士ガンダムSEED DESTINY"],
  "tags": ["キャラ", "主人公", "コーディネイター", ...],
  "normal": {
    "combat_power": 8000,
    "stats": { "shooting": 500, "melee": 600, "awakening": 400, "defense": 350, "reaction": 450, "sp": 100 },
    "skills": [{ "name": "...", "effect": "...", "sp_cost": 30 }],
    "abilities": [{ "name": "...", "desc": "...", "condition": "..." }]
  },
  "sp_stats": { "shooting": 600, ... },        // SP化後ステータス (非URのみ, 399件)
  "sp_skills": [{ "name": "...", ... }],        // SP化後スキル (305件)
  "sp_abilities": [{ "name": "...", ... }],     // SP化後アビリティ (32件)
  "lv100_stats": { "shooting": 700, ... }       // Lv100参考値 (URのみ, 62件)
}
```

#### データ件数

| 区分 | UR | ULT | SSR | SR | R | N | 計 |
|---|---|---|---|---|---|---|---|
| ユニット | 96 | 12 | 282 | 279 | 279 | 39 | 987 |
| キャラ | 62 | - | 94 | 255 | 50 | - | 461 |

| キャラ入手方法 | 件数 |
|---|---|
| スカウト | 304 |
| ガシャ | 111 |
| イベント | 31 |
| 配布 | 15 |

### 5.2 supporters.json (サポーターデータ)

70件の配列。

```json
{
  "name": "ブライト・ノア＆ホワイトベース",
  "rarity": "UR",              // UR(37), SSR(27), SR(6)
  "obtain": "ガシャ",
  "hp": 2800,
  "attack": 420,
  "target_series": "機動戦士ガンダム",
  "recovery_type": "HP",       // HP or EN
  "recovery_amount": "40%",
  "range": "1-4マス",
  "leader_effect": "...",
  "leader_0": "...",            // リーダースキル段階別
  "leader_1": "...",
  "leader_2": "...",
  "leader_3": "...",
  "leader_skill": "...",
  "support_skill": "...",
  "image": "/unit-images/mh-games-supporter-1.png"
}
```

### 5.3 translations_en.json (英語翻訳)

キー=日本語テキスト、値=英語翻訳。カテゴリ別に`_general`, `_series`, `_type`, `_terrain`, `_mechanism`, `_tags`をキーに持つ。

### 5.4 画像ファイル命名規則

| 種別 | パターン | 例 |
|---|---|---|
| ユニット | `/unit-images/mh-games-unit-{N}.png` | mh-games-unit-1.png |
| キャラ | `/unit-images/mh-games-chara-{N}.png` | mh-games-chara-343.png |
| サポーター | `/unit-images/mh-games-supporter-{N}.png` | mh-games-supporter-1.png |
| 外部参照 (一部キャラ) | `https://img.gamewith.jp/article_tools/ggene-eternal/gacha/chara_{N}.png` | — |

**注意:** 一部キャラ画像はGameWith CDNを直接参照しているものがある (ローカル画像がない場合の代替)。

---

## 6. SPA (spa.html) 主要機能

### 6.1 タブ構成

| タブ | 変数名 | 説明 |
|---|---|---|
| ユニット | `unit` | ユニット一覧・検索・フィルタ |
| キャラ | `chara` | キャラクター一覧・検索・フィルタ |
| サポーター | `supporter` | サポーター一覧 |
| タグ検索 | `taglookup` | タグ別ユニット/キャラ逆引き |
| 編成 | `team` | チーム編成シミュレーター |
| ランキング | `ranking` | ステータスランキング |
| ティア | `tierlist` | ティアリスト (ドラッグ&ドロップ) |
| ダメ計算 | `dmgcalc` | ダメージ計算機 |

### 6.2 フィルタ・検索機能

#### ユニットフィルタ
- テキスト検索 (名前)
- レアリティ: UR, ULT, SSR, SR, R, N
- タイプ: 攻撃, 耐久, 支援
- シリーズ (セレクトボックス, 複数選択可)
- タグ (セレクトボックス, 最大3個まで追加可)
- 入手方法: ガシャ, 限定ガシャ, 開発, イベント
- デバフ効果フィルタ (攻撃低下, 防御低下, 等)
- 特殊効果フィルタ (一撃必殺, 電光石火, 等)

#### キャラフィルタ
- テキスト検索
- レアリティ: UR, SSR, SR, R
- タイプ: 攻撃, 支援, 耐久
- シリーズ、タグ
- 入手方法: ガシャ, 限定ガシャ, スカウト, イベント, 配布

#### ソート
- ユニット: HP, EN, 攻撃, 防御, 機動, 運動, 戦闘力, 名前順
- キャラ: 射撃, 格闘, 覚醒, 守備, 反応, SP, 戦闘力, 名前順
- サポーター: HP, 攻撃力, 名前順

### 6.3 限定ユニット/キャラ判定

#### 限定URユニット (17体, ハードコード)

```javascript
const _limitedURNames = new Set([
  "ガンダムAGE-2 ノーマル(EX)", "ガンダムアストレイ レッドフレーム改(EX)",
  "ガンダムDX(EX)", "ガンダム・キャリバーン(最終決戦時)(EX)",
  "デスティニーガンダム(EX)", "Ξガンダム(EX)",
  "ガンダム・バルバトスルプスレクス(EX)", "ガンダム試作3号機(EX)",
  "ユニコーンガンダム(デストロイモード／覚醒)(EX)", "ゴッドガンダム(EX)",
  "キュベレイ(ZZ版)(EX)", "モンスターブラックドラゴン(EX)",
  "バンシィ・ノルン(デストロイモード)(EX)", "Hi-νガンダム(EX)",
  "ガンダム試作2号機(EX)", "Zガンダム(EX)", "ストライクフリーダムガンダム(EX)"
]);
```

#### 限定キャラ判定ロジック

1. `_limitedURNames`に名前が一致するユニットに`limited = true`を付与
2. 限定ユニットの`obtain`フィールドからキャラ名を収集 → `_limitedCharaNames`セットへ
3. `obtain`が空の限定ユニット(モンスターブラックドラゴン等)は同名キャラを名前マッチ
4. キャラデータ構築時に`_limitedCharaNames.has(name) && acquire === 'ガシャ'`で`limited`フラグ付与

**重要ルール:** ユニットのタイプとキャラのタイプは必ず一致する (攻撃↔攻撃, 支援↔支援, 耐久↔耐久)。

### 6.4 表示モード

- **カードビュー** (グリッド表示, デフォルト)
- **テーブルビュー** (一覧表形式)

### 6.5 比較機能

- ユニット/キャラを最大5体まで選択して比較
- レーダーチャート (Canvas描画) でステータス比較
- 限界突破(★)段階別ステータス比較対応

### 6.6 チーム編成シミュレーター

- 6スロット (ユニット+キャラ×6) + サポーター1
- リーダースキルのマッチ判定
- チームステータス合計表示
- 保存/読込 (localStorage)
- URL共有 & 画像出力 (Canvas→PNG)

### 6.7 ティアリスト

- SS/S/A/B/Cのティア分類
- ドラッグ&ドロップでユニット/キャラ/サポーターを配置
- localStorage保存
- 画像出力機能

### 6.8 ダメージ計算機

- 攻撃側: ユニット(★段階選択可) + キャラ + サポーター + 武装選択
- 防御側: ユニット(★段階選択可) + 地形
- バフ/デバフ自動検出 (アビリティから)
- ダメージ計算結果表示

### 6.9 多言語対応

- 日本語 (デフォルト) / 英語 切替
- `translations_en.json`から翻訳辞書をロード
- カテゴリ別翻訳: general, series, type, terrain, mechanism, tags
- `t()` / `tData()` / `tType()` 等の関数で動的変換

---

## 7. API仕様

### 7.1 公開API (`/api/data`)

**認証不要 (オリジン制限あり)**

| パラメータ | ファイル |
|---|---|
| `?type=units` | public/units.json |
| `?type=supporters` | public/supporters.json |
| `?type=translations` | public/translations_en.json |
| `?type=characters` | public/characters.json |

セキュリティ:
- オリジン/リファラーチェック: `gget-db.com` / `www.gget-db.com` のみ許可
- Bot UA検出 (curl, wget, python等をブロック)
- レートリミット: 30リクエスト/分/IP
- キャッシュ: `s-maxage=300, stale-while-revalidate=600`

### 7.2 CMS API (認証必要)

- `/api/save` — GitHub Contents APIを通じてJSONファイルを更新 (POST)
- `/api/supporters` — Supabase経由のサポーターCRUD
- `/api/units` — ユニットCRUD
- `/api/characters` — キャラCRUD

認証: `Authorization: Bearer {base64(password:timestamp)}`、24時間有効

### 7.3 CMS管理画面

- URL: `https://gget-db.com/cms-2228452ce1f04c71.html` (URLにハッシュを含むことで推測困難に)
- パスワード認証
- noindex設定済
- Supabase + GitHub APIでデータを管理

---

## 8. SEO対策

### SSGページ

- `/units/{id}` — 全987ユニットの詳細ページを静的生成
- `/charas/{id}` — 全461キャラの詳細ページを静的生成
- 各ページにOpenGraph、Twitter Card、JSON-LD構造化データ付与

### vercel.json リダイレクト

- `ggene-eternal-unit-db.vercel.app/*` → `gget-db.com/*` (301)
- `mh-dev-gget-db.vercel.app/*` → `gget-db.com/*` (301)
- `/units.json`, `/supporters.json`, `/characters.json`, `/translations_en.json` への直アクセス → `/` にリダイレクト (データ保護)

### robots.txt

- Allow: `/`
- Disallow: `/api/`, `/unit-images/`

---

## 9. デプロイフロー

```
[ローカル修正] → git push → GitHub (main) → Vercel 自動デプロイ → gget-db.com
```

- デプロイはGitHub mainブランチへのpushで自動トリガー
- Vercelが検知→ビルド→デプロイ→本番エイリアス自動割当
- ビルド: `next build` (Turbopack)
- SSGページはビルド時に全ページ生成

### CMS経由のデータ更新フロー

```
[CMS管理画面] → /api/save → GitHub Contents API → mainブランチcommit → Vercel自動デプロイ
```

---

## 10. 既知の技術的制約・注意点

### データ取得元

- ユニット/キャラデータは主にGameWith (gamewith.jp) とwikiwiki.jpからスクレイピング
- スクレイプスクリプト (`*.py`) は `.gitignore` に含まれているがリポジトリに残存
- `scrape_chunks/`, `dynamic_chunks/` はスクレイピング時の中間ファイル

### 画像について

- 画像命名規則は `mh-games-` プレフィックスに統一済
- **注意:** JSONファイル内の画像パスがリネーム時に更新漏れになりやすい (過去にサポーター画像消失の原因になった)
- 一部キャラ画像はGameWith CDN (`img.gamewith.jp`) を外部参照
- Coworkのサンドボックス環境からは外部画像を直接ダウンロード不可 (ネットワーク制限あり)
- 画像取得が必要な場合は、GameWith CDN URLをJSONに直接記載して外部参照するか、Chrome経由で手動取得

### 限定ユニットリスト

- `_limitedURNames` はSPA内にハードコード
- 新しい限定URユニットが追加された場合は手動でリストに追加が必要

### ユニット⇔キャラの紐付け

- ユニットの `obtain` フィールドにキャラ名が入っている (例: `"シン・アスカ(攻撃)"`)
- `【UR】` プレフィックスが付く場合があり、replace で除去が必要
- **タイプ一致ルール:** ユニットのタイプとキャラのタイプは必ず一致 (攻撃↔攻撃)

### データパッチ

- SPA内にベギルペンデの武装データ補完パッチがハードコードされている (line 1430)
- 今後もデータ欠損が見つかった場合は同様のパッチ追記が必要になる可能性あり

---

## 11. 主要関数リファレンス (spa.html)

| 関数名 | 行番号(目安) | 機能 |
|---|---|---|
| `init()` | 1424 | 初期化: データ読込・限定判定・フィルタ構築 |
| `buildFilters()` | 1697 | フィルタUI構築 |
| `getFiltered()` | 1948 | フィルタ適用後のデータ取得 |
| `sortItems()` | 2096 | ソート処理 |
| `render()` | 2151 | メイン描画 |
| `unitCardHTML()` | 2331 | ユニットカード生成 |
| `charaCardHTML()` | 2387 | キャラカード生成 |
| `supporterCardHTML()` | 2501 | サポーターカード生成 |
| `showUnitDetail()` | 2623 | ユニット詳細モーダル表示 |
| `showCharaDetail()` | 2865 | キャラ詳細モーダル表示 |
| `showSupporterDetail()` | 2996 | サポーター詳細モーダル表示 |
| `renderTeamSim()` | 3288 | チーム編成シミュレーター描画 |
| `renderRanking()` | 5069 | ランキング描画 |
| `renderTierList()` | 5200 | ティアリスト描画 |
| `renderDmgCalc()` | 5406 | ダメージ計算機描画 |
| `dcCalculateDamage()` | 5773 | ダメージ計算実行 |
| `syncURL()` | 4244 | URLステート同期 |
| `restoreFromURL()` | 4310 | URLからステート復元 |
| `shareTeamImage()` | 3781 | チーム編成画像出力 |

---

## 12. よく行う作業の手順

### データ更新 (units.json直接編集)

1. `public/units.json` を編集
2. `git add public/units.json && git commit -m "..." && git push`
3. Vercelが自動デプロイ (約1-2分)

### 新しい限定URユニットの追加

1. `spa.html` の `_limitedURNames` Set にユニット名を追加
2. units.jsonに該当ユニットデータが含まれていることを確認
3. ユニットの`obtain`フィールドが正しいキャラ名を指していることを確認
4. commit & push

### 画像の追加・修正

1. 画像ファイルを `public/unit-images/mh-games-{種別}-{N}.png` として配置
2. 対応するJSONファイル内の`image`フィールドを更新
3. **必ずJSONの画像パスと実ファイル名が一致していることを確認**

### フィルタ条件の追加

- ユニットフィルタ: `buildFilters()` (line 1697) と `getFiltered()` (line 1948)
- キャラフィルタ: 同関数内のキャラセクション
- ソート: `sortItems()` (line 2096)

---

*最終更新: 2026-03-22*
