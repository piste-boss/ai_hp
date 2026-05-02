# ブログSEO施策 — Piste AI EVANGELISTS

更新日: 2026年4月11日

---

## 1. 既存記事の最適化（緊急）

### 全記事共通で不足しているSEO要素

すべてのブログ記事（13記事）に以下を追加する必要がある：

#### a. canonical タグ（全記事で未設定）
```html
<link rel="canonical" href="https://www.piste-ai.com/blog/[slug].html">
```

#### b. Article 構造化データ（全記事で未設定）
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "記事タイトル",
  "description": "記事の概要",
  "author": {
    "@type": "Person",
    "name": "石川 卓",
    "jobTitle": "AIコンサルタント"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Piste AI EVANGELISTS",
    "logo": {
      "@type": "ImageObject",
      "url": "https://www.piste-ai.com/images/logo.png"
    }
  },
  "datePublished": "2026-XX-XX",
  "dateModified": "2026-XX-XX",
  "image": "https://www.piste-ai.com/images/blog-[slug].jpg",
  "mainEntityOfPage": "https://www.piste-ai.com/blog/[slug].html"
}
</script>
```

#### c. GA/Clarityトラッキングタグ
トップページと同じGAタグ・Clarityタグが設置されているか確認。未設置なら追加：
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
```

### 記事別 meta description・OGP 追加対応リスト

| # | 記事slug | meta description設定 | OGP設定 | 対応 |
|---|---------|---------------------|---------|------|
| 1 | ai-sales-email-automation | 🟢 設定済み | 🟢 設定済み | canonical・構造化データのみ追加 |
| 2 | ai-customer-support-automation | ❌ 未設定 | ❌ 未設定 | 全項目追加 |
| 3 | ai-accounting-automation | ❌ 未設定 | ❌ 未設定 | 全項目追加 |
| 4 | ai-sns-marketing-automation | 要確認 | 要確認 | 確認後対応 |
| 5 | ai-prompt-techniques-business | 要確認 | 要確認 | 確認後対応 |
| 6 | ai-recruitment-efficiency | 要確認 | 要確認 | 確認後対応 |
| 7 | ai-meeting-minutes-automation | 要確認 | 要確認 | 確認後対応 |
| 8 | ai-automation-one-person-business | 要確認 | 要確認 | 確認後対応 |
| 9 | ai-cost-roi-for-sme | 要確認 | 要確認 | 確認後対応 |
| 10 | claude-code-business-guide | ❌ 未設定 | ❌ 未設定 | 全項目追加 |
| 11 | ai-adoption-mistakes | ❌ 未設定 | ❌ 未設定 | 全項目追加 |
| 12 | ai-sales-growth-examples | 要確認 | 要確認 | 確認後対応 |
| 13 | ai-tools-for-business-2026 | ❌ 未設定 | ❌ 未設定 | 全項目追加 |

### meta description 案（未設定記事用）

| 記事 | 推奨 meta description（120文字以内） |
|------|--------------------------------------|
| ai-customer-support-automation | AIチャットボット・自動返信で問い合わせ対応と予約管理を効率化。中小企業でも始められる顧客対応AI自動化の実践ガイド。 |
| ai-accounting-automation | 請求書処理・仕訳入力をAIで自動化。経理業務を半分以下に削減する具体的なツールと導入ステップを解説。 |
| claude-code-business-guide | Claude Codeの基本機能からビジネス活用法まで徹底解説。プログラミング不要で業務自動化ができるAIコーディングツールの始め方。 |
| ai-adoption-mistakes | AI導入で失敗する中小企業の共通パターン5つと、成功企業に学ぶ正しいAI活用の進め方を具体的に解説。 |
| ai-tools-for-business-2026 | ChatGPT以外にも注目すべきビジネス向け生成AIツール5選。2026年最新の機能比較と選び方ガイド。 |

---

## 2. 新規記事の計画

### ターゲットKWに基づく推奨記事テーマ

| # | テーマ | ターゲットKW | 想定検索ボリューム | 構成案 |
|---|--------|-------------|-------------------|--------|
| 1 | AI導入の進め方完全ガイド | AI導入 進め方 手順 | 中 | ①現状分析→②ツール選定→③PoC→④本番導入→⑤定着化 |
| 2 | ChatGPT vs Claude 比較 | ChatGPT Claude 比較 違い | 高 | ①価格②機能③得意分野④ビジネス活用⑤選び方 |
| 3 | AI業務効率化の成功事例集 | AI 業務効率化 事例 | 中 | ①営業②経理③カスタマーサポート④マーケティング⑤採用 |
| 4 | 中小企業のDX推進ガイド | 中小企業 DX AI | 中 | ①DXとは②AI活用の位置づけ③段階的導入④補助金 |
| 5 | AI研修・社内教育の進め方 | AI研修 社内 中小企業 | 低〜中 | ①必要なスキル②カリキュラム設計③ツール④評価方法 |
| 6 | 生成AI導入の補助金・助成金 | AI導入 補助金 助成金 | 中 | ①IT導入補助金②ものづくり補助金③申請のコツ |
| 7 | ノーコードAIツール活用法 | ノーコード AI ビジネス | 低〜中 | ①Dify②Make③Zapier④業務別おすすめ |
| 8 | AI×データ分析の始め方 | AI データ分析 中小企業 | 低〜中 | ①売上データ分析②顧客分析③予測分析④ツール |

### 投稿スケジュール（推奨）
- **週2本**のペースを維持（現在のペースを継続）
- 月曜・木曜に公開が望ましい
- Tier 1 KW対応記事を月1本、Tier 3ロングテールを週1本

---

## 3. 記事作成SEOチェックリスト

新規記事を作成する際に、以下を必ず確認：

### <head>内
- [ ] `<title>` — 32〜60文字、ターゲットKW含む、 `| Piste AI EVANGELISTS` で終わる
- [ ] `<meta name="description">` — 80〜120文字、ターゲットKW含む、行動喚起を入れる
- [ ] `<meta name="keywords">` — 5〜8個のKW
- [ ] `<link rel="canonical">` — 記事の正規URL
- [ ] OGP（og:title, og:description, og:type="article", og:image, og:url）
- [ ] Twitter Card（twitter:card, twitter:title, twitter:description, twitter:image）
- [ ] GA/Clarityタグ
- [ ] Article構造化データ（JSON-LD）

### コンテンツ
- [ ] H1 — 記事タイトルと一致、ターゲットKW含む
- [ ] H2 — 5〜8個、論理的な構成、KWを自然に含む
- [ ] H3 — H2の補足として適切に使用
- [ ] 画像 — alt属性設定、WebP形式、width/height指定、遅延読み込み
- [ ] 内部リンク — 関連記事へのリンク2〜3本
- [ ] 外部リンク — 信頼できるソースへの参照1〜2本
- [ ] CTA — 記事末尾に無料相談・LINE友だち追加の導線
- [ ] 文字数 — 2,000〜4,000文字目安

### 公開後
- [ ] サイトマップ更新（sitemap.xmlに追加）
- [ ] ブログ一覧ページ更新（index.htmlに追加）
- [ ] トップページの最新記事セクション更新
- [ ] SNSシェア（X、Threads等）
- [ ] Google Search Consoleでインデックス登録リクエスト

---

## 4. カテゴリー見直し提案

### 現状
- カテゴリー分類なし（全記事がフラットに並列）

### 推奨カテゴリー構成
| カテゴリー | 対応記事 | URL案 |
|-----------|---------|-------|
| AI導入ガイド | ai-adoption-mistakes, ai-cost-roi-for-sme | /blog/category/guide/ |
| AI業務自動化 | ai-meeting-minutes-automation, ai-accounting-automation, ai-customer-support-automation, ai-sales-email-automation | /blog/category/automation/ |
| AIツール紹介 | ai-tools-for-business-2026, claude-code-business-guide | /blog/category/tools/ |
| AI活用術 | ai-prompt-techniques-business, ai-sns-marketing-automation, ai-recruitment-efficiency | /blog/category/tips/ |
| 事例・実績 | ai-sales-growth-examples, ai-automation-one-person-business | /blog/category/case-study/ |

> 静的サイトのため、カテゴリーページの実装はブログ一覧ページ内のフィルター機能として実装するのが現実的。
