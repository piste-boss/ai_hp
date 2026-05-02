# サイト管理SEOタスク — Piste AI EVANGELISTS

更新日: 2026年4月11日

> 注: piste-ai.comはNetlify静的サイトのため、WordPress管理画面ではなく、
> HTMLソースファイル（HP作成/site/）を直接編集して対応する。

---

## 🔴 緊急（即日対応）

### 1. 構造化データのemail修正
- **ファイル**: `site/index.html`
- **現在値**: `"email": "info@piste-i.com"`
- **修正値**: `"email": "info@piste-ai.com"`
- **作業時間**: 5分

### 2. サイトマップ更新
- **ファイル**: `site/sitemap.xml`
- 以下の3記事を追加：
  ```xml
  <url>
    <loc>https://www.piste-ai.com/blog/ai-sales-email-automation.html</loc>
    <lastmod>2026-04-11</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://www.piste-ai.com/blog/ai-customer-support-automation.html</loc>
    <lastmod>2026-04-09</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://www.piste-ai.com/blog/ai-accounting-automation.html</loc>
    <lastmod>2026-04-06</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  ```
- **作業時間**: 10分

### 3. ブログ記事にcanonicalタグ追加（全13記事）
- 各記事の `<head>` 内に追加：
  ```html
  <link rel="canonical" href="https://www.piste-ai.com/blog/[slug].html">
  ```
- **作業時間**: 30分

### 4. ブログ記事にmeta description追加（未設定記事）
- 対象: ai-customer-support-automation, ai-accounting-automation, claude-code-business-guide, ai-adoption-mistakes, ai-tools-for-business-2026 + 要確認記事
- **作業時間**: 1時間

### 5. ブログ記事にOGPタグ追加（未設定記事）
- 各記事に以下を追加：
  ```html
  <meta property="og:title" content="記事タイトル">
  <meta property="og:description" content="記事の概要">
  <meta property="og:type" content="article">
  <meta property="og:url" content="https://www.piste-ai.com/blog/[slug].html">
  <meta property="og:image" content="https://www.piste-ai.com/images/blog-[slug].jpg">
  <meta property="og:site_name" content="Piste AI EVANGELISTS">
  <meta name="twitter:card" content="summary_large_image">
  ```
- **作業時間**: 1時間

---

## 🟡 短期（1〜2週間）

### 6. 画像のWebP変換
- 対象: `site/images/` 内の全JPG/PNG画像
- ツール: `cwebp` コマンドまたはSquoosh
- 推定削減効果: 3,265KB（PageSpeed Insights計測）
- HTML内の `<img src>` も `.webp` に更新
- `<picture>` タグでフォールバック対応推奨：
  ```html
  <picture>
    <source srcset="image.webp" type="image/webp">
    <img src="image.jpg" alt="説明" width="800" height="600">
  </picture>
  ```

### 7. 画像にwidth/height属性追加
- CLS改善のため、全 `<img>` タグに明示的なサイズ指定
- デスクトップCLS 0.677 → 0.1以下を目標

### 8. ブログ記事にArticle構造化データ追加（全13記事）
- JSON-LD形式（詳細はblog.mdを参照）

### 9. BreadcrumbList構造化データ追加
- トップページ・ブログ一覧・各ブログ記事に追加：
  ```json
  {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      { "@type": "ListItem", "position": 1, "name": "ホーム", "item": "https://www.piste-ai.com/" },
      { "@type": "ListItem", "position": 2, "name": "ブログ", "item": "https://www.piste-ai.com/blog/" },
      { "@type": "ListItem", "position": 3, "name": "記事タイトル" }
    ]
  }
  ```

### 10. 構造化データにsameAs追加
- **ファイル**: `site/index.html`
- X（Twitter）、LINE、その他SNSのURLを追加：
  ```json
  "sameAs": [
    "https://x.com/PisteAI",
    "https://lin.ee/XXXXXXX"
  ]
  ```

### 11. 構造化データにtelephone・address追加
- ローカルSEO強化のため、可能であれば連絡先情報を追加

### 12. ブログ記事にGA/Clarityタグ確認・追加
- 全ブログ記事の `<head>` にGA/Clarityタグが設置されているか確認
- 未設置の場合はトップページと同じタグを追加

### 13. 未使用CSS/JSの削減
- PageSpeed指摘: 未使用CSS 89KB、未使用JS 63KB
- PurgeCSS等のツールで不要なスタイルを除去
- 各ブログ記事がインラインCSSを持つ構造を見直し、共通CSSファイル化を検討

---

## 🔵 中期（1〜3ヶ月）

### 14. レンダリングブロックリソースの最適化
- Google Fonts の読み込みを最適化（preload + display=swap）
- クリティカルCSSをインライン化、残りを非同期読み込み
- 推定改善効果: -5,580ms

### 15. 内部リンク強化
- ブログ記事末尾に「関連記事」セクション追加
- トップページからブログ記事への動線強化
- 記事本文中に関連記事へのテキストリンク追加

### 16. サービス詳細ページ新設
- `/services/` — AI導入コンサルティングの詳細
- `/case-studies/` — 導入事例集
- `/faq/` — よくある質問

### 17. 画像の遅延読み込み（lazy loading）
- ファーストビュー以外の画像に `loading="lazy"` 追加

### 18. Netlifyデプロイ時のサイトマップ自動更新
- デプロイスクリプトにサイトマップ更新を組み込む

---

## ⚠️ 注意事項

- 全変更はGitでコミットし、Netlifyの自動デプロイで反映される
- 大きな変更（CSS構造変更等）はステージング環境で検証してからデプロイ
- 構造化データの変更後はGoogleリッチリザルトテストで検証: https://search.google.com/test/rich-results
