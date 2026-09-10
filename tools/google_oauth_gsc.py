#!/usr/bin/env python3
"""Search Console / GA4（読み取り）用の Google OAuth 認可を1回だけ行い、トークンを保存する。

使い方（ターミナルで実行）:
    python3 /Users/ishikawasuguru/AI_コンサル/HP作成/tools/google_oauth_gsc.py

1. 表示される URL をブラウザで開く（Search Console と GA4 の所有者アカウントでログイン）
2. 「許可」を押すと localhost に戻り「認証が完了しました」と表示される
3. ~/.claude/credentials/google_searchconsole_token.json が保存される

保存後は Claude 側で以下が自動化できる:
  - Search Console API でサイトマップ送信・検索クエリ / インデックス状況の取得
  - GA4 Data API で過去28日のアクセス数値の取得
"""
import http.server
import json
import sys
import time
import urllib.parse
import urllib.request
import webbrowser

CLIENT = "/Users/ishikawasuguru/.claude/credentials/client_secret_googleusercontent.com.json"
OUT = "/Users/ishikawasuguru/.claude/credentials/google_searchconsole_token.json"
PORT = 8790
REDIRECT = f"http://localhost:{PORT}/"
SCOPES = [
    "https://www.googleapis.com/auth/webmasters",
    "https://www.googleapis.com/auth/analytics.readonly",
]

cs = json.load(open(CLIENT))
c = cs.get("installed") or cs.get("web")
url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
    "client_id": c["client_id"], "redirect_uri": REDIRECT, "response_type": "code",
    "scope": " ".join(SCOPES), "access_type": "offline", "prompt": "consent",
})
print("\nこの URL をブラウザで開いてください:\n\n" + url + "\n")
try:
    webbrowser.open(url)
except Exception:
    pass

code = {}

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if "code" in q:
            code["v"] = q["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<h2>認証が完了しました。この画面は閉じて構いません。</h2>".encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *a):
        pass

srv = http.server.HTTPServer(("127.0.0.1", PORT), Handler)
srv.timeout = 5
t0 = time.time()
while "v" not in code and time.time() - t0 < 900:
    srv.handle_request()
if "v" not in code:
    print("15分以内に認可されなかったため終了します")
    sys.exit(1)

data = urllib.parse.urlencode({
    "code": code["v"], "client_id": c["client_id"], "client_secret": c["client_secret"],
    "redirect_uri": REDIRECT, "grant_type": "authorization_code",
}).encode()
tok = json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", data))
tok.update({"client_id": c["client_id"], "client_secret": c["client_secret"],
            "token_uri": "https://oauth2.googleapis.com/token", "scopes": SCOPES})
json.dump(tok, open(OUT, "w"), indent=1)
print("保存しました:", OUT)
