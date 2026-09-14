# HP作成（piste-ai.com）プロジェクトルール

対象サイト: <https://www.piste-ai.com/>（Piste AI EVANGELISTS / 株式会社Piste）
静的HTMLサイト。WordPressではない。Netlify でホスティング。

| 項目 | 値 |
|---|---|
| Netlify site ID | `22906075-c680-4d7e-b48b-ceb78d987037`（サイト名 piste-ai） |
| 本番デプロイ | **`site/` から直接デプロイしない。** `python3 tools/seo_build.py` → `python3 tools/release_build.py` → `python3 tools/verify_release.py` → `cd site && netlify deploy --prod --no-build --dir=../audit/20260910/release/public --functions=netlify/functions --site=22906075-c680-4d7e-b48b-ceb78d987037`（詳細: `.Codex/commands/seo-publish.md`） |
| GA4 測定ID | `G-LR35246V7B`（プロパティ 531067300） |
| Microsoft Clarity ID | `w54yutjekb` |
| Search Console | ドメインプロパティ `sc-domain:piste-ai.com`（DNS TXT 認証済み） |
| 編集ディレクトリ | `site/`（ブログは `site/blog/`、画像は `site/images/`）。ここは**ソース**であり、公開物は `tools/release_build.py` が `audit/20260910/release/public` に生成する |
| ブログソース | `ブログ/`（HTML）、`ブログ/ココナラ用/`（MD原稿） |
| 同期スキル | `/sync-blog`（本体: `~/.claude/commands/ai-hp-blog.md`） |
| 著者 | 石川 卓（AIコンサルタント）。表記は漢字で統一 |

---

## 2026-09-10 SEO/MEO/AIO 診断の要点（ブログ運用に直結する部分）

- 診断レポート（アーティファクト）: <https://claude.ai/code/artifact/b24183ce-2387-48ea-86ec-97702c2db064>
- Markdown 版: `20260910_seo_analysis_report.md`
- 機械判定の結果: `audit/20260910/summary.json`（`missing_ga` / `missing_clarity` / `missing_canonical` / `missing_from_sitemap` に該当URLの一覧）
- 派生タスク: `20260910_blog_seo_actions.md` / `20260910_site_seo_tasks.md` / `20260910_seo_schedule.md` / `20260910_google_business_actions.md`

**結論**: コンテンツ生産（155記事・ほぼ毎日更新）は良好。一方、4月以降に自動化した `/sync-blog` の公開フローに
SEOの後処理が組み込まれていないため、**新しい記事ほど検索エンジンにも GA4 にも見えていない**。

| 領域 | 状態（2026-09-10時点） |
|---|---|
| sitemap.xml | 16 URL のみ。lastmod 2026-04-12 で停止。145ページ未登録 |
| RSS/feed.xml | 存在しない（/feed.xml, /rss.xml とも404） |
| GA4 / Clarity | 記事 155 中 18 にしか設置なし（137記事が未計測） |
| canonical | 137記事に未設置。Netlify のプリティURLで `/blog/x.html` と `/blog/x` の両方が200 |
| OGP | 134記事に未設置（生成済みサムネがあるのに使われていない） |
| Article スキーマ / 公開日 | 142記事に未設置。HTML上に日付がない |
| title | 全記事 45〜68 文字で検索結果で途切れる |
| Bing | 未登録（ChatGPT search / Copilot の入口が閉じている） |
| 画像 | 記事画像はほぼ全て 2MB 超。WebP 未使用。width/height なし |
| モバイル速度 | Lighthouse 53、LCP 11.6s、CLS 0.239 |
| MEO | 住所・地域名の記載ゼロ。構造化データに address/geo なし |

4月の診断（`blog.md`, `20260411_seo_analysis_report.md`）で指摘済みだった canonical / GA4 / OGP / Article スキーマ /
サイトマップは、いずれも **4月12日以前の記事にしか適用されておらず、以降の記事は未対応**。
`blog.md` の記述と本ファイルが矛盾する場合は本ファイルを優先する。

---

## ブログ記事の公開ルール（必須）

以下は **新規記事を `site/blog/` に置く時点で必ず満たす**。`/sync-blog` 実行時も、手作業で追加する時も同じ。
ソース側 `ブログ/*.html` にもタグは入っていないので、**site 側にコピーした後に必ず head を補完する**。

### 1. `<head>` 必須テンプレート

**このテンプレートを手で書かない。** `tools/seo_build.py` が全記事に生成する（冪等）。以下は生成される内容の仕様として残す。
`{slug}` はファイル名（拡張子なし）、日付は `YYYY-MM-DD`。

**計測タグの注意（2026-09-10）**: GA4・Clarity は `/js/analytics.js` に集約されている。`site/` の記事には seo_build.py が直書き gtag を入れるが、`release_build.py`（measurement_build）が公開時に直書きを除去して analytics.js だけにする。`site/` を直接デプロイすると**両方が読み込まれ二重計測になる**。

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-LR35246V7B"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-LR35246V7B');
</script>
<!-- Microsoft Clarity -->
<script type="text/javascript">
  (function(c,l,a,r,i,t,y){
    c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
    t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
    y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
  })(window, document, "clarity", "script", "w54yutjekb");
</script>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" type="image/png" href="/favicon.png">
<title>{検索向け短縮タイトル 30〜35文字}</title>
<meta name="description" content="{80〜120文字}">
<meta name="keywords" content="{5〜8個}">
<link rel="canonical" href="https://www.piste-ai.com/blog/{slug}.html">
<meta property="og:title" content="{検索向け短縮タイトル}">
<meta property="og:description" content="{description と同じでよい}">
<meta property="og:type" content="article">
<meta property="og:url" content="https://www.piste-ai.com/blog/{slug}.html">
<meta property="og:image" content="https://www.piste-ai.com/images/blog-{slug}.jpg">
<meta property="og:site_name" content="Piste AI EVANGELISTS">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{検索向け短縮タイトル}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="https://www.piste-ai.com/images/blog-{slug}.jpg">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{H1 と同じ記事タイトル}",
  "description": "{description}",
  "author": { "@type": "Person", "name": "石川 卓", "jobTitle": "AIコンサルタント", "url": "https://www.piste-ai.com/about/" },
  "publisher": {
    "@type": "Organization",
    "name": "Piste AI EVANGELISTS",
    "logo": { "@type": "ImageObject", "url": "https://www.piste-ai.com/images/logo.png" }
  },
  "datePublished": "{YYYY-MM-DD}",
  "dateModified": "{YYYY-MM-DD}",
  "image": "https://www.piste-ai.com/images/blog-{slug}.jpg",
  "mainEntityOfPage": "https://www.piste-ai.com/blog/{slug}.html"
}
</script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    { "@type": "Question", "name": "{FAQの質問1}", "acceptedAnswer": { "@type": "Answer", "text": "{回答1}" } }
  ]
}
</script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "ホーム", "item": "https://www.piste-ai.com/" },
    { "@type": "ListItem", "position": 2, "name": "ブログ", "item": "https://www.piste-ai.com/blog/" },
    { "@type": "ListItem", "position": 3, "name": "{記事タイトル}", "item": "https://www.piste-ai.com/blog/{slug}.html" }
  ]
}
</script>
```

補足:

- **title と H1 は分ける**。H1 は現状の長いタイトルのままでよい。`<title>` は 30〜35 文字の検索向け短縮版にする
  （例: `Claude Codeで外注先の依頼記録を整える｜中小企業向け`）。`| Piste AI EVANGELISTS` の接尾辞は文字数を圧迫するので付けない。
- FAQPage の `mainEntity` には記事末尾の FAQ セクションの Q/A を**そのまま**入れる（本文と一致させる）。
- 著者ページは `about.html`（公開URL `/about`）。Person の `@id` は `https://www.piste-ai.com/about.html#person`（release_build が拡張子なしに変換）。全記事の `author` はこの `@id` を参照する（設置済み）。
- 記事末尾の FAQ は `<h2>N. よくある質問</h2>` の下に `<h3>質問</h3><p>回答</p>` か `<div class="faq-item"><p class="q">…</p><p class="a">…</p></div>` のどちらかで書く。seo_build.py が両形式から FAQPage を生成する。
- 「この記事でわかること」欄は現状 H2 の先頭3項目のコピー。AIO 上は「対象者・得られる成果・必要条件」の3行にすべきで、seo_build.py の `keypoints_block` 改修が未着手（`20260910_aio_guide.html` 8章）。
- 既存137記事へ一括適用する場合、`datePublished` は `site/blog/index.html` のカード内 `<p class="blog-date">YYYY.MM.DD</p>` から復元する。
  `dateModified` は実質的な内容変更のときだけ更新する（タグ追加だけでは更新しない）。

### 2. URL の統一（2026-09-10 改定）

- 正規URLは **拡張子なし**（`https://www.piste-ai.com/blog/{slug}`）。旧 `.html` URL と `index.html` は `site/_redirects` で 301。
- `site/` 内のHTMLは `.html` 付きのまま書いてよい。canonical・OGP・JSON-LD の @id・内部リンク・サイトマップ・feed・llms.txt を拡張子なしに揃えるのは `tools/release_build.py` の仕事。**`site/` を直接デプロイすると canonical がリダイレクト先を指す不整合になる**（2026-09-10 14:56 のデプロイで実際に発生）。
- ホスト名は必ず `www.piste-ai.com`（`piste-ai.com` は 301 で www に統一されている）。

### 3. 本文の必須要素

- H1 は1つだけ。
- H1 直下に **公開日（更新日）の表示**と、**要点3行**（対象者・得られる成果・必要条件）。
- 記事末尾に FAQ（Q/A形式）・まとめ・CTA。CTA の表示文言と遷移先を一致させる（「ココナラで相談する」なのに自社フォームへ飛ばさない）。
- **関連記事へのリンクを2〜3本**（同じクラスタ: ツール連携 / 経理・財務 / 現場記録 / Claude Code の使い方）。トップページへのリンクだけで終わらせない。
- 画像: `alt` 必須、`width` と `height` を必ず指定、`loading="lazy"`（アイキャッチ以外）。
- 画像ファイルは **幅1,200px・WebP・300KB以下**を目標。`/sync-blog` が生成する JPG（1536x1024）はそのまま置かず変換する。
  変換例: `cwebp -q 80 -resize 1200 0 in.jpg -o out.webp`（cwebp が無ければ `sips` で幅1200にリサイズしてから圧縮）。

### 4. 公開後の手順（毎回）

1. `site/sitemap.xml` を **全公開ページ**で再生成する（トップ・blog/・全記事・training・privacy・terms・tokushoho）。
   `lastmod` はファイルの更新日。changefreq/priority は現行と同じ（トップ 1.0 weekly、一覧 0.8 weekly、記事 0.7 monthly）。
2. `site/feed.xml`（RSS 2.0）を最新記事順で生成する。タイトル・link・description・pubDate・guid（URL）。
3. `site/blog/index.html` と `site/index.html`（最大4枚）のカードを更新（既存スキルの Step 5・6）。
4. Netlify に本番デプロイ。
5. デプロイ後、公開URLで **GA4 タグが1回だけ発火していること**と canonical を確認する。
6. Search Console で URL 検査 → インデックス登録リクエスト（可能なら）。

### 5. `/sync-blog` スキル（`~/.claude/commands/ai-hp-blog.md`）に不足している工程

現行スキルは「コピー → 画像生成 → 一覧更新 → デプロイ」のみで、以下が無い。**スキル改修時はこの順で追加する**:

| 追加位置 | 工程 |
|---|---|
| Step 2 の直後 | 上記「1. head 必須テンプレート」の挿入（GA4 / Clarity / canonical / OGP / Twitter / Article / FAQPage / BreadcrumbList） |
| Step 3 | 検索向け短縮 title の生成、FAQ セクションの Q/A 抽出（FAQPage 用）、公開日の抽出 |
| Step 4-3 | 挿入する `<img>` に `width` / `height` / `loading="lazy"` を付与、JPG→WebP 変換 |
| Step 6 の直後 | sitemap.xml と feed.xml の再生成 |
| Step 8 | 公開URLでのタグ発火・canonical の確認結果を報告に含める |

スキル改修前に手動で記事を公開する場合も、本ファイルのルールを満たすこと。

---

## 既存記事の一括修正（2026-09-10 の状況）

上記「診断の要点」の表は午前時点のもので、同日中に `tools/seo_build.py` と `tools/release_build.py` で以下が**完了**した:
GA4/Clarity・canonical・OGP・Article(BlogPosting)・BreadcrumbList（4階層）・短縮 title・sitemap/feed/llms.txt・WebP と width/height・
関連記事3本・パンくず・公開日・著者表示・カテゴリページ6種・about.html・404。

夕方〜夜の再調査と一括修正（`audit/20260910/aio_summary.json`、レポート `20260910_aio_guide.html` 3章・8章）で、2026-09-10 中に以下を**完了**:

- 「この記事の要点」欄（対象・できるようになること・必要なもの）: `tools/keypoints/{slug}.json` に155記事分。seo_build.py が読んで生成する。**新規記事は必ずこの JSON も作る**
- H2 のうち2本を読者の質問文に（全155記事、目次も同期）
- 外部の一次資料リンク（公式サイト・公式ドキュメント、実在確認済み）と本文中の関連記事リンク（全155記事）
- FAQ 節と FAQPage スキーマ（155/155。seo_build.py は h3 形式・`.faq-item` 形式・`<p><strong>` 形式の3種を読む）
- 更新日: `tools/modified.json`（{slug: "YYYY-MM-DD"}）で管理。内容を変えた記事だけ日付を更新すると dateModified と本文の「更新日」に反映される。タグ追加だけでは更新しない
- 表記の統一: 肩書き「株式会社Piste 代表取締役」（CEO 表記や「Piste AI EVANGELISTS 代表 / AIコンサルタント / フィットネスクラブ経営者」の併記はしない。JSON-LD の jobTitle は「代表取締役 / AIコンサルタント」）、支援実績「400社以上（2026年9月時点）」、導入サポート「1時間 ¥10,000（税込）」、電話「0566-48-6580」、「ココナラで相談する」はココナラへ
- アフィリエイトリンク（A8）は 2026-09-10 に全廃し公式サイトへのリンクに置換。以後、記事にアフィリエイトを入れない
- 色コントラスト: LINE緑 `--line-green: #05823a`、金色バッジは `--gold-dark` 背景（WCAG AA）

残っているもの:

- [ ] 実測つきの独自事例3本（石川さんの案件データが必要）
- [ ] 3か月ごとの記事見直し（次回 2026-12。見直した記事だけ `tools/modified.json` を更新）

---

## サイト全体の未対応課題（ブログ以外）

2026-09-10 に完了: llms.txt、training.html の H1、JSON-LD の address/sameAs（X・Instagram・Threads・ココナラ・LINE）、
フッター住所、地域の一文、Google Fonts 削減（5ウェイト）、カスタム404、`.html`→拡張子なしの301、カテゴリページ、about.html と Person。
電話番号は石川さんの指示で **0566-48-6580** に統一（フッター・about・aichi・特商法・JSON-LD、`tools/seo_build.py` の `PHONE`）。以前の 090 番号は使わない（2026-09-10 夕方に統一）。支援実績は **「400社以上」** で統一（同日）。

残り:

- Bing Webmaster Tools は 2026-09-10 に石川さんが登録済み（Search Console からインポート）。同日時点で Bing の索引は0件。IndexNow で170 URL 送信済み。数日後に `site:piste-ai.com` を Bing で検索して索引数を確認する
- `sameAs` に YouTube → チャンネルを持っていないため不要（2026-09-10 石川さん確認）
- http→https→www の2段リダイレクトを1段に（Netlify 側の仕様）
- ~~API トークン~~ → 2026-09-10 18:27 に `google_searchconsole_token.json` 保存済み（analytics.readonly + webmasters）。Search Console の `https://www.piste-ai.com/` は所有者権限で取得可。**GA4 プロパティ 531067300 は 403**（認可アカウントが閲覧者に入っていない。GA4 管理画面で閲覧者追加、または所有アカウントで再認可が必要）
- 月次記録: `python3 tools/ai_referral_report.py`（直近28日。引数で期間指定可）→ `audit/reports/ai_referral_*.md`。GA4 の AI 参照元（chatgpt / perplexity / copilot / gemini / claude）と GSC の上位ページ・クエリ・サイトマップ状況を出す。毎月1日に実行し、手動項目（3つの AI への質問テスト、生成AI機能フィルタ、Bing の site: 件数）を追記する

---

## 効果測定の注意

- GA4 のタグ設置範囲を広げた日を記録し、その前後の数字をそのまま成長率として扱わない。
- Search Console と GA4 は期間をそろえて比較するが、クリック数とセッション数の一致は求めない。
- 投稿頻度そのものをランキング要因と見なさない。当初2週間は新規記事より既存上位記事の改善を優先。


## 公開手順（2026-09-10 導入。本ファイル内で矛盾があればこの節と `.Codex/commands/seo-publish.md` を優先）

1. `python3 tools/optimize_images.py` → `python3 tools/seo_build.py`（`site/` を正規化）
2. `python3 tools/release_build.py`（`audit/20260910/release/public` を生成。canonical・内部リンク・JSON-LD・RSS・sitemap・llms.txt を拡張子なしへ、直書き gtag を除去）
3. `python3 tools/verify_release.py` と `node --test tests/*.test.mjs`
4. `cd site && netlify deploy --no-build --dir=../audit/20260910/release/public --functions=netlify/functions --site=22906075-c680-4d7e-b48b-ceb78d987037` で確認URL → 問題なければ `--prod`
5. 本番の記事URLで canonical が拡張子なし、GA4 が analytics.js の1回だけ、旧 `.html` が 301 であることを確認
6. IndexNow で Bing に URL を通知する（キーは `audit/20260910/indexnow_key.txt`、キーファイル `site/<key>.txt` は release_build の PUBLIC_FILES に登録済み）。sitemap.xml の全 URL を `https://api.indexnow.org/indexnow` に POST（host / key / keyLocation / urlList）。202 が返れば受付済み。2026-09-10 に初回170 URL 送信済み

`site/` を直接デプロイしてはいけない。2026-09-10 14:56 の直デプロイで、ブログ155記事の GA4 二重発火と canonical 不整合が発生した（同日夕方に手順どおり再デプロイして解消）。

AIO の要点・米国調査・構造化データ・残タスクは `20260910_aio_guide.html`（アーティファクト <https://claude.ai/code/artifact/f168e2ce-2df1-435e-9d07-d66956fd9308>）。
