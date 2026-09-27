#!/usr/bin/env python3
"""piste-ai.com の Microsoft Clarity 定量データ（Data Export API）を取得して保存する。

毎日1回実行する想定。API は「直近24時間（numOfDays=1）」の集計を返す。
Clarity の制限は 1プロジェクト 10リクエスト/日 なので、1回の実行で5リクエストに抑え、
同日の保存済みデータがあれば再取得しない（--force で上書き）。

出力:
  audit/clarity/raw/YYYYMMDD_{dimension}.json   API レスポンスそのまま
  audit/clarity/YYYYMMDD_piste_ai_clarity.md     人が読む日次レポート
  audit/clarity/daily_metrics.csv                全体指標の日次推移（1日1行）

トークン: ~/.claude/credentials/clarity_piste_ai_token.json
  {"project_id": "w54yutjekb", "jwt_token": "<Clarity の Data Export トークン>"}
"""

import argparse
import csv
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "audit" / "clarity"
RAW = OUT / "raw"
CSV_PATH = OUT / "daily_metrics.csv"
TOKEN_PATH = Path.home() / ".claude" / "credentials" / "clarity_piste_ai_token.json"
API = "https://www.clarity.ms/export-data/api/v1/project-live-insights"

# (保存名, dimension1)。None は全体集計
DIMENSIONS = [
    ("total", None),
    ("url", "URL"),
    ("device", "Device"),
    ("channel", "Channel"),
    ("source", "Source"),
]

CSV_FIELDS = [
    "date", "sessions", "bot_sessions", "users", "pages_per_session",
    "scroll_depth", "total_time", "active_time",
    "dead_click_pct", "rage_click_pct", "quickback_pct",
    "excessive_scroll_pct", "script_error_pct", "error_click_pct",
]

# メトリクス名 → CSV 列（sessionsWithMetricPercentage を入れる）
PCT_METRICS = {
    "DeadClickCount": "dead_click_pct",
    "RageClickCount": "rage_click_pct",
    "QuickbackClick": "quickback_pct",
    "ExcessiveScroll": "excessive_scroll_pct",
    "ScriptErrorCount": "script_error_pct",
    "ErrorClickCount": "error_click_pct",
}

METRIC_LABELS = {
    "Traffic": "トラフィック",
    "ScrollDepth": "スクロール深度",
    "EngagementTime": "エンゲージメント時間",
    "DeadClickCount": "デッドクリック",
    "RageClickCount": "レイジクリック",
    "QuickbackClick": "クイックバック",
    "ExcessiveScroll": "過剰スクロール",
    "ScriptErrorCount": "スクリプトエラー",
    "ErrorClickCount": "エラークリック",
}


def load_token():
    if not TOKEN_PATH.exists():
        sys.exit(f"TOKEN_MISSING: {TOKEN_PATH} がありません。Clarity の設定 → データエクスポート でトークンを発行して保存してください。")
    data = json.loads(TOKEN_PATH.read_text())
    token = data.get("jwt_token", "").strip()
    if not token:
        sys.exit(f"TOKEN_MISSING: {TOKEN_PATH} の jwt_token が空です。")
    return token


def fetch(token, dimension):
    url = API + "?numOfDays=1" + (f"&dimension1={dimension}" if dimension else "")
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode("utf-8", "replace")[:500]}


def metrics_by_name(payload):
    if not isinstance(payload, list):
        return {}
    return {m.get("metricName"): m.get("information") or [] for m in payload}


def fmt(v):
    if v is None or v == "":
        return "-"
    try:
        f = float(v)
        return f"{int(f):,}" if f.is_integer() else f"{f:,.2f}"
    except (TypeError, ValueError):
        return str(v).replace("|", "\\|")


def table(rows):
    if not rows:
        return "（データなし）\n"
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    lines = ["| " + " | ".join(keys) + " |", "|" + "---|" * len(keys)]
    for r in rows:
        lines.append("| " + " | ".join(fmt(r.get(k)) for k in keys) + " |")
    return "\n".join(lines) + "\n"


def summary_row(date, total):
    m = metrics_by_name(total)
    row = {k: "" for k in CSV_FIELDS}
    row["date"] = date
    t = (m.get("Traffic") or [{}])[0]
    row["sessions"] = t.get("totalSessionCount", "")
    row["bot_sessions"] = t.get("totalBotSessionCount", "")
    row["users"] = t.get("distinctUserCount", "")
    row["pages_per_session"] = t.get("pagesPerSessionPercentage", "")
    row["scroll_depth"] = (m.get("ScrollDepth") or [{}])[0].get("averageScrollDepth", "")
    e = (m.get("EngagementTime") or [{}])[0]
    row["total_time"] = e.get("totalTime", "")
    row["active_time"] = e.get("activeTime", "")
    for name, col in PCT_METRICS.items():
        row[col] = (m.get(name) or [{}])[0].get("sessionsWithMetricPercentage", "")
    return row


def write_csv(row):
    rows = []
    if CSV_PATH.exists():
        with CSV_PATH.open(newline="") as f:
            rows = [r for r in csv.DictReader(f) if r.get("date") != row["date"]]
    rows.append(row)
    rows.sort(key=lambda r: r["date"])
    with CSV_PATH.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="同日の保存済みデータがあっても再取得する")
    args = ap.parse_args()

    now = datetime.now()
    ymd = now.strftime("%Y%m%d")
    date = now.strftime("%Y-%m-%d")
    report = OUT / f"{ymd}_piste_ai_clarity.md"
    if report.exists() and not args.force:
        print(f"SKIP: 本日分は取得済み {report}")
        return

    token = load_token()
    RAW.mkdir(parents=True, exist_ok=True)

    results, statuses = {}, []
    for key, dim in DIMENSIONS:
        status, payload = fetch(token, dim)
        statuses.append(f"{dim or '全体'}: HTTP {status}")
        if status != 200:
            if status in (401, 403):
                sys.exit(f"AUTH_ERROR: HTTP {status}。トークンが無効か期限切れです。{TOKEN_PATH} を更新してください。")
            if status == 429:
                sys.exit("RATE_LIMIT: 本日の API 上限（10回/日）に達しています。明日再実行してください。")
            print(f"WARN: {dim or '全体'} の取得に失敗 HTTP {status}", file=sys.stderr)
            continue
        (RAW / f"{ymd}_{key}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2))
        results[key] = payload

    if "total" not in results:
        sys.exit("FETCH_ERROR: 全体集計が取得できませんでした: " + " / ".join(statuses))

    row = summary_row(date, results["total"])
    write_csv(row)

    lines = [
        "# piste-ai.com Clarity 定量データ",
        "",
        f"- 取得日時: {now.strftime('%Y-%m-%d %H:%M')}",
        "- 対象期間: 取得時点から直近24時間（numOfDays=1）",
        "- プロジェクト: w54yutjekb（https://www.piste-ai.com/）",
        f"- API: {' / '.join(statuses)}",
        "",
        "## 全体サマリー",
        "",
        "| 指標 | 値 |",
        "|---|---|",
        f"| セッション | {fmt(row['sessions'])} |",
        f"| ボットセッション | {fmt(row['bot_sessions'])} |",
        f"| ユーザー | {fmt(row['users'])} |",
        f"| ページ/セッション | {fmt(row['pages_per_session'])} |",
        f"| 平均スクロール深度（%） | {fmt(row['scroll_depth'])} |",
        f"| 合計時間 / アクティブ時間（秒） | {fmt(row['total_time'])} / {fmt(row['active_time'])} |",
        f"| デッドクリック発生率（%） | {fmt(row['dead_click_pct'])} |",
        f"| レイジクリック発生率（%） | {fmt(row['rage_click_pct'])} |",
        f"| クイックバック発生率（%） | {fmt(row['quickback_pct'])} |",
        f"| 過剰スクロール発生率（%） | {fmt(row['excessive_scroll_pct'])} |",
        f"| スクリプトエラー発生率（%） | {fmt(row['script_error_pct'])} |",
        f"| エラークリック発生率（%） | {fmt(row['error_click_pct'])} |",
        "",
    ]
    for key, dim in DIMENSIONS[1:]:
        lines += [f"## {dim} 別", ""]
        if key not in results:
            lines += ["（取得失敗）", ""]
            continue
        for name, info in metrics_by_name(results[key]).items():
            if not info:
                continue
            lines += [f"### {METRIC_LABELS.get(name, name)}", "", table(info)]
    report.write_text("\n".join(lines))
    print(f"OK: {report}")
    print(f"sessions={row['sessions']} users={row['users']} scroll={row['scroll_depth']}")


if __name__ == "__main__":
    main()
