#!/usr/bin/env python3
"""sitemap.xml の全 URL を Search Console の URL 検査 API にかけ、索引状態を集計する。

使い方:
    python3 tools/gsc_index_check.py            # audit/reports/index_check_YYYYMMDD.json に保存
    python3 tools/gsc_index_check.py out.json   # 保存先を指定

前提: ~/.claude/credentials/google_searchconsole_token.json（tools/google_oauth_gsc.py で作成）。
      1 URL ずつ問い合わせるため 180 URL で 10〜15 分かかる。1日 2,000 URL が上限。
"""
import collections, datetime, json, re, sys, time, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ai_referral_report import access_token, api

SITE = "https://www.piste-ai.com/"

def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "audit/reports" / f"index_check_{datetime.date.today():%Y%m%d}.json"
    at = access_token()
    urls = re.findall(r"<loc>([^<]+)</loc>", urllib.request.urlopen(SITE + "sitemap.xml").read().decode())
    res = {}
    for i, u in enumerate(urls, 1):
        r = api(at, "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect", {"inspectionUrl": u, "siteUrl": SITE, "languageCode": "ja"})
        if "error" in r:
            res[u] = {"error": r}
            if r["error"] == 429: time.sleep(10)
        else:
            ir = r.get("inspectionResult", {}).get("indexStatusResult", {})
            res[u] = {k: ir.get(k) for k in ("verdict", "coverageState", "lastCrawlTime", "googleCanonical", "indexingState")}
        print(f"\r{i}/{len(urls)}", end="", file=sys.stderr, flush=True)
    print(file=sys.stderr)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1))
    cnt = collections.Counter((v.get("verdict"), v.get("coverageState")) if "error" not in v else ("error", str(v["error"].get("error"))) for v in res.values())
    print(f"URLs {len(urls)}  saved {out}")
    for k, n in cnt.most_common(): print(f"  {n:>4} {k}")
    wk = collections.Counter()
    for v in res.values():
        c = (v.get("lastCrawlTime") or "")[:10]
        if c: wk[datetime.date.fromisoformat(c).isocalendar()[1]] += 1
    print("  最終クロール日の ISO 週別:", dict(sorted(wk.items())))
    for state in ("URL が Google に認識されていません", "クロール済み - インデックス未登録"):
        L = [u.replace(SITE, "/") for u, v in res.items() if v.get("coverageState") == state]
        if L: print(f"  {state} ({len(L)}):"); [print("    ", u) for u in L]
    mm = [u.replace(SITE, "/") for u, v in res.items() if v.get("googleCanonical") and v["googleCanonical"] != u]
    if mm: print(f"  Google が別 URL を正規と判断 ({len(mm)}):"); [print("    ", u) for u in mm]

if __name__ == "__main__":
    main()
