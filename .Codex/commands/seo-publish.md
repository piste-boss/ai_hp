# SEO・計測を維持する公開手順

2026-09-10導入。新規記事・ニュース・固定ページ更新後も必ず実行する。

1. プロジェクトルートで `python3 tools/optimize_images.py`、`python3 tools/seo_build.py` を実行。
2. `python3 tools/release_build.py` で公開用コピーを生成。
3. `python3 tools/verify_release.py` と `node --test tests/*.test.mjs` を実行。失敗した場合は修正する。
4. `site/` で `netlify deploy --no-build --dir=../audit/20260910/release/public --functions=netlify/functions --site=22906075-c680-4d7e-b48b-ceb78d987037` を実行し、確認URLで表示・転送・フォームの入力エラーを確認する。
5. 同じコマンドに `--prod` を付けて公開する。ユーザーが公開を依頼している場合、重ねて承認を求めない。
6. 本番のcanonical、旧.html URLの301、GA4・Clarityの読み込み、サイトマップを確認する。

公開ディレクトリは `audit/20260910/release/public`。`site/gas/` や認証情報を公開対象に含めない。Functionsは別にバンドルする。

正規URLは拡張子なし。HTMLファイルは `.html` のまま保持し、release_build.pyでcanonical・内部リンク・JSON-LD・RSS・サイトマップと301転送を揃える。記事の公開日は一覧から復元した値を維持し、実質的な内容変更時のみ更新日を変更する。

計測は `/js/analytics.js` に集約する。GA4 `G-LR35246V7B`、Clarity `w54yutjekb`。本番 `www.piste-ai.com` のみで発火し、Netlify確認URLは計測しない。GTMコンテナや直書きタグを重ねて追加しない。

フォームの成功判定は `/api/contact` の `{status:"ok"}` のみ。`generate_lead` は受付成功時のみ送信する。LINEクリックは `line_click`、ココナラ遷移は `coconala_click`。氏名・メール・相談本文を計測へ送らない。

実送信のテストはメール通知・台帳記録を伴う。通常の検証では `tests/contact.test.mjs` のモックと不正入力の400応答を利用する。
