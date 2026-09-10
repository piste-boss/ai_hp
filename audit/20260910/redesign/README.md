# Piste トップページ デザイン刷新 — 2026-09-10

アイボリーの背景、チャコールの文字、落ち着いたゴールドを使い、AI導入の伴走支援を伝えるトップページへ刷新しました。

- 大きな日本語見出しとオリジナル画像によるヒーロー。
- 相談・実装・定着を3つの支援として整理。料金比較、代表紹介、問い合わせへつなぐ構成。
- ニュース6件と研修の詳説は、キーボードでも操作できるHTMLの開閉要素へ変更。
- 700px / 1000pxでレイアウトを調整。スマートフォン用メニューの開閉状態とEscape操作を追加。
- SEOメタデータ、構造化データ、計測コード、フォームの入力項目と送信処理を保持。

## 画像

OpenAIの内蔵画像生成ツールを使用。CLI/APIキーは不使用。生成画像を目視確認し、WebPとレスポンシブ画像に変換しました。ヒーローは抽象的なコンセプトアート、仕事風景はAI生成イメージと表記。実際の顧客写真としては扱っていません。

|用途|公開ファイル|容量|
|---|---|---|
|ヒーロー|site/images/redesign-ascent-1200.webp（1122×1402）|110,322 bytes|
|ヒーロー小型|site/images/redesign-ascent-640.webp|48,084 bytes|
|伴走支援イメージ|site/images/redesign-workshop-1200.webp|62,968 bytes|
|伴走支援小型|site/images/redesign-workshop-640.webp|28,296 bytes|

元画像: `audit/20260910/redesign/generated/ascent.png`、`audit/20260910/redesign/generated/workshop.png`。

### 最終プロンプト — ヒーロー

Use case: stylized-concept. Asset type: premium Japanese AI consulting website hero artwork, no website UI. Create a refined editorial 3D architectural still life representing steady progress from complexity to clarity. A single sculptural brushed champagne-gold ribbon ascends through three floating dark charcoal stone platforms, forming a subtle winding path toward soft daylight. Warm ivory plaster backdrop, sculptural shadows, very restrained premium materials, tactile stone and satin metal, elegant and quiet, no sci-fi glow. Composition: portrait 4:5, main sculpture centered with breathing room, entire sculpture visible; designed for the right half of a split website hero, visual weight toward center. Sophisticated architectural magazine photography, realistic global illumination, warm late-afternoon natural side light. Palette warm cream, charcoal, champagne gold. No text, no letters, no numbers, no logos, no robots, no people, no charts, no watermark. This is a conceptual brand illustration, not a customer case photograph.

### 最終プロンプト — 伴走支援

Use case: photorealistic-natural. Asset type: wide editorial image for a Japanese small-business AI consulting website, explicitly an illustrative scene, not a real client or testimonial. Photograph a thoughtful, calm collaborative work surface: two people's hands working together beside an open dark laptop, a cream notebook with small abstract non-legible planning marks, a brushed brass pen, one ceramic coffee cup. No faces. Modern light oak table beside a large window, warm ivory contemporary office, soft late afternoon natural daylight, gentle shadows, premium understated Japanese editorial photography. Cropped close, tactile paper and wood grain, realistic hands with correct anatomy. Wide landscape 3:2. Balanced composition with laptop right and notebook left, quiet visual rhythm, restrained warm cream, charcoal and muted gold palette matching an architectural still-life website hero. No readable text, no numbers, no logos, no watermarks, no futuristic holograms, no staged handshake.

## 検証

全171 HTML / サイトマップ170 URL / JSON-LD168ブロックのリリース検査でエラー0件。計測・問い合わせ関連の4テスト成功。JavaScript構文検査成功。公開環境のHTTP確認結果は `http-check.json`、デプロイ記録は `preview.json` / `production.json` を参照。

ユーザーの指定に従いブラウザユーズは実施していません。実ブラウザでの画面・操作確認、問い合わせの実メール送信は未実施です。表示幅別のCSS、画像寸法、フォームの構造とコードを検査しています。

## 保守

トップページ専用CSS: `site/css/redesign-20260910.css`。本文の `.redesign-home` のみに適用し、記事ページのレイアウトを変更しません。今後のニュース・記事同期時はこのスタイルシートの読み込みと新しいヒーロー要素を保持してください。属性順に依存しないcanonical抽出へリリースビルドも修正しました。
