# SEO 改善効果の1週間後チェック（2026-09-17）

対象: https://www.piste-ai.com/ ／ 比較対象: 2026-09-10 の一括修正（canonical・OGP・構造化データ・sitemap・RSS・GA4 統一・WebP など）
データ: Search Console API（URL プレフィックス プロパティ）、URL 検査 API（sitemap の全 177 URL）、本番 HTML の実測、Bing 検索結果。
Search Console の検索データは 9/14 まで（2〜3日の遅延）。GA4 は API 403 のため未取得。

## 結論

- **技術面の修正は本番で全部効いている。** canonical は拡張子なし、旧 `.html` は 301、GA4 は analytics.js の1回だけ、sitemap 177 URL、RSS 30件、llms.txt 200。9/16 公開の新記事にも BlogPosting・FAQPage・BreadcrumbList・OGP・公開日が入っている。
- **Google のクロールが4倍に増えた。** 直近1週間（9/10〜9/16）に 56 URL がクロールされた。前週は 14、その前は 11。9/16 だけで 22 URL。修正が「見つけてもらう」段階で効いている。
- **索引数は 127 → 149 に増えた。** 9/10 の診断では 127 URL 登録。今回の URL 検査では 177 中 149 が登録済み（ブログ記事は 162 中 140）。
- **クリック・表示回数はまだ変化なし。** 1日あたりクリック 6〜7、表示 70〜95 で、修正前（28日平均でクリック 7.9/日、表示 84/日）と同水準。順位・流入への反映は通常2〜4週間かかるため、今週の時点では判定しない。
- **Bing は依然 0 件。** `site:piste-ai.com` に Web 結果が出ない（画像だけ4件ヒット）。IndexNow 送信から1週間経っても未反映。

## 1. Search Console（クリック・表示・順位）

| 日付 | クリック | 表示 | CTR | 平均順位 | 表示のあったページ数 |
|---|---|---|---|---|---|
| 9/9（修正前日） | 11 | 107 | 10.3% | 6.9 | 40 |
| 9/10 | 10 | 87 | 11.5% | 7.3 | 36 |
| 9/11 | 4 | 71 | 5.6% | 7.9 | 28 |
| 9/12 | 5 | 64 | 7.8% | 8.1 | 31 |
| 9/13 | 7 | 75 | 9.3% | 11.7 | 36 |
| 9/14 | 6 | 95 | 6.3% | 8.4 | 33 |

- 修正前の基準（9/10 診断、28日間）: 221 クリック / 2,356 表示 = 7.9 クリック/日、84 表示/日。
- 修正後 9/10〜9/14 の5日間: 32 クリック / 392 表示 = 6.4 クリック/日、78 表示/日。**差は誤差の範囲**。
- デバイス: 修正後はモバイル 17 クリック / デスクトップ 15。9/9 はデスクトップ 9 / モバイル 2 だったので、モバイルの比率は上がっている（母数が小さいので参考値）。
- 上位ページは変わらず Instagram 連携（9 クリック / 145 表示 / 7.0 位）、PayPay 連携（38 表示 / 3.8 位）。
- 主要クエリ: 「claude 支払い方法 paypay」17 表示 5.3 位、「claude インスタ 連携」7 表示 7.6 位、「claude paypay」6 表示 2.7 位。「石川卓」3 表示 6.0 位、「学歴」「実業家」で 1 位表示あり（about ページが人物検索に出始めた）。
- searchAppearance（生成AI機能など）の内訳は API に出ない。管理画面の「生成AI機能」フィルタは手動確認が必要。

### 注意: 修正前データが API で取れない

URL プレフィックス プロパティ `https://www.piste-ai.com/` は 9/9 からしかデータがない（このとき作成されたため）。8月以前の履歴はドメイン プロパティ `sc-domain:piste-ai.com` にあるが、API 認可アカウントに権限がなく 403。**来週以降も前後比較をするなら、ドメイン プロパティに認可アカウント（token 作成時の Google アカウント）を「フル」権限で追加する**。

## 2. Google のクロール・索引（URL 検査 API、177 URL）

| 状態 | 件数 |
|---|---|
| 登録済み（送信して登録されました） | 149 |
| Google に認識されていない（未クロール） | 18 |
| 代替ページ（Google が旧 `.html` を正規と判断） | 6 |
| クロール済み・インデックス未登録 | 3 |
| API エラー（500） | 1 |

最終クロール日の週別分布:

| 週 | クロールされた URL |
|---|---|
| 8/20〜8/26 | 9 |
| 8/27〜9/2 | 11 |
| 9/3〜9/9 | 14 |
| **9/10〜9/16** | **56** |

### 未クロールの 18 URL

新記事と、9/10 に新設したページが中心。sitemap には載っているが Googlebot がまだ来ていない。

- 新設ページ: `/aichi`、`/blog/category-claude-code-basics`、`/blog/category-finance`
- 9/10 以降の新記事: customer-acquisition-channels、lending-checkout-records、promotion-campaign-results、purchase-price-history、waste-loss-records
- それ以前の記事で未クロール: asana、automation-effect-tracking、backlog、denshi-chobo-compliance、google-sheets、jalan、kintone、peatix、shopify、zoho（各 `-integration` など）

### 旧 `.html` を正規と判断されている 6 URL

ai-data-analysis-dashboard、ai-knowledge-management、ai-sales-email-automation、ai-sns-marketing-automation、terms、training。
どれも 4月以前から索引されていた URL で、Google 側の正規判定が旧 URL のまま。301 と canonical は正しく出ているので、再クロールで自然に切り替わる。放置でよい。

### クロール済み・未登録の 3 URL

- `/blog/category-tool-integration`（9/10 クロール）: カテゴリ一覧。品質判定待ち。
- `/blog/claude-code-food-delivery-integration`（9/16 クロール）: クロール直後で判定待ち。
- `/blog/claude-code-gmail-integration`（7/31 クロール）: 1か月半再クロールされていない。内容の薄さで落とされた可能性。要確認。

## 3. 本番 HTML の実測（9/17）

| 項目 | 結果 |
|---|---|
| 記事 URL の canonical | 拡張子なしで一致 |
| 旧 `.html` URL | 301 → 拡張子なし |
| `piste-ai.com` → `www` | 301（http は http→https→www の2段のまま） |
| GA4 / Clarity | `/js/analytics.js` 1本のみ。直書き gtag なし |
| sitemap.xml | 177 URL。lastmod はファイルごとの更新日（3/15〜9/17） |
| feed.xml | 200、30 記事 |
| llms.txt / robots.txt | 200。AI クローラー許可、Sitemap 指定あり |
| 9/16 公開の新記事 | BlogPosting・FAQPage・BreadcrumbList・OGP 画像・datePublished すべてあり |

### 見つけた気になる点: title の長さ

`seo_build.py` は本文 title を表示幅 33（全角換算）以内に収めているが、その後ろに ` | Piste AI EVANGELISTS` を必ず付ける。
結果、162 記事中 131 記事が接尾辞込みで表示幅 33 を超え、51 記事は 60 文字超（例: 「Claude Code × PayPay連携で売上集計・キャッシュレス対応をAI自動化 | Piste AI EVANGELISTS」66 文字）。
検索結果では末尾のブランド名側が切れるだけなので致命的ではないが、CLAUDE.md の「接尾辞は付けない」ルールと実装が食い違っている。
接尾辞を外すか短くする（`| Piste` など）かは判断が必要。

## 4. Bing

- `site:piste-ai.com` の Web 検索結果は 0（DuckDuckGo でも 0）。画像検索には 4 枚（ogp.jpg・profile.jpg など）がヒットしており、クロール自体は始まっている。
- 9/10 の IndexNow 170 URL 送信から1週間で Web 索引はまだ反映されていない。Bing Webmaster Tools の「サイトエクスプローラー」でクロール状況を確認し、sitemap の再送信を推奨。

## 5. 取れなかったデータ

- **GA4**（プロパティ 531067300）: API 403 のまま。認可アカウントを GA4 の閲覧者に追加すれば `tools/ai_referral_report.py` でセッション・AI 参照元が取れる。
- **ドメイン プロパティの Search Console**: 上記のとおり 403。修正前（8月）との比較に必要。
- **PageSpeed Insights API**: 日次クォータ超過（quota_limit 0）で取得不可。Lighthouse のモバイル速度（前回 53、LCP 11.6s）の再測定は PageSpeed の Web 画面で手動確認が必要。

## 6. 来週までにやること

1. **石川さん**: Search Console のドメイン プロパティと GA4 に、API 認可アカウントの権限を追加する（前後比較のため）。
2. **石川さん**: Bing Webmaster Tools でサイトの索引状況を確認し、sitemap を再送信する。
3. 未クロール 18 URL のうち新設ページ 3 つと新記事 5 本は Search Console の URL 検査から「インデックス登録をリクエスト」する（1日あたり 10〜12 件が上限目安）。
4. ~~gmail-integration 記事の加筆~~ → 9/17 に実施。接続方法（claude.ai コネクタ / 自前 MCP）の比較表、権限スコープ、Google 送信者ガイドライン、FAQ 2問を追加。更新日 2026-09-17。
5. ~~title 接尾辞の扱いを決める~~ → 9/17 に記事 title から ` | Piste AI EVANGELISTS` を外して本番反映（`tools/seo_build.py`）。カテゴリ一覧・ブログ一覧の title は短いので接尾辞を維持。
6. 次回チェックは 9/24〜10/1。クリック・表示回数の判定はそこから。今回の数値（クリック 6.4/日、表示 78/日、索引 149）を基準にする。
