# SEO・AIO・計測の実装報告（2026-09-10）

本番: https://www.piste-ai.com/  
初回実装完了時のデプロイ: `6aa20f07f0efb9e960bd058e`

16:29のHTTP再調査で見つかった残りのメタ情報・画像寸法を追加修正。最新結果は [ブラウザ操作なしの再調査報告](20260910_recheck_report.md) を参照。

## 本番へ反映した内容

- 全171 HTML（404を含む）のGA4・Clarityを `/js/analytics.js` に集約。本番 `www.piste-ai.com` のみで発火。
- 正規URLを `.html` なしへ統一。旧 `.html` と `index.html` は301。canonical・内部リンク・JSON-LD・RSS・サイトマップも統一。
- サイトマップを170 URLに拡充。Search Consoleから再提出し「サイトマップを送信しました」を確認。
- 155記事のメタ情報、公開日・著者、構造化データ、関連記事、パンくず、カテゴリ一覧を含む既存の新しいSEOビルド成果を統合して公開。
- 代表・会社紹介 `/about`、Claude Code支援 `/claude-code-support`、地域向け `/aichi`、カスタム404を公開。
- 旧 `#service`・`#about`・`#consulting` と経理記事の目次リンクを修正。
- 画像のWebP化・寸法指定を反映。記事アイキャッチは優先読み込み。スマートフォンでのブログロゴの変形とナビゲーションを修正。
- トップの「現場」「伴走」が語の途中で折り返されないよう調整。ニュースの開閉にキーボード操作・開閉状態の読み上げを追加。
- 経理記事の「Claude Codeなら外部へデータが出ない」「3か月で95%以上の精度になる」という説明を修正し、公式資料を掲載。

## 問い合わせと成果計測

従来のブラウザからの `no-cors` 送信を、Netlify Function `/api/contact` 経由に変更。入力検証後、既存GASのJSON応答 `status:ok` を確認した場合だけ受付完了を表示する。受付成功時に限り `generate_lead` をGA4とClarityに記録する。

LINEリンクは `line_click` とし、友だち追加の成立と区別。GA4の旧 `line_friend_add` のキーイベント指定を解除した。`generate_lead` の既存キーイベント指定は維持。ココナラ遷移は `coconala_click`。

氏名・メール・相談本文をイベントパラメータへ送らない。UTMなどのキャンペーン情報は保持する。Netlify確認用URLでは本番タグを読み込まない。

GASへの実送信テストはメール通知・台帳記録を伴うため実施していない。正常応答・異常応答・通信エラーはモックで検証し、公開APIでは不正入力の400応答を確認した。メールの最終配達までを保証するテストではない。

## 管理画面で確認・変更した内容

| 項目 | 結果 |
|---|---|
| GA4 ↔ Search Console | リンク作成済みを確認。GA4プロパティ531067300、ストリーム14296889350、ドメインpiste-ai.com |
| GA4 | 測定ID G-LR35246V7Bを継続 |
| Clarity ↔ Google Analytics | プロジェクトw54yutjekb、接続先https://www.piste-ai.com、アクティブを確認 |
| GTM | 新規コンテナは導入せず、既存Googleタグの直接設置を共通化。二重設置を回避 |
| Search Consoleサイトマップ | 170 URL版を本番公開後に再提出成功 |
| Googleビジネスプロフィール | AI事業の登録適格性・実際の対面提供方法の回答待ち。ジムのプロフィールは転用していない |

## 検証結果

- 171 HTML: H1・canonical・計測コード・内部リンク・リンク先アンカー・JSON-LDの構文検査を通過。
- サイトマップ170 URLと公開ページのcanonicalが一致。代表紹介ページはSearch Consoleからインデックス登録をリクエスト済み。
- 本番170 URLすべてHTTP200・canonical一致・共通計測コード1件を確認。
- 旧URL301、転送先200、存在しないURL404を確認。GASソースは公開対象から除外し、`/gas/Code.gs` は404。
- 本番ブラウザでGoogleタグとClarityタグが各1件読み込まれることを確認。確認環境には外部計測タグなし。
- 自動テスト4件成功（問い合わせの成功判定・異常応答、確認環境の除外・重複初期化防止・イベントパラメータ）。
- 代表紹介と主力Instagram記事のPC／390px表示を確認。
- プロフィール画像: 2,525,167 → 29,816 bytes。Instagram記事の主画像: 1,905,865 → 54,092 bytes。

データ: [公開URL検査](audit/20260910/release/production-crawl.json)、[静的検査](audit/20260910/release/validation.json)、[デプロイ・連携記録](audit/20260910/release/deployment.json)。

## 継続運用と残る確認

公開手順は [.Codex/commands/seo-publish.md](.Codex/commands/seo-publish.md)。公開用コピーは `tools/release_build.py` で生成し、`tools/verify_release.py` で検査する。155記事の公開日を復元できることを検証し、今後の再生成で公開日が一律に今日へ変わらないよう修正した。変更前ファイルは `audit/20260910/pre-implementation/` に保存。

AI事業のGoogleビジネスプロフィール作成・連携には、対面相談／顧客先訪問の実態と既存登録の有無が必要。支援社数の集計時点、掲載可能な具体的な顧客事例・成果、パートナー認定の参照先も未確認であり、新しい数値や顧客成果は作っていない。既存の会社提供情報は継続掲載している。

Google広告アカウントとの新規連携、全記事の個別仕様の再調査、最新ニュース各項目の一次資料照合、月次レポートの無人実行は今回の公開完了項目に含めない。Google側の再クロール・順位・AI引用・診断警告の解消は、公開直後には判定できない。計測対象ページが増えた2026-09-10を境に、GA4の単純な前後比較は避ける。

参考: [Claude Codeのデータ取り扱い](https://code.claude.com/docs/en/data-usage)、[コンテキストとキャッシュ](https://code.claude.com/docs/en/prompt-caching)、[人材開発支援助成金の公式情報](https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/koyou_roudou/koyou/kyufukin/d01-1.html)。
