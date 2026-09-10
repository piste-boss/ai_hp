# SEO / MEO / AIO 施策 実施ログ（2026年9月10日）

対象: https://www.piste-ai.com/（Netlify プロジェクト piste-ai）
分析レポート: `20260910_seo_analysis_report.md`

## 追加したツール（今後の運用はこの2本で回す）

| ファイル | 役割 |
|---|---|
| `tools/optimize_images.py` | `site/images/` の画像から WebP（記事 1200px / カード 640px / アイコン 160px 等）と OGP 用 JPG を生成。冪等。`--force` で全再生成 |
| `tools/seo_build.py` | 記事 head の正規化（GA4・Clarity・短縮 title・canonical・OGP・Twitter・JSON-LD・RSS）、本文へのパンくず／公開日／著者／要点／関連記事の挿入、画像の WebP 差し替え、ブログ一覧のカテゴリナビ、カテゴリページ、sitemap.xml / feed.xml / llms.txt の生成。冪等 |

`/sync-blog` スキル（`~/.claude/commands/ai-hp-blog.md`）に **Step 6.5** として組み込み済み。
新記事公開時は Step 5（ブログ一覧更新）の後・Step 7（デプロイ）の前に必ず実行する。

```bash
cd /Users/ishikawasuguru/AI_コンサル/HP作成 && python3 tools/optimize_images.py && python3 tools/seo_build.py
```

## 実施内容

### 緊急施策（すべて完了・本番反映済み）

| # | 施策 | 結果 |
|---|---|---|
| 1 | サイトマップ再生成 | 16 URL → **170 URL**（記事155 + カテゴリ6 + 固定ページ）。`feed.xml`（最新30件の RSS）も新設 |
| 2 | GA4 / Clarity タグ | 18記事 → **155記事すべて**に設置 |
| 3 | canonical / OGP / 構造化データ | 155記事すべてに canonical（`.html` 付きに統一）、OGP（記事ごとの生成画像を 1200px JPG で）、Twitter Card、JSON-LD を設置 |
| 4 | Search Console | ※要ログイン（下記「石川さんにお願いしたい作業」） |
| 5 | Bing Webmaster | ※要ログイン |
| 6 | `llms.txt` | 設置。会社概要・料金・カテゴリ別の全記事一覧（要約付き） |
| 7 | training.html の H1 重複 | 2つ目を H2 に変更。トップの構造化データに address / sameAs / founder / OfferCatalog を追加 |

### 短期施策（完了）

| # | 施策 | 結果 |
|---|---|---|
| 8 | 画像最適化 | WebP 676 ファイル生成。トップページのアイコン 400KB → 14KB、プロフィール 2.4MB → 29KB、記事画像 2〜3MB → 30〜60KB。全 img に width / height 付与 |
| 9 | Google Fonts | 8ウェイト → 5ウェイト。style.css 使用ページは `display=optional`（フォント読み込みによるレイアウトシフト防止） |
| 10 | 短縮 title | 155記事すべてに全角33文字以内の検索用 title を設定（H1 は元のまま）。手動指定は `TITLE_OVERRIDES` |
| 11 | 記事テンプレート | パンくず・公開日・著者リンク・「この記事でわかること」（H2 から3点）・関連記事3本（同カテゴリ優先）を全記事に挿入 |
| 12 | カテゴリ | 6カテゴリ（ツール連携 87 / Claude Codeの使い方 24 / 業務記録・現場改善 15 / 経理・財務・資金 14 / 営業・顧客対応 11 / AI導入の基礎 4）。一覧ページにナビ、`blog/category-*.html` を生成 |
| 13 | 404 / リダイレクト | カスタム 404 ページ（noindex）を設置。http → https → www の2段リダイレクトは Netlify 側の仕様のため未変更 |

### 中長期施策（今回着手した分）

| # | 施策 | 結果 |
|---|---|---|
| 14 | 著者ページ | `about.html` 新設。ProfilePage + Person スキーマ。全記事の `author` と `article:author` から参照 |
| 15 | サービス詳細ページ | `claude-code-support.html` 新設。Service + Offer + FAQPage スキーマ |
| 17 | 地域ランディング | `aichi.html` 新設。対応エリア（碧南・安城・刈谷・知立・高浜・西尾・岡崎・半田・名古屋）を areaServed に記載。フッターに住所を掲載 |
| 19 | 色コントラスト | 明るい背景上の金色文字を濃い金色（#7f6122）へ。トップページの不合格 46 → 2 |
| — | robots.txt | GPTBot / OAI-SearchBot / ClaudeBot / PerplexityBot / Google-Extended / Bingbot を明示的に許可、llms.txt を案内 |
| — | `_headers` | 画像・CSS・JS に 1週間のキャッシュ、llms.txt / feed.xml の Content-Type を指定 |
| — | トップページ LCP | ヒーロー文言の `fade-in`（JS 実行までopacity 0）を外し、初期表示で描画されるように変更 |

### 未着手（今回の範囲外・要判断）

- **#16 事例・お客様の声ページ** — 実在のお客様の声が手元にないため作成していない（捏造しない）
- **#18 GA4 / Search Console API の自動レポート** — OAuth 認証が必要
- ~~電話番号~~ → 090-9948-0878 をフッター・代表プロフィール・地域ページ・全ページの JSON-LD（telephone）に掲載（同日追記）
- ~~SNS URL~~ → X（@piste_ai_boss）・Instagram（@piste_ai）・Threads（@piste_ai）を sameAs とフッターに追加（同日追記）
- Search Console の HTML タグ確認メタをトップページに設置（同日追記）

## AI 向け構造化データの設計（ご質問への回答）

「AI 用の観点で構造化データを出さなくていいのか」→ **必要**。Google の公式見解は「AI Overviews 専用のマークアップはなく、通常の構造化データがそのまま使われる」であり、
ChatGPT search / Perplexity / Copilot も JSON-LD をエンティティ理解と出典判定に使う。今回は以下を全ページに出力した。

| ページ | 出力する型 | 狙い |
|---|---|---|
| 全ページ共通 | `Organization`+`ProfessionalService`（住所・sameAs・founder・knowsAbout）、`Person`（著者。alumniOf・worksFor・knowsAbout）、`WebSite` | 「誰が・どの会社が・何の専門で」書いているかを @id で相互参照させ、AI がエンティティとして認識できるようにする |
| トップ | `WebPage`、`OfferCatalog`（各サービスと価格） | 料金の質問に AI が正確に答えられるようにする |
| 記事 | `BlogPosting`（headline・alternativeHeadline・datePublished・dateModified・articleSection・keywords・wordCount・about=Claude Code/Anthropic）、`BreadcrumbList`、`FAQPage`（101記事） | 鮮度・トピック・FAQ を機械可読にし、引用されやすくする |
| カテゴリ / 一覧 | `CollectionPage` + `BreadcrumbList` | サイトの専門領域（トピッククラスタ）を示す |
| 研修 | `Course` + `CourseInstance` | 研修プログラムとしての認識 |
| Claude Code 導入サポート | `Service` + `Offer` + `FAQPage` | サービス・価格・FAQ |
| 代表プロフィール | `ProfilePage` + `Person` | 著者の権威性（E-E-A-T） |
| 地域ページ | `ProfessionalService`（areaServed に市区町村） | ローカル検索・MEO |

補完する非スキーマ要素: `llms.txt`、RSS、本文中の公開日・著者・「この記事でわかること」、AI クローラーを明示許可した robots.txt。

## 石川さんにお願いしたい作業（ログインが必要なもの）

1. **Search Console**（https://search.google.com/search-console）
   - プロパティ `piste-ai.com`（DNS 認証済みのドメインプロパティ）を開く
   - 「サイトマップ」→ `https://www.piste-ai.com/sitemap.xml` を追加（送信済みなら再送信）
   - 「設定」→「関連付け」→ GA4 プロパティ 531067300 とリンク
   - 「URL 検査」で `https://www.piste-ai.com/` と `https://www.piste-ai.com/blog/` のインデックス登録をリクエスト
2. **Bing Webmaster Tools**（https://www.bing.com/webmasters）
   - 「Google Search Console からインポート」でサイトを追加（数分で完了）
   - サイトマップ `https://www.piste-ai.com/sitemap.xml` を送信
3. **Netlify**（任意）: Site configuration → Build & deploy → Post processing → 「Pretty URLs」を無効にすると `.html` なし URL の重複が解消される（現状は canonical で対処済み）
4. **GA4 数値の共有**: レポート用スプレッドシート `18iefSBHkun3S9fREw0bR98H4RquG7v_sLE5_q3F9uAU` を boss112030@gmail.com に閲覧共有していただければ、次回から数値分析まで自動化できます
5. **SNS URL**: X / Threads / Instagram / YouTube の公式アカウント URL があればお知らせください（`sameAs` に追加）

## 計測結果（Lighthouse モバイル・本番）

| 指標 | 施策前（9/10 朝） | 施策後（9/10 昼・3回計測） |
|---|---|---|
| トップ Performance（モバイル） | 53 | 43 / 71 / 91（ブレあり） |
| トップ LCP（モバイル） | 11.6 s | 2.7〜6.6 s |
| トップ CLS（モバイル） | 0.239 | 0 / 0 / 0.756（3回中1回） |
| トップ Performance（デスクトップ） | 57 | 93 |
| トップ LCP / CLS（デスクトップ） | 3.3 s / 0.177 | 1.2 s / 0 |
| ページ総重量（トップ） | 2.6MB | 1.3MB |
| 色コントラスト不合格（トップ） | 46 | 2 |
| 記事ページ Performance / CLS | — | 67〜71 / 0.004 |
| 記事ページ アクセシビリティ | — | 100 |

残課題: モバイルの Lighthouse で3回に1回、初回描画直後に全体が動く（CLS 0.75）ケースが残る。
実ブラウザ（Playwright）での計測では CLS 0 で再現しないため、スロットリング環境特有の現象と見ている。
正式な評価は Search Console の「ウェブに関する主な指標」（実ユーザーデータ）で1〜2か月後に確認する。

副産物として、トップページのフォント読み込み属性に含まれていた構文エラー（`\'` の混入）を発見・修正した。

## ロールバック

デプロイ前の HTML バックアップ: セッションのスクラッチ領域（`site_backup/`）に保存。
Netlify 側でも「Deploys」から前回デプロイ（`6aa1d514...`）へワンクリックで戻せる。
