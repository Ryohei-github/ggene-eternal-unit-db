# GジェネエターナルDB — 開発ガイド

## プロジェクト概要

Gジェネレーション エターナルの全ユニット・キャラクター・サポーターを検索できるデータベースサイト。
詳細な技術仕様は `GGENE_DB_SPEC.md` を参照。

- **本番URL:** https://gget-db.com
- **GitHub:** https://github.com/Ryohei-github/ggene-eternal-unit-db
- **Vercel:** prj_4fNmGCjuBjvPnUkI8EEqNCucUllf / team_KcVgx54lZzv1G748ekkgc9Yv

## デプロイフロー

```
ローカル編集 → git push → GitHub → Vercel自動デプロイ（約30秒〜1分）
```

Desktop Commander MCPのgitコマンドで操作する。ローカルリポジトリは `/Users/RH/Documents/5.File/5.Dev/P_GGeneDB`。
Vercel MCP (`list_deployments` 等) でデプロイ状況を確認可能。

## 主要ファイル一覧

| ファイル | 役割 | 編集頻度 |
|---------|------|---------|
| `public/spa.html` | メインSPA（全UI・ロジック、約7300行） | 高 |
| `public/units.json` | ユニット+キャラ統合データ（約1470件） | 高 |
| `public/characters.json` | キャラ専用データ（68件、SSG/CMS用） | 中 |
| `public/supporters.json` | サポーターデータ（71件） | 中 |
| `public/translations_en.json` | 英語翻訳辞書 | 中 |
| `public/translations_zh-tw.json` | 繁体字中国語翻訳辞書 | 中 |
| `public/items.json` | アイテムデータ | 低 |
| `public/option_parts.json` | オプションパーツデータ | 低 |

## データ構造の要点

### units.json
ユニットとキャラ（`tags` に `キャラ` を含む）が混在する統合ファイル。
主要フィールド: `id`, `name`, `rarity`, `type`, `obtain`, `series`(配列), `tags`(配列), `normal`(stats/terrain/abilities/mechanism), `normal_weapons`, `stats_by_star`, `transformed`, `transformed_weapons`

### characters.json
SPA側のキャラタブで使用するキャラ専用データ。units.jsonのキャラとは別管理。
主要フィールド: `name`, `rarity`, `series`(文字列), `chara_type`, `obtain_method`, `abilities`, `skills`, `stats`(shooting/melee/awakening/defense/reaction/combat_power/mobility)

### supporters.json
主要フィールド: `id`, `name`, `rarity`, `obtain`, `hp`, `attack`, `target_series`, `target_tags`, `recovery_type`(HP/EN/HP・EN/HP&ダメ軽減), `recovery_amount`, `range`, `leader_skill`, `leader_0`〜`leader_3`, `support_skill`, `image`

## spa.html 主要セクション（行番号目安）

行番号はコード変更で前後するため、検索キーワードも併記。

| 機能 | 検索キーワード | 概要 |
|------|--------------|------|
| フィルタHTML | `id="filterSupObtainGroup"` | フィルタボタン群のHTML定義 |
| タブ切替ロジック | `function switchTab` | タブ表示切替 |
| フィルタ表示切替 | `isSupporter ?` | タブに応じたフィルタグループの表示/非表示 |
| サポーターフィルタ | `activeSupObtain` | 入手方法フィルタロジック |
| サポートスキルアイコン | `function supportSkillIcon` | recovery_typeに応じたSVGアイコン |
| カード表示 | `function renderCard` | ユニット/キャラ/サポーターのカード描画 |
| 詳細モーダル | `function showDetail` | 詳細表示モーダル |
| テーブル表示 | `renderTable` | テーブルビュー描画 |
| ダメ計算：攻撃パネル | `function dcRenderAtkPanel` | 攻撃側UI |
| ダメ計算：防御パネル | `function dcRenderDefPanel` | 防御側UI（サポーター選択あり） |
| ダメ計算：計算ロジック | `function dcCalculateDamage` | ダメージ計算式 |
| ダメ計算：ドロップダウン | `function dcFilterDropdown` | ユニット/キャラ/サポーター検索ドロップダウン |
| チーム編成 | `function renderTeamTab` | 編成シミュレーター |
| ティアリスト | `function renderTierList` | ティアリスト機能 |

## 開発ルール

### データ追加時のチェックリスト
1. `units.json` にユニットを追加（IDは既存最大+1から連番）
2. `characters.json` にキャラを追加（IDフィールドなし、name+rarityで識別）
3. `translations_en.json` と `translations_zh-tw.json` に新規シリーズ名・タグの翻訳を追加
4. 画像がある場合は `public/unit-images/` に配置

### タグの表記ルール
- ゲーム内表示に準拠（例: ガンダム → `ガンダム`、『ガンダム』は不可）
- タグの `『』` 括弧は使わない（過去に修正済み）

### フィルタの命名ルール
- 入手方法フィルタのラベル: `恒常ガシャ`, `限定ガシャ`, `イベント報酬`, `Gショップ` 等
- `限定` と `周年限定` は `限定ガシャ` に統一して表示

### フィルタの配置ルール
全タブ共通で `レア → 入手方法 → 専門フィルタ` の順序で統一。

### サポーターのrecovery_type
- `HP`: HP回復のみ
- `EN`: EN回復のみ
- `HP・EN`: HP+EN回復
- `HP&ダメ軽減`: HP回復+ダメージ軽減（スメラギ等）

`HP&ダメ軽減` は独立したフィルタカテゴリ。HP回復フィルタでは引っかからない。

### ダメージ計算機
- 攻撃側・防御側ともにユニット+キャラ+サポーターを選択可能
- サポーターのLS%は `dcGetLeaderPct()` で算出
- 攻撃側: `UnAtk = ユニット攻撃力 * (1 + (unitAtkUp + supAtkPct) / 100) + supFlatAtk`
- 防御側: `UnDef = ユニット防御力 * (1 + (unitDefUp + supDefPct) / 100) + supFlatDef`
- `dcSelectSup(side, id)` で `'atk'` / `'def'` を指定

## データソース

### Wiki（主要参照元）
- **マチュWiki:** `https://wikiwiki.jp/gget/` — ユニット・キャラ・サポーターの詳細データ
  - ユニット個別: `/gget/ユニットリスト/[ユニット名]【[レア]】`
  - パイロット個別: `/gget/パイロットリスト/[キャラ名]【[レア]】`
- **GameWith:** `https://gamewith.jp/ggene-eternal/` — 画像取得元

### 画像取得
- GameWithの画像URLパターン: `https://img.gamewith.jp/article_tools/ggene-eternal/gacha/unit_{N}.png`
- 画像マッチング仕様: `docs/image-matching.md` を参照

## よくある作業パターン

### 新ストーリー追加時
1. Wikiのシリーズページからユニットとキャラのリストを確認
2. `units.json` の既存データと照合して差分を特定
3. 各ユニット個別ページからタイプ・シリーズ・タグ・メカニズムを取得
4. `units.json`, `characters.json` に新規データを追加
5. 翻訳ファイルに新シリーズ・新タグを追加
6. git commit & push → Vercelデプロイ

### フィルタ追加時
1. `spa.html` のフィルタHTML部分にボタングループを追加
2. タブ切替の表示/非表示ロジックに追加
3. `render()` 内のフィルタ適用ロジックに条件を追加

### spa.htmlデバッグ
Chrome拡張のJavaScript実行ツール (`javascript_tool`) で本番サイト上のDOMやデータを直接確認できる。
`allUnits`, `allCharas`, `allSupporters` がグローバル変数として利用可能。

## 環境セットアップ（別PCで作業する場合）

```bash
git clone https://github.com/Ryohei-github/ggene-eternal-unit-db.git
cd ggene-eternal-unit-db
# Coworkでこのフォルダを選択すれば作業開始できる
# 作業前に必ず git pull で最新化
```

クラウドストレージ（iCloud/Dropbox等）での同期は `.git` フォルダとの相性問題があるため非推奨。
GitHubをハブにしてPC間で同期する。
