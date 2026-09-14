#!/usr/bin/env python3
"""AI 参照元レポート（GA4）と Search Console の月次記録を生成する。

使い方:
    python3 tools/ai_referral_report.py            # 直近28日
    python3 tools/ai_referral_report.py 2026-08-01 2026-08-31

前提: ~/.claude/credentials/google_searchconsole_token.json（tools/google_oauth_gsc.py で作成。
       analytics.readonly と webmasters スコープ）。
       認可したアカウントが GA4 プロパティ 531067300 の閲覧者であること。
出力: audit/reports/ai_referral_YYYYMMDD-YYYYMMDD.md と同名 .json
"""
import json, sys, datetime, urllib.request, urllib.parse
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
TOKEN = Path.home() / ".claude/credentials/google_searchconsole_token.json"
GA4_PROPERTY = "531067300"
GSC_SITES = ["https://www.piste-ai.com/", "sc-domain:piste-ai.com"]
AI_SOURCES = {  # sessionSource に含まれる文字列 → 表示名
    "chatgpt": "ChatGPT", "openai": "ChatGPT", "perplexity": "Perplexity", "copilot": "Copilot",
    "bing.com/chat": "Copilot", "gemini": "Gemini", "bard": "Gemini", "claude": "Claude", "anthropic": "Claude",
    "you.com": "You.com", "duckduckgo": "DuckDuckGo AI", "felo": "Felo", "genspark": "Genspark",
}

def access_token():
    tok = json.loads(TOKEN.read_text())
    data = urllib.parse.urlencode({"client_id": tok["client_id"], "client_secret": tok["client_secret"],
                                   "refresh_token": tok["refresh_token"], "grant_type": "refresh_token"}).encode()
    return json.load(urllib.request.urlopen(urllib.request.Request("https://oauth2.googleapis.com/token", data=data)))["access_token"]

def api(at, url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {at}", "Content-Type": "application/json"},
                                 method="POST" if body is not None else "GET")
    try:
        return json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode()[:300]}

def ga4(at, start, end):
    out = {"error": None, "ai_sessions": [], "ai_pages": [], "total_sessions": None, "sources": []}
    tot = api(at, f"https://analyticsdata.googleapis.com/v1beta/properties/{GA4_PROPERTY}:runReport",
              {"dateRanges": [{"startDate": start, "endDate": end}], "metrics": [{"name": "sessions"}, {"name": "screenPageViews"}]})
    if "error" in tot:
        out["error"] = tot; return out
    out["total_sessions"] = int(tot["rows"][0]["metricValues"][0]["value"]) if tot.get("rows") else 0
    src = api(at, f"https://analyticsdata.googleapis.com/v1beta/properties/{GA4_PROPERTY}:runReport",
              {"dateRanges": [{"startDate": start, "endDate": end}], "dimensions": [{"name": "sessionSource"}, {"name": "sessionMedium"}],
               "metrics": [{"name": "sessions"}, {"name": "engagedSessions"}, {"name": "keyEvents"}], "limit": 500,
               "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}]})
    for r in src.get("rows", []):
        s, m = r["dimensionValues"][0]["value"], r["dimensionValues"][1]["value"]
        sess, eng, key = (int(float(x["value"])) for x in r["metricValues"])
        out["sources"].append({"source": s, "medium": m, "sessions": sess})
        for k, name in AI_SOURCES.items():
            if k in s.lower():
                out["ai_sessions"].append({"ai": name, "source": s, "medium": m, "sessions": sess, "engaged": eng, "key_events": key}); break
    if out["ai_sessions"]:
        flt = {"orExpression": {"expressions": [{"filter": {"fieldName": "sessionSource", "stringFilter": {"matchType": "CONTAINS", "value": k, "caseSensitive": False}}} for k in AI_SOURCES]}}
        pg = api(at, f"https://analyticsdata.googleapis.com/v1beta/properties/{GA4_PROPERTY}:runReport",
                 {"dateRanges": [{"startDate": start, "endDate": end}], "dimensions": [{"name": "pagePath"}, {"name": "sessionSource"}],
                  "metrics": [{"name": "sessions"}], "dimensionFilter": flt, "limit": 50,
                  "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}]})
        for r in pg.get("rows", []):
            out["ai_pages"].append({"page": r["dimensionValues"][0]["value"], "source": r["dimensionValues"][1]["value"], "sessions": int(r["metricValues"][0]["value"])})
    return out

def gsc(at, start, end):
    res = {}
    for site in GSC_SITES:
        q = urllib.parse.quote(site, safe="")
        base = f"https://www.googleapis.com/webmasters/v3/sites/{q}/searchAnalytics/query"
        d = {}
        tot = api(at, base, {"startDate": start, "endDate": end, "dimensions": []})
        if "error" in tot:
            res[site] = {"error": tot}; continue
        d["total"] = (tot.get("rows") or [{}])[0]
        d["searchAppearance"] = api(at, base, {"startDate": start, "endDate": end, "dimensions": ["searchAppearance"]}).get("rows", [])
        d["top_pages"] = api(at, base, {"startDate": start, "endDate": end, "dimensions": ["page"], "rowLimit": 15}).get("rows", [])
        d["top_queries"] = api(at, base, {"startDate": start, "endDate": end, "dimensions": ["query"], "rowLimit": 20}).get("rows", [])
        sm = api(at, f"https://www.googleapis.com/webmasters/v3/sites/{q}/sitemaps")
        d["sitemaps"] = [{"path": s["path"], "lastDownloaded": s.get("lastDownloaded", "")[:10], "errors": s.get("errors"),
                          "submitted": [c.get("submitted") for c in s.get("contents", [])], "indexed": [c.get("indexed") for c in s.get("contents", [])]} for s in sm.get("sitemap", [])]
        res[site] = d
    return res

def md(start, end, g, s):
    L = [f"# AI 参照元・検索の月次記録（{start} 〜 {end}）", "", "生成: tools/ai_referral_report.py。数字は GA4 Data API と Search Console API の取得値。", ""]
    L += ["## GA4: AI サービスからの流入", ""]
    if g["error"]:
        L += [f"取得できず: HTTP {g['error'].get('error')}。認可アカウントが GA4 プロパティ {GA4_PROPERTY} の閲覧者になっているか確認する。", ""]
    else:
        L += [f"サイト全体のセッション: {g['total_sessions']}", ""]
        if g["ai_sessions"]:
            L += ["| AI | 参照元 | セッション | エンゲージ | キーイベント |", "|---|---|---|---|---|"]
            L += [f"| {a['ai']} | {a['source']} / {a['medium']} | {a['sessions']} | {a['engaged']} | {a['key_events']} |" for a in g["ai_sessions"]]
            L += ["", "### AI 経由で見られたページ", "", "| ページ | 参照元 | セッション |", "|---|---|---|"]
            L += [f"| {p['page']} | {p['source']} | {p['sessions']} |" for p in g["ai_pages"]]
        else:
            L += ["AI サービス（chatgpt.com / perplexity.ai / copilot / gemini など）からのセッションは 0。", "", "上位参照元:", ""]
            L += [f"- {x['source']} / {x['medium']}: {x['sessions']}" for x in g["sources"][:10]]
        L += [""]
    L += ["## Search Console", ""]
    for site, d in s.items():
        L += [f"### {site}", ""]
        if "error" in d:
            L += [f"取得できず: HTTP {d['error'].get('error')}（このアカウントに権限がない）", ""]; continue
        t = d["total"]
        L += [f"クリック {t.get('clicks', 0)} / 表示 {t.get('impressions', 0)} / CTR {t.get('ctr', 0):.3f} / 平均掲載順位 {t.get('position', 0):.1f}", ""]
        if d["searchAppearance"]:
            L += ["検索での見え方（searchAppearance）:", ""] + [f"- {r['keys'][0]}: クリック {r['clicks']} / 表示 {r['impressions']}" for r in d["searchAppearance"]] + [""]
        else:
            L += ["searchAppearance の内訳なし（生成AI機能の内訳は API に出ないため、管理画面の「生成AI機能」フィルタで手動確認する）", ""]
        if d["top_pages"]:
            L += ["上位ページ:", ""] + [f"- {r['clicks']} クリック / {r['impressions']} 表示 / 順位 {r['position']:.1f}: {r['keys'][0]}" for r in d["top_pages"]] + [""]
        if d["top_queries"]:
            L += ["上位クエリ:", ""] + [f"- {r['clicks']} / {r['impressions']}: {r['keys'][0]}" for r in d["top_queries"]] + [""]
        for sm in d["sitemaps"]:
            L += [f"サイトマップ {sm['path']}: 最終取得 {sm['lastDownloaded']}、送信 {sm['submitted']}、索引 {sm['indexed']}、エラー {sm['errors']}", ""]
    L += ["## 手動で記録する項目", "", "- ChatGPT / Gemini / Claude に「碧南 AI導入 支援」「Claude Code 導入 サポート 愛知」「中小企業 AI研修 助成金」を各3回聞き、出典に piste-ai.com が出た回数",
          "- Search Console 管理画面 → 検索パフォーマンス → 「生成AI機能」フィルタの表示回数と表示ページ数", "- Bing で site:piste-ai.com の件数", ""]
    return "\n".join(L)

def main():
    if len(sys.argv) >= 3:
        start, end = sys.argv[1], sys.argv[2]
    else:
        today = datetime.date.today()
        end = (today - datetime.timedelta(days=2)).isoformat(); start = (today - datetime.timedelta(days=29)).isoformat()
    at = access_token()
    g = ga4(at, start, end); s = gsc(at, start, end)
    out = PROJECT / "audit/reports"; out.mkdir(parents=True, exist_ok=True)
    stem = f"ai_referral_{start.replace('-', '')}-{end.replace('-', '')}"
    (out / f"{stem}.json").write_text(json.dumps({"start": start, "end": end, "ga4": g, "gsc": s}, ensure_ascii=False, indent=1))
    (out / f"{stem}.md").write_text(md(start, end, g, s))
    print(f"wrote {out / stem}.md")
    print("GA4:", "OK" if not g["error"] else f"error {g['error'].get('error')}", "| AI sessions:", sum(a["sessions"] for a in g["ai_sessions"]) if not g["error"] else "-")
    for site, d in s.items():
        print("GSC", site, ":", "error" if "error" in d else f"clicks {d['total'].get('clicks', 0)} imp {d['total'].get('impressions', 0)}")

if __name__ == "__main__":
    main()
