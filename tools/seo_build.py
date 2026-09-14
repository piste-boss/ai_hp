#!/usr/bin/env python3
"""SEO / AIO 後処理ビルド（冪等）。site/ 配下を直接書き換える。

やること
 1. ブログ記事の <head> を正規化: GA4 + Clarity、短縮 title、canonical、OGP、Twitter Card、
    JSON-LD（Organization / Person / WebSite / BlogPosting / BreadcrumbList / FAQPage）、RSS alternate
 2. 記事本文にパンくず・公開日・著者・「この記事でわかること」・関連記事3本を挿入
 3. 記事内画像を WebP に差し替え、width / height / loading を付与
 4. ブログ一覧にカテゴリナビを追加し、カテゴリ別一覧ページを生成
 5. トップページ・ブログ一覧のカード画像を軽量 WebP に差し替え
 6. sitemap.xml / feed.xml / llms.txt を再生成

使い方: python3 tools/seo_build.py   （tools/optimize_images.py を先に実行しておく）
"""
from __future__ import annotations
import html as H
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent / "site"
BLOG = ROOT / "blog"
IMG = ROOT / "images"
SITE = "https://www.piste-ai.com"
BRAND = "Piste AI EVANGELISTS"
COMPANY = "株式会社Piste"
GA_ID = "G-LR35246V7B"
CLARITY_ID = "w54yutjekb"
JST = timezone(timedelta(hours=9))
ORG_ID = f"{SITE}/#organization"
PERSON_ID = f"{SITE}/about.html#person"
WEBSITE_ID = f"{SITE}/#website"
SAME_AS = [
    "https://x.com/piste_ai_boss",
    "https://www.instagram.com/piste_ai",
    "https://www.threads.com/@piste_ai",
    "https://coconala.com/users/2208051",
    "https://lin.ee/Pul5f6V",
]
PHONE = "+81-566-48-6580"
MODIFIED_FILE = Path(__file__).resolve().parent / "modified.json"   # {slug: "YYYY-MM-DD"} 実質的な内容変更日
MODIFIED = json.loads(MODIFIED_FILE.read_text()) if MODIFIED_FILE.exists() else {}
KEYPOINTS_DIR = Path(__file__).resolve().parent / "keypoints"       # {slug}.json {"target","outcome","requirement"}
ADDRESS = {
    "@type": "PostalAddress",
    "postalCode": "447-0042",
    "addressRegion": "愛知県",
    "addressLocality": "碧南市",
    "streetAddress": "中後町3-3 中央ビル1F",
    "addressCountry": "JP",
}

# ---------------------------------------------------------------- カテゴリ定義
CATEGORIES = [
    ("tool-integration", "ツール連携", "Claude Code と業務ツール（会計・EC・SNS・チャット・予約など）をつなぐ自動化ガイド"),
    ("claude-code-basics", "Claude Codeの使い方", "CLAUDE.md・権限・スキル・サブエージェントなど、Claude Code を業務で安全に使いこなすための基礎"),
    ("finance", "経理・財務・資金", "資金繰り・粗利・固定費・請求書・インボイス・補助金など、お金まわりの整理と判断材料づくり"),
    ("sales-customer", "営業・顧客対応", "失注分析・休眠顧客・クレーム対応・顧客名簿・アンケートなど、売上と顧客に関わる記録の整え方"),
    ("operations", "業務記録・現場改善", "ヒヤリハット・不良品・点検・納期・外注先・仕様変更など、現場の記録を一覧にして改善につなげる方法"),
    ("ai-basics", "AI導入の基礎", "AI導入の失敗パターン・費用対効果・プロンプト術・ツール選定など、これから AI を使う中小企業向けの入門"),
]
CAT_BY_SLUG = {c[0]: c for c in CATEGORIES}

CAT_RULES = {
    "claude-code-basics": [
        "business-guide", "claude-md-rules", "claudemd-memory", "context-management", "hooks-automation",
        "loop-scheduler", "model-cost", "permission-security", "plan-mode", "playwright-automation",
        "remote-control", "skills-knowledge", "slash-commands", "subagent-team", "team-parallel",
        "websearch-research", "troubleshooting", "task-delegation", "confidential-data", "backup-and-recovery",
        "deliverable-review", "automation-handover", "automation-inventory", "automation-effect",
    ],
    "finance": [
        "cashflow", "gross-margin", "fixed-cost", "loan-repayment", "receivables", "invoice-amount",
        "invoice-registration", "denshi-chobo", "price-revision", "quote-comparison", "subsidy",
        "new-client-credit", "ai-accounting-automation", "ai-cost-roi",
    ],
    "sales-customer": [
        "lost-deal", "dormant-customer", "complaint-first", "customer-list", "survey-freetext",
        "contract-renewal", "ai-sales-email", "ai-customer-support", "ai-sns-marketing", "ai-sales-growth",
        "ai-competitor",
    ],
    "operations": [
        "near-miss", "returns-defect", "equipment-inspection", "spec-change", "subcontractor",
        "delivery-delay", "paper-document", "bcp-", "ai-inventory", "ai-meeting-minutes", "ai-knowledge",
        "ai-contract-review", "ai-presentation", "ai-data-analysis", "ai-recruitment",
    ],
    "ai-basics": ["ai-adoption-mistakes", "ai-automation-one-person", "ai-prompt-techniques", "ai-tools-for-business"],
}

def categorize(slug: str) -> str:
    if "-integration" in slug or "discord-notification" in slug or slug == "moneyforward-mcp-accounting":
        return "tool-integration"
    for cat, keys in CAT_RULES.items():
        if any(k in slug for k in keys):
            return cat
    return "ai-basics"

# ---------------------------------------------------------------- 短縮タイトル
TITLE_OVERRIDES = {
    # 自動短縮で意味が落ちるものは手で指定
    "claude-code-cybozu-office-integration": "Claude Code × サイボウズ Office連携で申請・掲示板を自動化",
    "claude-code-google-business-profile-integration": "Claude Code × Googleビジネスプロフィールで口コミ返信を自動化",
    "claude-code-google-calendar-integration": "Claude Code × Googleカレンダー連携で予定調整を自動化",
    "claude-code-google-docs-integration": "Claude Code × Googleドキュメント連携で議事録作成を自動化",
    "claude-code-google-drive-integration": "Claude Code × Googleドライブ連携で資料整理を自動化",
    "claude-code-hotpepper-beauty-integration": "Claude Code × ホットペッパービューティーで口コミ返信を自動化",
    "claude-code-food-delivery-integration": "Claude Code × フードデリバリー連携でメニュー文を自動化",
    "claude-code-microsoft-teams-integration": "Claude Code × Microsoft Teams連携で会議要約を自動化",
    "claude-code-rakuraku-seisan-integration": "Claude Code × 楽楽精算連携で経費精算をAI自動化",
    "claude-code-timee-integration": "Claude Code × タイミー連携で募集文・手順書をAI自動化",
    "claude-code-zoho-integration": "Claude Code × Zoho連携で顧客管理・見積請求をAI自動化",
    "claude-code-etsy-integration": "Claude Code × Etsy連携で海外販売・英語商品ページを自動化",
    "claude-code-linkedin-integration": "Claude Code × LinkedIn連携で情報発信・B2Bリード獲得を自動化",
    "claude-code-wantedly-integration": "Claude Code × Wantedly連携で採用広報・記事作成を自動化",
    "claude-code-colorme-integration": "Claude Code × カラーミーショップ連携で受注対応を自動化",
    "claude-code-jalan-integration": "Claude Code × じゃらん連携で宿泊プラン・口コミ返信を自動化",
    "claude-code-andpad-integration": "Claude Code × ANDPAD連携で工事日報・写真整理を自動化",
    "claude-code-make-integration": "Claude Code × Make連携で複数ステップの業務自動化を設計",
    "claude-code-ga4-analytics-integration": "Claude Code × GA4連携でアクセス解析・改善提案を自動化",
    "claude-code-search-console-integration": "Claude Code × サーチコンソール連携でSEO改善を自動化",
    "claude-code-line-official-integration": "Claude Code × LINE公式アカウント連携で顧客対応を自動化",
    "claude-code-lineworks-integration": "Claude Code × LINE WORKS連携で社内チャットを自動化",
    "claude-code-mcp-integration": "Claude CodeのMCP連携で業務ツールを統合するガイド",
    "claude-code-playwright-automation": "Claude CodeのPlaywright連携でブラウザ業務を自動化",
    "claude-code-loop-scheduler-automation": "Claude Codeの/loop機能で業務を24時間自動運転する",
    "claude-code-model-cost-optimization": "Claude CodeのOpus・Sonnet・Haiku使い分けでコスト削減",
    "claude-code-context-management": "Claude Codeで作業が長引くと精度が落ちる原因とコンテキスト管理",
    "claude-code-troubleshooting-guide": "Claude Codeの自動化が止まった・結果がおかしいときの対処法",
    "claude-code-task-delegation-boundary": "Claude Codeに任せる仕事と人がやる仕事の線引きガイド",
    "claude-code-confidential-data-rules": "Claude Codeに社内のどの情報まで渡してよい？機密情報の取り扱い",
    "claude-code-deliverable-review-process": "Claude Codeが出した成果物は誰がどう確認する？検収体制づくり",
    "claude-code-automation-effect-tracking": "Claude Codeの自動化は結局どれだけ効いた？削減時間の記録ガイド",
    "claude-code-automation-handover": "Claude Codeで組んだ自動化を担当者以外でも動かせる引き継ぎ設計",
    "claude-code-automation-inventory-cleanup": "Claude Codeで増やした自動化を棚卸しする方法",
    "claude-code-backup-and-recovery": "Claude Codeに任せた作業を元に戻せるバックアップと復旧",
    "claude-code-denshi-chobo-compliance": "Claude Codeで電子帳簿保存法のファイル名づけを自動化",
    "claude-code-bcp-emergency-preparedness": "Claude CodeでBCP（事業継続計画）の下地をつくる",
    "claude-code-invoice-registration-check": "Claude Codeで受け取った請求書のインボイス登録番号を確かめる",
    "claude-code-invoice-amount-reconciliation": "Claude Codeで請求書と発注内容の食い違いを見つける",
    "moneyforward-mcp-accounting": "マネーフォワード×MCP連携でClaude Codeが会計業務を自動化",
    "ai-prompt-techniques-business": "ChatGPTへの指示の出し方で成果が変わる！ビジネスプロンプト術",
}

def disp_w(s: str) -> float:
    """半角 0.5 / 全角 1 で表示幅を数える（検索結果の表示目安は全角32文字前後）"""
    return sum(0.5 if ord(c) < 0x2E80 else 1 for c in s)

MAX_W = 33

def short_title(slug: str, title: str) -> str:
    if slug in TITLE_OVERRIDES:
        return TITLE_OVERRIDES[slug]
    t = title
    if disp_w(t) <= MAX_W:
        return t
    head = re.split(r"[！!]", t, maxsplit=1)[0]
    if disp_w(head) <= MAX_W:
        return head
    m = re.match(r"(Claude Code × .+?連携で)(.+?)(をAI自動化|を自動化|をAI自動運用|をAIに.+)$", head)
    if m:
        items = m.group(2).split("・")
        for n in range(len(items), 0, -1):
            cand = m.group(1) + "・".join(items[:n]) + "をAI自動化"
            if disp_w(cand) <= MAX_W:
                return cand
    return head

# ---------------------------------------------------------------- ユーティリティ
def strip_tags(s: str) -> str:
    s = re.sub(r"<br\s*/?>", "", s)
    s = re.sub(r"<[^>]+>", "", s)
    return H.unescape(s).strip()

def esc(s: str) -> str:
    return H.escape(s, quote=True)

def img_size(path: Path):
    try:
        with Image.open(path) as im:
            return im.width, im.height
    except Exception:
        return None

def jsonld(obj) -> str:
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>"

def org_node():
    return {
        "@type": ["Organization", "ProfessionalService"],
        "@id": ORG_ID,
        "name": COMPANY,
        "alternateName": BRAND,
        "url": SITE + "/",
        "logo": {"@type": "ImageObject", "url": f"{SITE}/images/logo.png", "width": 640, "height": 640},
        "image": f"{SITE}/images/ogp.jpg",
        "email": "info@piste-ai.com",
        "telephone": PHONE,
        "address": ADDRESS,
        "areaServed": [{"@type": "Country", "name": "日本"}, {"@type": "AdministrativeArea", "name": "愛知県"}],
        "founder": {"@id": PERSON_ID},
        "sameAs": SAME_AS,
        "knowsAbout": ["AI導入コンサルティング", "Claude Code", "業務自動化", "AI研修", "中小企業のDX"],
        "description": "中小企業のためのAI導入コンサルティング。Claude Code を中心に、相談・実装・定着までマンツーマンで伴走します。Anthropic 公式パートナーネットワーク認定企業。",
    }

def person_node():
    return {
        "@type": "Person",
        "@id": PERSON_ID,
        "name": "石川 卓",
        "alternateName": "いしかわ すぐる",
        "url": f"{SITE}/about.html",
        "image": f"{SITE}/images/profile.jpg",
        "jobTitle": "代表取締役 / AIコンサルタント",
        "worksFor": {"@id": ORG_ID},
        "alumniOf": {"@type": "CollegeOrUniversity", "name": "岐阜大学大学院 工学研究科"},
        "knowsAbout": ["Claude Code", "生成AIの業務活用", "中小企業のAI導入", "業務自動化", "AI研修"],
        "description": "岐阜大学工学部修士課程修了後、大手鉄鋼メーカーで約8年エンジニアとして勤務。独立後、AIエンジニア・コンサルタントとして400社以上のAI導入を支援（2026年9月時点）。フィットネスクラブ経営者としても自社業務をAIで自動化している。",
        "sameAs": SAME_AS,
    }

def website_node():
    return {"@type": "WebSite", "@id": WEBSITE_ID, "url": SITE + "/", "name": BRAND, "publisher": {"@id": ORG_ID}, "inLanguage": "ja"}

TRACKING = f"""
  <!-- Google Analytics -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{GA_ID}');
  </script>
  <!-- Microsoft Clarity -->
  <script type="text/javascript">
    (function(c,l,a,r,i,t,y){{
      c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};
      t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
      y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    }})(window, document, "clarity", "script", "{CLARITY_ID}");
  </script>
"""

SEO_STYLE = """<style id="seo-style">
.seo-breadcrumb{font-size:13px;color:#9a9a9a;margin:0 0 6px;line-height:1.6}
.seo-breadcrumb a{color:#c4a24e;text-decoration:none;margin:0;font-size:13px}
.seo-breadcrumb a:hover{text-decoration:underline}
.seo-postmeta{font-size:13px;color:#9a9a9a;margin:0 0 18px;display:flex;flex-wrap:wrap;gap:6px 18px}
.seo-postmeta a{color:#d4b96a;text-decoration:underline;text-underline-offset:3px}
body > footer{color:#a9a9a9}
.seo-keypoints{background:#232323;border-left:4px solid #c4a24e;border-radius:8px;padding:16px 20px;margin:0 0 30px}
.seo-keypoints-title{font-weight:700;color:#d4b96a;margin:0 0 8px;font-size:15px}
.seo-keypoints ul{margin:0 0 0 20px;padding:0}
.seo-keypoints li{margin-bottom:4px;color:#e2e2e2;font-size:15px}
.seo-related{margin:52px 0 12px}
.seo-related h2{font-size:20px;color:#d4b96a;border-bottom:1px solid #3a3a3a;padding-bottom:8px;margin:0 0 16px}
.seo-related-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
@media(max-width:640px){.seo-related-grid{grid-template-columns:1fr}}
.seo-related-card{display:block;background:#2c2c2c;border:1px solid #444;border-radius:10px;overflow:hidden;text-decoration:none;color:#eee}
.seo-related-card:hover{border-color:#c4a24e}
.seo-related-card img{width:100%;height:auto;display:block;aspect-ratio:3/2;object-fit:cover}
.seo-related-cat{display:block;font-size:11px;color:#c4a24e;padding:10px 12px 0;letter-spacing:.04em}
.seo-related-title{display:block;font-size:14px;line-height:1.5;padding:4px 12px 12px;font-weight:600}
.seo-related-more{margin:14px 0 0;font-size:14px}
.seo-related-more a{color:#c4a24e}
</style>"""

# ---------------------------------------------------------------- 記事の読み込み
class Article:
    def __init__(self, path: Path, dates: dict, thumbs: dict | None = None):
        self.path = path
        self.slug = path.stem
        self.url = f"{SITE}/blog/{self.slug}.html"
        s = path.read_text(encoding="utf-8")
        self.src = s
        m = re.search(r"<title>(.*?)</title>", s, re.S)
        t = strip_tags(m.group(1)) if m else self.slug
        t = re.sub(r"\s*\|\s*(Piste AI EVANGELISTS|Piste)\s*$", "", t).strip()
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S)
        self.title = strip_tags(h1.group(1)) if h1 and len(strip_tags(h1.group(1))) >= len(t) - 2 else t
        self.short = short_title(self.slug, self.title)
        d = re.search(r'name="description"\s+content="([^"]*)"', s)
        self.description = H.unescape(d.group(1)) if d else ""
        k = re.search(r'name="keywords"\s+content="([^"]*)"', s)
        self.keywords = [x.strip() for x in H.unescape(k.group(1)).split(",") if x.strip()] if k else []
        published = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', s)
        self.date = dates.get(self.slug) or (published[1].replace('-', '.') if published else None)
        if not self.date:
            raise ValueError(f"公開日が不明です。ブログ一覧の日付を確認してください: {self.slug}")
        y, mo, dd = self.date.split(".")
        self.iso = f"{y}-{mo}-{dd}"
        self.iso_dt = f"{self.iso}T09:00:00+09:00"
        modified = re.search(r'"dateModified"\s*:\s*"([^"]+)"', s)
        self.modified_dt = modified[1] if modified else self.iso_dt
        mod_override = MODIFIED.get(self.slug)
        if mod_override and mod_override > self.modified_dt[:10]:
            self.modified_dt = f"{mod_override}T09:00:00+09:00"
        self.category = categorize(self.slug)
        self.cat_name = CAT_BY_SLUG[self.category][1]
        thumb = IMG / f"blog-{self.slug}.jpg"
        if thumb.exists():
            self.thumb_base = f"blog-{self.slug}"
        elif thumbs and thumbs.get(self.slug) and (IMG / (thumbs[self.slug] + ".jpg")).exists():
            self.thumb_base = thumbs[self.slug]
        else:
            self.thumb_base = "ogp"
        body = s.split("<body", 1)[1] if "<body" in s else s
        self.h2s = [strip_tags(x) for x in re.findall(r"<h2[^>]*>(.*?)</h2>", body, re.S)]
        self.points = [h for h in self.h2s if h and not re.search(r"目次|よくある|まとめ|導入サポート|関連記事|相談", h)][:3]
        self.faq = self._faq(body)
        self.wordcount = len(re.sub(r"\s", "", strip_tags(re.sub(r"<(script|style)[^>]*>.*?</\1>", "", body, flags=re.S))))

    def _faq(self, body: str):
        m = re.search(r"<h2[^>]*>[^<]*(?:よくある質問|よくあるご質問|FAQ)[^<]*</h2>(.*?)(?=<h2|<div class=\"cta\"|<footer|<!-- seo:related -->)", body, re.S)
        if not m:
            return []
        out = []
        # 形式B: <div class="faq-item"><p class="q">…</p><p class="a">…</p></div>
        for q, a in re.findall(r'<p class="q">(.*?)</p>\s*<p class="a">(.*?)</p>', m.group(1), re.S):
            q, a = strip_tags(q), strip_tags(a)
            q = re.sub(r"^Q[.．:：]?\s*", "", q); a = re.sub(r"^A[.．:：]?\s*", "", a)
            if q and a:
                out.append((q, a))
        if out:
            return out
        # 形式C: <p><strong>質問</strong></p><p>回答</p>  形式D: <p><strong>Q. 質問</strong><br>回答</p>
        for mm in re.finditer(r"<p[^>]*>\s*<strong>(.*?)</strong>\s*(?:<br\s*/?>\s*(.*?)</p>|</p>\s*<p[^>]*>(?!\s*<strong>)(.*?)</p>)", m.group(1), re.S):
            q = re.sub(r"^Q[.．:：]?\s*", "", strip_tags(mm.group(1)))
            a = strip_tags(mm.group(2) or mm.group(3) or "")
            a = re.sub(r"^A[.．:：]?\s*", "", a)
            if q and a and len(q) < 120:
                out.append((q, a))
        if out:
            return out
        for q, a in re.findall(r"<h3[^>]*>(.*?)</h3>\s*((?:<p[^>]*>.*?</p>\s*)+)", m.group(1), re.S):
            q = re.sub(r"^Q[.．:：]?\s*", "", strip_tags(q))
            a = " ".join(strip_tags(p) for p in re.findall(r"<p[^>]*>(.*?)</p>", a, re.S))
            a = re.sub(r"^A[.．:：]?\s*", "", a)
            if q and a:
                out.append((q, a))
        return out

    # ---- 画像
    def og_image(self):
        og = IMG / f"{self.thumb_base}-og.jpg"
        if og.exists():
            return f"{SITE}/images/{self.thumb_base}-og.jpg", img_size(og)
        return f"{SITE}/images/{self.thumb_base}.jpg", img_size(IMG / f"{self.thumb_base}.jpg")

    def card_image(self):
        c = IMG / f"{self.thumb_base}-card.webp"
        if c.exists():
            return f"{self.thumb_base}-card.webp", img_size(c)
        return f"{self.thumb_base}.jpg", img_size(IMG / f"{self.thumb_base}.jpg")


def load_dates() -> dict:
    idx = (BLOG / "index.html").read_text(encoding="utf-8")
    return {m.group(1): m.group(2) for m in re.finditer(r'<a href="([a-z0-9-]+)(?:\.html)?">.*?class="blog-date">([0-9.]+)<', idx, re.S)}

def load_thumbs() -> dict:
    """ブログ一覧のカード画像からスラッグ→画像ベース名を得る（jpg / -card.webp どちらでも）"""
    idx = (BLOG / "index.html").read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r'<a href="([a-z0-9-]+)(?:\.html)?">\s*<div class="blog-thumb"><img src="\.\./images/([^"]+?)(?:-card)?\.(?:jpg|webp)"', idx, re.S):
        out[m.group(1)] = m.group(2)
    return out


# ---------------------------------------------------------------- 関連記事
def related(a: Article, arts: list[Article], n=3):
    def score(b: Article):
        s = 0
        if b.category == a.category:
            s += 3
        s += len(set(a.keywords) & set(b.keywords))
        ta = set(re.findall(r"[一-龠ぁ-んァ-ヶA-Za-z0-9]{2,}", a.title))
        tb = set(re.findall(r"[一-龠ぁ-んァ-ヶA-Za-z0-9]{2,}", b.title))
        s += len(ta & tb) * 0.5
        return s
    cands = [b for b in arts if b.slug != a.slug]
    cands.sort(key=lambda b: (-score(b), b.iso), reverse=False)
    cands.sort(key=lambda b: -score(b))
    return cands[:n]


# ---------------------------------------------------------------- head の正規化
HEAD_STRIP = [
    r"<!--\s*Google Analytics\s*-->",
    r"<!--\s*Microsoft Clarity\s*-->",
    r'<script[^>]*src="https://www\.googletagmanager\.com/gtag/js[^"]*"[^>]*>\s*</script>',
    r"<script>\s*window\.dataLayer[^<]*?gtag\('config'[^<]*?</script>",
    r"<script[^>]*>\s*\(function\(c,l,a,r,i,t,y\).*?</script>",
    r'<link rel="canonical"[^>]*>',
    r'<meta property="og:[^>]*>',
    r'<meta name="twitter:[^>]*>',
    r'<link rel="alternate" type="application/rss\+xml"[^>]*>',
    r'<script type="application/ld\+json">.*?</script>',
    r"<!-- seo:head -->.*?<!-- /seo:head -->",
    r'<style id="seo-style">.*?</style>',
]

def build_head(a: Article, rel: list[Article]) -> str:
    og_url, og_wh = a.og_image()
    cat_slug, cat_name, _ = CAT_BY_SLUG[a.category]
    graph = [org_node(), person_node(), website_node()]
    post = {
        "@type": "BlogPosting",
        "@id": a.url + "#article",
        "mainEntityOfPage": {"@type": "WebPage", "@id": a.url},
        "url": a.url,
        "headline": a.title[:110],
        "alternativeHeadline": a.short,
        "description": a.description,
        "image": {"@type": "ImageObject", "url": og_url, **({"width": og_wh[0], "height": og_wh[1]} if og_wh else {})},
        "datePublished": a.iso_dt,
        "dateModified": a.modified_dt,
        "author": {"@id": PERSON_ID},
        "publisher": {"@id": ORG_ID},
        "isPartOf": {"@id": WEBSITE_ID},
        "inLanguage": "ja",
        "articleSection": cat_name,
        "keywords": a.keywords,
        "wordCount": a.wordcount,
        "isAccessibleForFree": True,
        "audience": {"@type": "BusinessAudience", "audienceType": "中小企業・個人事業主"},
    }
    if "Claude Code" in a.title:
        post["about"] = [{
            "@type": "SoftwareApplication", "name": "Claude Code", "applicationCategory": "DeveloperApplication",
            "operatingSystem": "macOS, Windows, Linux",
            "creator": {"@type": "Organization", "name": "Anthropic", "url": "https://www.anthropic.com/"},
        }]
    graph.append(post)
    graph.append({
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "ホーム", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "ブログ", "item": SITE + "/blog/"},
            {"@type": "ListItem", "position": 3, "name": cat_name, "item": f"{SITE}/blog/category-{cat_slug}.html"},
            {"@type": "ListItem", "position": 4, "name": a.short, "item": a.url},
        ],
    })
    if a.faq:
        graph.append({
            "@type": "FAQPage",
            "@id": a.url + "#faq",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in a.faq],
        })
    ld = jsonld({"@context": "https://schema.org", "@graph": graph})
    return f"""<!-- seo:head -->
  <link rel="canonical" href="{a.url}">
  <link rel="alternate" type="application/rss+xml" title="{BRAND} ブログ" href="{SITE}/feed.xml">
  <meta name="author" content="石川 卓">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{esc(a.short)}">
  <meta property="og:description" content="{esc(a.description)}">
  <meta property="og:url" content="{a.url}">
  <meta property="og:image" content="{og_url}">{f'''
  <meta property="og:image:width" content="{og_wh[0]}">
  <meta property="og:image:height" content="{og_wh[1]}">''' if og_wh else ''}
  <meta property="og:site_name" content="{BRAND}">
  <meta property="og:locale" content="ja_JP">
  <meta property="article:published_time" content="{a.iso_dt}">
  <meta property="article:author" content="{SITE}/about.html">
  <meta property="article:section" content="{esc(cat_name)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(a.short)}">
  <meta name="twitter:description" content="{esc(a.description)}">
  <meta name="twitter:image" content="{og_url}">
  {ld}
  {SEO_STYLE}
<!-- /seo:head -->"""


def normalize_head(a: Article, rel: list[Article]) -> str:
    s = a.src
    head, rest = s.split("</head>", 1)
    for pat in HEAD_STRIP:
        head = re.sub(pat, "", head, flags=re.S | re.I)
    head = re.sub(r"\n{3,}", "\n\n", head)
    head = re.sub(r"<title>.*?</title>", f"<title>{esc(a.short)} | {BRAND}</title>", head, count=1, flags=re.S)
    head = re.sub(r'(<meta charset="UTF-8">)', r"\1" + TRACKING.replace("\\", "\\\\"), head, count=1, flags=re.I)
    head = head.rstrip() + "\n" + build_head(a, rel) + "\n"
    return head + "</head>" + rest


# ---------------------------------------------------------------- body の加工
def fmt_jp(iso: str) -> str:
    y, m, d = iso.split("-")
    return f"{int(y)}年{int(m)}月{int(d)}日"

def modified_html(a: Article) -> str:
    m = a.modified_dt[:10]
    if m and m > a.iso:
        return f'<time datetime="{m}">更新日：{fmt_jp(m)}</time>'
    return ""

def meta_block(a: Article) -> str:
    cat_slug, cat_name, _ = CAT_BY_SLUG[a.category]
    return f"""<!-- seo:meta -->
<nav class="seo-breadcrumb" aria-label="パンくずリスト"><a href="../index.html">ホーム</a> › <a href="index.html">ブログ</a> › <a href="category-{cat_slug}.html">{esc(cat_name)}</a></nav>
<p class="seo-postmeta"><time datetime="{a.iso}">公開日：{fmt_jp(a.iso)}</time>{modified_html(a)}<span>著者：<a href="../about.html" rel="author">石川 卓</a>（{COMPANY}）</span></p>
<!-- /seo:meta -->"""

def keypoints_block(a: Article) -> str:
    kp_file = KEYPOINTS_DIR / f"{a.slug}.json"
    if kp_file.exists():
        try:
            kp = json.loads(kp_file.read_text())
        except json.JSONDecodeError:
            kp = {}
        if kp.get("target") and kp.get("outcome") and kp.get("requirement"):
            return f"""<!-- seo:points -->
<div class="seo-keypoints"><p class="seo-keypoints-title">この記事の要点</p><ul><li><strong>対象：</strong>{esc(kp["target"])}</li><li><strong>できるようになること：</strong>{esc(kp["outcome"])}</li><li><strong>必要なもの：</strong>{esc(kp["requirement"])}</li></ul></div>
<!-- /seo:points -->"""
    if not a.points:
        return ""
    lis = "".join(f"<li>{esc(p)}</li>" for p in a.points)
    return f"""<!-- seo:points -->
<div class="seo-keypoints"><p class="seo-keypoints-title">この記事でわかること</p><ul>{lis}</ul></div>
<!-- /seo:points -->"""

def related_block(a: Article, rel: list[Article]) -> str:
    cat_slug, cat_name, _ = CAT_BY_SLUG[a.category]
    cards = []
    for b in rel:
        img, wh = b.card_image()
        wh_attr = f' width="{wh[0]}" height="{wh[1]}"' if wh else ""
        cards.append(
            f'<a class="seo-related-card" href="{b.slug}.html"><img src="../images/{img}" alt=""{wh_attr} loading="lazy">'
            f'<span class="seo-related-cat">{esc(b.cat_name)}</span><span class="seo-related-title">{esc(b.short)}</span></a>'
        )
    return f"""<!-- seo:related -->
<section class="seo-related" aria-labelledby="seo-related-h"><h2 id="seo-related-h">関連記事</h2><div class="seo-related-grid">{''.join(cards)}</div>
<p class="seo-related-more"><a href="category-{cat_slug}.html">「{esc(cat_name)}」の記事一覧を見る</a></p></section>
<!-- /seo:related -->"""

IMG_RE = re.compile(r'<img\b([^>]*?)\s*/?>', re.S)

def swap_images(html: str, prefix: str, first_eager=True) -> str:
    """images/*.jpg|png を WebP へ差し替え、width/height/loading を付与。prefix は "../images/" or "images/"。"""
    count = [0]
    def repl(m):
        attrs = m.group(1)
        sm = re.search(r'src="' + re.escape(prefix) + r'([^"]+?)\.(jpe?g|png|webp)"', attrs)
        if not sm:
            return m.group(0)
        base = sm.group(1)
        if base.endswith("-og"):
            return m.group(0)
        webp = IMG / f"{base}.webp"
        if not webp.exists():
            return m.group(0)
        wh = img_size(webp)
        attrs = attrs.replace(sm.group(0), f'src="{prefix}{base}.webp"')
        attrs = re.sub(r'\s(width|height)="[^"]*"', "", attrs)
        if wh:
            attrs += f' width="{wh[0]}" height="{wh[1]}"'
        count[0] += 1
        is_first = count[0] == 1 and first_eager
        if not re.search(r"\bloading=", attrs):
            attrs += ' loading="eager" fetchpriority="high"' if is_first else ' loading="lazy"'
        elif is_first and 'loading="lazy"' in attrs:
            attrs = attrs.replace('loading="lazy"', 'loading="eager" fetchpriority="high"')
        return f"<img{attrs}>"
    return IMG_RE.sub(repl, html)

def process_article(a: Article, arts: list[Article]) -> str:
    rel = related(a, arts)
    s = normalize_head(a, rel)
    head, body = s.split("</head>", 1)
    for pat in (r"<!-- seo:meta -->.*?<!-- /seo:meta -->\n?", r"<!-- seo:points -->.*?<!-- /seo:points -->\n?", r"<!-- seo:related -->.*?<!-- /seo:related -->\n?"):
        body = re.sub(pat, "", body, flags=re.S)
    # メタ（h1 直後）
    body = re.sub(r"(</h1>)", r"\1\n" + meta_block(a).replace("\\", "\\\\"), body, count=1)
    # 要点（ヒーロー画像の後、なければメタの後）
    kp = keypoints_block(a)
    if kp:
        hero = re.search(r'<div class="blog-hero-image".*?</div>\s*', body, re.S)
        ab = re.search(r'<article class="article-body">\s*', body)
        if hero:
            body = body[:hero.end()] + kp + "\n" + body[hero.end():]
        elif ab:
            body = body[:ab.end()] + kp + "\n" + body[ab.end():]
        else:
            body = body.replace("<!-- /seo:meta -->", "<!-- /seo:meta -->\n" + kp, 1)
    # 関連記事（CTA の前、なければ footer の前）
    rb = related_block(a, rel) + "\n"
    if '<div class="cta">' in body:
        body = body.replace('<div class="cta">', rb + '<div class="cta">', 1)
    elif re.search(r'<section class="cta', body):
        body = re.sub(r'(<section class="cta)', rb.replace("\\", "\\\\") + r"\1", body, count=1)
    else:
        body = re.sub(r"(<footer)", rb.replace("\\", "\\\\") + r"\1", body, count=1)
    # main ランドマーク
    if "<main" not in body and 'role="main"' not in body:
        if '<div class="wrap">' in body:
            body = body.replace('<div class="wrap">', '<div class="wrap" role="main">', 1)
        elif '<article class="article-body">' in body:
            body = body.replace('<article class="article-body">', '<article class="article-body" role="main">', 1)
    # 画像
    body = swap_images(body, "../images/", first_eager=True)
    return head + "</head>" + body


# ---------------------------------------------------------------- ブログ一覧 / カテゴリページ
CARD_RE = re.compile(r'<div class="blog-card"[^>]*>\s*<a href="([^"]+)">.*?</a>\s*</div>', re.S)
CATNAV_STYLE = """
    /* seo:catnav */
    .cat-nav{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin:24px 0 8px}
    .cat-nav a{font-size:0.85em;padding:7px 16px;border:1px solid rgba(196,162,78,0.5);border-radius:999px;color:#e0e0e0;text-decoration:none;background:rgba(196,162,78,0.06)}
    .cat-nav a:hover,.cat-nav a.is-current{background:var(--gold);color:#1a1a1a;border-color:var(--gold)}
    .cat-count{font-size:0.8em;color:#9a9a9a;text-align:center;margin-top:12px}
"""

def cat_nav(current: str | None, counts: dict) -> str:
    links = [f'<a href="index.html"{" class=\"is-current\"" if current is None else ""}>すべて（{sum(counts.values())}）</a>']
    for slug, name, _ in CATEGORIES:
        cur = ' class="is-current"' if slug == current else ""
        links.append(f'<a href="category-{slug}.html"{cur}>{esc(name)}（{counts.get(slug, 0)}）</a>')
    return '<nav class="cat-nav" aria-label="カテゴリ">' + "".join(links) + "</nav>"

def rebuild_card(card: str, a: Article) -> str:
    img, wh = a.card_image()
    def repl(m):
        attrs = m.group(1)
        attrs = re.sub(r'src="[^"]*"', f'src="../images/{img}"', attrs)
        attrs = re.sub(r'\s(width|height|loading)="[^"]*"', "", attrs)
        if wh:
            attrs += f' width="{wh[0]}" height="{wh[1]}"'
        return f'<img{attrs} loading="lazy">'
    card = IMG_RE.sub(repl, card, count=1)
    card = re.sub(r'<div class="blog-card"[^>]*>', f'<div class="blog-card" data-category="{a.category}">', card, count=1)
    return card

def build_blog_index(arts: list[Article], by_slug: dict):
    p = BLOG / "index.html"
    s = p.read_text(encoding="utf-8")
    # 既存のカテゴリナビ・件数表示を除去
    s = re.sub(r'<nav class="cat-nav".*?</nav>\s*', "", s, flags=re.S)
    s = re.sub(r'<p class="cat-count">.*?</p>\s*', "", s, flags=re.S)
    s = re.sub(r"\n\s*/\* seo:catnav \*/.*?(?=\n\s*</style>)", "", s, flags=re.S)
    s = s.replace("</style>", CATNAV_STYLE + "  </style>", 1)
    counts = {}
    for a in arts:
        counts[a.category] = counts.get(a.category, 0) + 1
    cards = {}
    def collect(m):
        slug = m.group(1)[:-5]
        a = by_slug.get(slug)
        if a:
            cards[slug] = rebuild_card(m.group(0), a)
            return cards[slug]
        return m.group(0)
    s = CARD_RE.sub(collect, s)
    s = s.replace('<div class="blog-grid">', cat_nav(None, counts) + '\n    <div class="blog-grid">', 1)
    # head の補強
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', "", s, flags=re.S)
    s = re.sub(r'<link rel="alternate" type="application/rss\+xml"[^>]*>\s*', "", s)
    s = re.sub(r'<meta property="og:image"[^>]*>\s*', "", s)
    ld = jsonld({"@context": "https://schema.org", "@graph": [org_node(), website_node(), {
        "@type": "CollectionPage", "@id": f"{SITE}/blog/", "url": f"{SITE}/blog/", "name": f"ブログ | {BRAND}",
        "isPartOf": {"@id": WEBSITE_ID}, "inLanguage": "ja",
        "description": "中小企業向けの Claude Code・AI活用ガイド。ツール連携、経理・財務、営業・顧客対応、業務記録・現場改善、AI導入の基礎を毎日更新。",
    }, {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "ホーム", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "ブログ", "item": SITE + "/blog/"}]}]})
    extra = (f'<link rel="alternate" type="application/rss+xml" title="{BRAND} ブログ" href="{SITE}/feed.xml">\n'
             f'  <meta property="og:image" content="{SITE}/images/ogp.jpg">\n  {ld}\n')
    s = s.replace('<meta property="og:url" content="https://www.piste-ai.com/blog/">', '<meta property="og:url" content="https://www.piste-ai.com/blog/">\n  ' + extra, 1)
    p.write_text(s, encoding="utf-8")
    # カテゴリページ
    for slug, name, desc in CATEGORIES:
        cs = s
        cs = re.sub(r"<title>.*?</title>", f"<title>{esc(name)}の記事一覧 | {BRAND}</title>", cs, count=1, flags=re.S)
        cs = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(desc)}。{BRAND} のブログ「{esc(name)}」カテゴリの記事一覧です。">', cs, count=1)
        cs = cs.replace('<link rel="canonical" href="https://www.piste-ai.com/blog/">', f'<link rel="canonical" href="{SITE}/blog/category-{slug}.html">')
        cs = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{esc(name)}の記事一覧 | {BRAND}">', cs)
        cs = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc(desc)}">', cs)
        cs = cs.replace('<meta property="og:url" content="https://www.piste-ai.com/blog/">', f'<meta property="og:url" content="{SITE}/blog/category-{slug}.html">')
        cs = re.sub(r'<script type="application/ld\+json">.*?</script>', jsonld({"@context": "https://schema.org", "@graph": [org_node(), website_node(), {
            "@type": "CollectionPage", "@id": f"{SITE}/blog/category-{slug}.html", "url": f"{SITE}/blog/category-{slug}.html",
            "name": f"{name}の記事一覧", "description": desc, "isPartOf": {"@id": WEBSITE_ID}, "inLanguage": "ja"},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "ホーム", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "ブログ", "item": SITE + "/blog/"},
                {"@type": "ListItem", "position": 3, "name": name, "item": f"{SITE}/blog/category-{slug}.html"}]}]}).replace("\\", "\\\\"), cs, count=1, flags=re.S)
        cs = re.sub(r"(<div class=\"page-hero\">\s*<div class=\"container\">\s*<p class=\"section-title\">)Blog(</p>\s*<h1>)[^<]*(</h1>\s*<p>)[^<]*(</p>)",
                    lambda m: m.group(1) + "Category" + m.group(2) + esc(name) + m.group(3) + esc(desc) + m.group(4), cs, count=1, flags=re.S)
        cs = re.sub(r'<nav class="cat-nav".*?</nav>', cat_nav(slug, counts).replace("\\", "\\\\"), cs, count=1, flags=re.S)
        def keep(m):
            a = by_slug.get(m.group(1)[:-5])
            return m.group(0) if (a and a.category == slug) else ""
        cs = CARD_RE.sub(keep, cs)
        cs = re.sub(r"\n(\s*\n){2,}", "\n", cs)
        (BLOG / f"category-{slug}.html").write_text(cs, encoding="utf-8")
    return counts


# ---------------------------------------------------------------- トップページ等の画像差し替え
def swap_top_images():
    for name in ("index.html", "training.html", "about.html", "claude-code-support.html", "aichi.html"):
        p = ROOT / name
        if not p.exists():
            continue
        s = p.read_text(encoding="utf-8")
        # ブログカードは軽量版
        def card(m):
            attrs = m.group(1)
            sm = re.search(r'src="images/(blog-[^"]+?)(?:-card)?\.(?:jpg|webp)"', attrs)
            if not sm:
                return m.group(0)
            base = sm.group(1)
            c = IMG / f"{base}-card.webp"
            if not c.exists():
                return m.group(0)
            wh = img_size(c)
            attrs = attrs.replace(sm.group(0), f'src="images/{base}-card.webp"')
            attrs = re.sub(r'\s(width|height)="[^"]*"', "", attrs)
            if wh:
                attrs += f' width="{wh[0]}" height="{wh[1]}"'
            return f"<img{attrs}>"
        s = IMG_RE.sub(card, s)
        s = swap_images(s, "images/", first_eager=False)
        p.write_text(s, encoding="utf-8")


# ---------------------------------------------------------------- sitemap / feed / llms.txt
def file_lastmod(p: Path) -> str:
    return datetime.fromtimestamp(p.stat().st_mtime, JST).strftime("%Y-%m-%d")

def build_sitemap(arts: list[Article]):
    today = datetime.now(JST).strftime("%Y-%m-%d")
    latest = max(a.iso for a in arts) if arts else today
    urls = [(SITE + "/", latest, "daily", "1.0")]
    for name, pr in (("training.html", "0.8"), ("about.html", "0.7"), ("claude-code-support.html", "0.8"), ("aichi.html", "0.6")):
        if (ROOT / name).exists():
            urls.append((f"{SITE}/{name}", file_lastmod(ROOT / name), "monthly", pr))
    urls.append((f"{SITE}/blog/", latest, "daily", "0.9"))
    for slug, name, _ in CATEGORIES:
        cat_latest = max([a.iso for a in arts if a.category == slug] or [latest])
        urls.append((f"{SITE}/blog/category-{slug}.html", cat_latest, "weekly", "0.7"))
    for a in sorted(arts, key=lambda x: x.iso, reverse=True):
        urls.append((a.url, a.iso, "monthly", "0.7"))
    for name in ("privacy.html", "terms.html", "tokushoho.html"):
        if (ROOT / name).exists():
            urls.append((f"{SITE}/{name}", file_lastmod(ROOT / name), "yearly", "0.3"))
    body = "".join(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{d}</lastmod>\n    <changefreq>{c}</changefreq>\n    <priority>{p}</priority>\n  </url>\n" for u, d, c, p in urls)
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n", encoding="utf-8")
    return len(urls)

def build_feed(arts: list[Article], n=30):
    items = []
    for a in sorted(arts, key=lambda x: x.iso, reverse=True)[:n]:
        dt = datetime.strptime(a.iso, "%Y-%m-%d").replace(hour=9, tzinfo=JST)
        og, _ = a.og_image()
        items.append(
            f"  <item>\n    <title>{esc(a.title)}</title>\n    <link>{a.url}</link>\n    <guid isPermaLink=\"true\">{a.url}</guid>\n"
            f"    <pubDate>{dt.strftime('%a, %d %b %Y %H:%M:%S %z')}</pubDate>\n    <category>{esc(a.cat_name)}</category>\n"
            f"    <description>{esc(a.description)}</description>\n    <enclosure url=\"{og}\" type=\"image/jpeg\" length=\"0\"/>\n  </item>\n")
    now = datetime.now(JST).strftime("%a, %d %b %Y %H:%M:%S %z")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n<channel>\n'
           f"  <title>{BRAND} ブログ</title>\n  <link>{SITE}/blog/</link>\n  <atom:link href=\"{SITE}/feed.xml\" rel=\"self\" type=\"application/rss+xml\"/>\n"
           f"  <description>中小企業のための Claude Code・AI活用ガイド。ツール連携、経理・財務、営業・顧客対応、業務記録・現場改善、AI導入の基礎を毎日更新。</description>\n"
           f"  <language>ja</language>\n  <lastBuildDate>{now}</lastBuildDate>\n" + "".join(items) + "</channel>\n</rss>\n")
    (ROOT / "feed.xml").write_text(xml, encoding="utf-8")

def build_llms(arts: list[Article]):
    lines = [
        f"# {BRAND}（{COMPANY}）",
        "",
        f"> 中小企業のためのAI導入コンサルティング。Anthropic 公式パートナーネットワーク認定企業。代表・石川 卓が Claude Code を中心に、相談・実装・定着までマンツーマンで伴走します。所在地は愛知県碧南市、全国オンライン対応。",
        "",
        "## 会社・サービス",
        "",
        f"- [トップページ]({SITE}/): サービス概要、料金プラン、ご利用の流れ、最新AIニュース、お問い合わせ",
        f"- [Claude Code 導入サポート]({SITE}/claude-code-support.html): Claude Code のセットアップから業務への組み込みまでのマンツーマン支援（¥10,000税込/1時間）",
        f"- [AI研修プログラム]({SITE}/training.html): 従業員向け Claude Code 実践研修（全12コマ）。厚生労働省「人材開発支援助成金」の対象",
        f"- [愛知県・西三河の中小企業向けAI導入支援]({SITE}/aichi.html): 地域の事業者向けの案内",
        f"- [代表プロフィール]({SITE}/about.html): 石川 卓（岐阜大学大学院修了、大手鉄鋼メーカーで約8年勤務、400社以上のAI導入支援（2026年9月時点））",
        f"- [ブログ一覧]({SITE}/blog/): 毎日更新。{len(arts)}記事",
        f"- [RSS]({SITE}/feed.xml) / [サイトマップ]({SITE}/sitemap.xml)",
        "",
        "## 料金（税込）",
        "",
        "- Claude Code 導入サポート: ¥10,000 / 1時間",
        "- 動画レッスン「Claude Code 基礎＆セットアップ」: ¥5,000",
        "- ライトプラン: ¥20,000 / 月（週1時間×2回のマンツーマン指導）",
        "- スタンダードプラン: ¥40,000 / 月（週1時間×4回のマンツーマン相談・ハンズオン支援・業務テンプレート作成）",
        "",
        "## ブログ記事（カテゴリ別）",
        "",
    ]
    for slug, name, desc in CATEGORIES:
        lines.append(f"### {name}")
        lines.append("")
        lines.append(f"{desc}。一覧: {SITE}/blog/category-{slug}.html")
        lines.append("")
        for a in sorted([x for x in arts if x.category == slug], key=lambda x: x.iso, reverse=True):
            lines.append(f"- [{a.title}]({a.url}) ({a.iso}): {a.description}")
        lines.append("")
    lines += [
        "## 利用上の注意",
        "",
        "- 記事の内容は公開日時点の情報です。引用する際は記事URLと公開日を併記してください。",
        f"- 会社情報・法的表記: [特定商取引法に基づく表記]({SITE}/tokushoho.html) / [プライバシーポリシー]({SITE}/privacy.html) / [利用規約]({SITE}/terms.html)",
        "",
    ]
    (ROOT / "llms.txt").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------- main
def main():
    dates = load_dates()
    thumbs = load_thumbs()
    paths = sorted(p for p in BLOG.glob("*.html") if p.name != "index.html" and not p.name.startswith("category-"))
    arts = [Article(p, dates, thumbs) for p in paths]
    by_slug = {a.slug: a for a in arts}
    for a in arts:
        out = process_article(a, arts)
        a.path.write_text(out, encoding="utf-8")
    counts = build_blog_index(arts, by_slug)
    swap_top_images()
    n = build_sitemap(arts)
    build_feed(arts)
    build_llms(arts)
    from theme_build import apply_theme
    apply_theme()
    faq = sum(1 for a in arts if a.faq)
    print(f"articles: {len(arts)} / with FAQ schema: {faq} / sitemap urls: {n}")
    print("categories:", {CAT_BY_SLUG[k][1]: v for k, v in counts.items()})
    long_titles = [(a.slug, disp_w(a.short)) for a in arts if disp_w(a.short) > MAX_W + 1]
    if long_titles:
        print("titles wider than %s:" % (MAX_W + 1), long_titles)

if __name__ == "__main__":
    main()
