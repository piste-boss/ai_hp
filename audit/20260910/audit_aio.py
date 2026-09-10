import re, json, glob, os, sys, datetime, csv
from html import unescape

SITE = "/Users/ishikawasuguru/AI_コンサル/HP作成/site"
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
TODAY = datetime.date(2026, 9, 10)

def strip_tags(s):
    s = re.sub(r"<script.*?</script>", "", s, flags=re.S)
    s = re.sub(r"<style.*?</style>", "", s, flags=re.S)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    return unescape(re.sub(r"\s+", "", s))

rows = []
files = sorted(f for f in glob.glob(f"{SITE}/blog/*.html") if not os.path.basename(f).startswith(("index", "category-")))
for f in files:
    slug = os.path.basename(f)[:-5]
    html = open(f, encoding="utf-8").read()
    r = {"slug": slug}
    title = re.search(r"<title>(.*?)</title>", html, re.S)
    t = unescape(title.group(1).strip()) if title else ""
    r["title_len"] = len(t)
    r["title_core_len"] = len(re.sub(r"\s*\|\s*Piste AI EVANGELISTS\s*$", "", t))
    r["title_suffix"] = "Piste AI EVANGELISTS" in t
    r["h1_count"] = len(re.findall(r"<h1[\s>]", html))
    h2s = [strip_tags(x) for x in re.findall(r"<h2[^>]*>(.*?)</h2>", html, re.S)]
    r["h2_count"] = len(h2s)
    r["h2_question"] = sum(1 for h in h2s if h.endswith(("？", "?")))
    r["h2_numbered"] = sum(1 for h in h2s if re.match(r"^\d+[\.．]", h))
    # main body chars
    main = re.search(r"<main[^>]*>(.*?)</main>", html, re.S)
    body = main.group(1) if main else html
    # remove related/cta/nav
    body_core = re.sub(r"<section class=\"seo-related\".*?</section>", "", body, flags=re.S)
    body_core = re.sub(r"<div class=\"cta\">.*?</div>", "", body_core, flags=re.S)
    r["body_chars"] = len(strip_tags(body_core))
    # keypoints
    kp = re.search(r"<div class=\"seo-keypoints\">(.*?)</div>", html, re.S)
    kp_items = [strip_tags(x) for x in re.findall(r"<li>(.*?)</li>", kp.group(1), re.S)] if kp else []
    r["keypoints"] = len(kp_items)
    r["keypoints_is_toc"] = bool(kp_items) and all(k in h2s or re.sub(r"^\d+[\.．]\s*", "", k) in [re.sub(r"^\d+[\.．]\s*", "", h) for h in h2s] for k in kp_items)
    r["keypoints_has_target"] = any(("対象" in k or "向け" in k) for k in kp_items)
    # postmeta
    r["visible_pubdate"] = "公開日" in html
    r["visible_moddate"] = "更新日" in html
    r["visible_author"] = 'rel="author"' in html
    # ld+json
    lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    types = []
    faq_q_ld = 0
    dp = dm = None
    author_id = False
    tel_ld = False
    wordcount = None
    for ld in lds:
        try:
            data = json.loads(ld)
        except Exception:
            r.setdefault("ld_json_error", 0)
            r["ld_json_error"] = r.get("ld_json_error", 0) + 1
            continue
        nodes = data.get("@graph", [data]) if isinstance(data, dict) else data
        for n in nodes:
            tt = n.get("@type")
            types.append(tt if isinstance(tt, str) else "+".join(tt))
            if tt == "FAQPage":
                faq_q_ld = len(n.get("mainEntity", []))
            if tt in ("BlogPosting", "Article"):
                dp, dm = n.get("datePublished"), n.get("dateModified")
                author_id = isinstance(n.get("author"), dict) and "@id" in n["author"]
                wordcount = n.get("wordCount")
            if "telephone" in n:
                tel_ld = True
    r["ld_types"] = " ".join(types)
    r["ld_blocks"] = len(lds)
    r["has_faqpage"] = faq_q_ld > 0
    r["faq_q_ld"] = faq_q_ld
    r["faq_q_body"] = len(re.findall(r"<h3[^>]*>\s*Q[\.．]", html))
    r["faq_h2"] = any("よくある質問" in h or "FAQ" in h for h in h2s)
    r["author_by_id"] = author_id
    r["tel_in_ld"] = tel_ld
    r["wordcount_ld"] = wordcount
    r["datePublished"] = dp[:10] if dp else ""
    r["dateModified"] = dm[:10] if dm else ""
    r["mod_eq_pub"] = bool(dp) and dp == dm
    if dp:
        d = datetime.date.fromisoformat(dp[:10])
        r["age_days"] = (TODAY - d).days
    else:
        r["age_days"] = None
    # links
    related = re.search(r"<section class=\"seo-related\".*?</section>", html, re.S)
    r["related_cards"] = len(re.findall(r"seo-related-card", related.group(0))) if related else 0
    body_links = re.findall(r'href="([^"]+)"', body_core)
    r["inbody_blog_links"] = sum(1 for l in body_links if re.match(r"^(\.\./blog/|)[a-z0-9\-]+\.html$", l) and not l.startswith(("index", "category-")))
    ext = set()
    for l in re.findall(r'href="(https?://[^"]+)"', body):
        dom = re.sub(r"^https?://(www\.)?", "", l).split("/")[0]
        if dom in ("piste-ai.com", "x.com", "instagram.com", "threads.com", "threads.net", "coconala.com", "lin.ee", "line.me"):
            continue
        ext.add(dom)
    r["ext_domains"] = len(ext)
    r["ext_list"] = " ".join(sorted(ext))
    # CTA
    ctas = re.findall(r'<a href="([^"]+)"[^>]*>([^<]*(?:ココナラ|相談|問い合わせ)[^<]*)</a>', body)
    r["cta_coconala_text_to_contact"] = sum(1 for h, tx in ctas if "ココナラ" in tx and "coconala" not in h)
    r["cta_links"] = " | ".join(f"{tx}→{h}" for h, tx in ctas)[:200]
    # images
    imgs = re.findall(r"<img[^>]*>", body)
    r["img_count"] = len(imgs)
    r["img_no_wh"] = sum(1 for i in imgs if "width=" not in i or "height=" not in i)
    r["img_no_alt"] = sum(1 for i in imgs if 'alt="' not in i)
    r["img_non_webp"] = sum(1 for i in imgs if ".webp" not in i)
    r["img_no_lazy"] = sum(1 for i in imgs[1:] if 'loading="lazy"' not in i)
    # tracking / canonical
    r["ga4_config"] = len(re.findall(r"gtag\('config',\s*'G-LR35246V7B'", html))
    r["clarity"] = len(re.findall(r"clarity\.ms/tag", html))
    can = re.search(r'rel="canonical" href="([^"]+)"', html)
    r["canonical"] = can.group(1) if can else ""
    r["canonical_ok"] = r["canonical"] == f"https://www.piste-ai.com/blog/{slug}.html"
    # numbers / consistency
    text = strip_tags(html)
    for k in ["200社", "110社", "70社", "3,000円", "¥10,000", "10,000円", "1万円"]:
        r["n_" + k] = text.count(k)
    # first-answer position: chars before first h2 that is not 目次
    r["intro_chars"] = len(strip_tags(body_core.split("<h2")[0])) if "<h2" in body_core else r["body_chars"]
    # primary data heuristics
    r["has_evidence_words"] = sum(text.count(w) for w in ["検証", "実測", "実際に", "時間短縮", "削減した", "分かかっていた", "分に短縮", "件を処理"])
    rows.append(r)

keys = list(rows[0].keys())
with open(os.path.join(OUT, "audit_articles.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=keys)
    w.writeheader(); w.writerows(rows)

N = len(rows)
def cnt(pred): return sum(1 for r in rows if pred(r))
def lst(pred, n=8): return [r["slug"] for r in rows if pred(r)][:n]
summary = {
  "articles": N,
  "title_core_over_35": cnt(lambda r: r["title_core_len"] > 35),
  "title_full_over_60": cnt(lambda r: r["title_len"] > 60),
  "title_suffix": cnt(lambda r: r["title_suffix"]),
  "h1_not_1": cnt(lambda r: r["h1_count"] != 1),
  "h2_question_zero": cnt(lambda r: r["h2_question"] == 0),
  "h2_numbered_any": cnt(lambda r: r["h2_numbered"] > 0),
  "h2_count_dist": {"<7": cnt(lambda r: r["h2_count"] < 7), "7-15": cnt(lambda r: 7 <= r["h2_count"] <= 15), ">15": cnt(lambda r: r["h2_count"] > 15)},
  "keypoints_present": cnt(lambda r: r["keypoints"] > 0),
  "keypoints_is_toc_copy": cnt(lambda r: r["keypoints_is_toc"]),
  "keypoints_has_target": cnt(lambda r: r["keypoints_has_target"]),
  "visible_pubdate": cnt(lambda r: r["visible_pubdate"]),
  "visible_moddate": cnt(lambda r: r["visible_moddate"]),
  "visible_author": cnt(lambda r: r["visible_author"]),
  "faqpage_missing": cnt(lambda r: not r["has_faqpage"]),
  "faq_h2_but_no_schema": cnt(lambda r: r["faq_h2"] and not r["has_faqpage"]),
  "faq_h2_missing": cnt(lambda r: not r["faq_h2"]),
  "faq_q_mismatch": cnt(lambda r: r["has_faqpage"] and r["faq_q_ld"] != r["faq_q_body"]),
  "author_by_id": cnt(lambda r: r["author_by_id"]),
  "tel_in_ld": cnt(lambda r: r["tel_in_ld"]),
  "mod_eq_pub": cnt(lambda r: r["mod_eq_pub"]),
  "age_over_90": cnt(lambda r: r["age_days"] is not None and r["age_days"] > 90),
  "age_over_180": cnt(lambda r: r["age_days"] is not None and r["age_days"] > 180),
  "age_under_30": cnt(lambda r: r["age_days"] is not None and r["age_days"] < 30),
  "related_lt_2": cnt(lambda r: r["related_cards"] < 2),
  "inbody_blog_links_zero": cnt(lambda r: r["inbody_blog_links"] == 0),
  "ext_domains_zero": cnt(lambda r: r["ext_domains"] == 0),
  "cta_coconala_to_contact": cnt(lambda r: r["cta_coconala_text_to_contact"] > 0),
  "img_no_wh_any": cnt(lambda r: r["img_no_wh"] > 0),
  "img_non_webp_any": cnt(lambda r: r["img_non_webp"] > 0),
  "img_no_lazy_any": cnt(lambda r: r["img_no_lazy"] > 0),
  "ga4_not_1": cnt(lambda r: r["ga4_config"] != 1),
  "clarity_not_1": cnt(lambda r: r["clarity"] != 1),
  "canonical_bad": cnt(lambda r: not r["canonical_ok"]),
  "ld_json_error": cnt(lambda r: r.get("ld_json_error", 0) > 0),
  "body_chars_dist": {"<1500": cnt(lambda r: r["body_chars"] < 1500), "1500-5000": cnt(lambda r: 1500 <= r["body_chars"] <= 5000), "5000-8000": cnt(lambda r: 5000 < r["body_chars"] <= 8000), ">8000": cnt(lambda r: r["body_chars"] > 8000)},
  "intro_chars_over_600": cnt(lambda r: r["intro_chars"] > 600),
  "n_200社_any": cnt(lambda r: r["n_200社"] > 0),
  "n_70社_any": cnt(lambda r: r["n_70社"] > 0),
  "n_110社_any": cnt(lambda r: r["n_110社"] > 0),
  "n_3000yen_any": cnt(lambda r: r["n_3,000円"] > 0),
  "n_10000_any": cnt(lambda r: r["n_¥10,000"] + r["n_10,000円"] + r["n_1万円"] > 0),
  "both_70_and_200": cnt(lambda r: r["n_70社"] > 0 and r["n_200社"] > 0),
  "evidence_zero": cnt(lambda r: r["has_evidence_words"] == 0),
  "examples": {
    "faqpage_missing": lst(lambda r: not r["has_faqpage"]),
    "faq_h2_missing": lst(lambda r: not r["faq_h2"]),
    "title_core_over_35": lst(lambda r: r["title_core_len"] > 35, 5),
    "ext_domains_zero": lst(lambda r: r["ext_domains"] == 0, 5),
    "body_over_8000": lst(lambda r: r["body_chars"] > 8000, 8),
    "cta_coconala_to_contact": lst(lambda r: r["cta_coconala_text_to_contact"] > 0, 8),
    "n_3000yen": lst(lambda r: r["n_3,000円"] > 0, 8),
    "n_110社": lst(lambda r: r["n_110社"] > 0, 8),
    "ga4_not_1": lst(lambda r: r["ga4_config"] != 1, 8),
    "img_non_webp": lst(lambda r: r["img_non_webp"] > 0, 8),
  },
  "medians": {
    "body_chars": sorted(r["body_chars"] for r in rows)[N//2],
    "title_len": sorted(r["title_len"] for r in rows)[N//2],
    "h2_count": sorted(r["h2_count"] for r in rows)[N//2],
    "intro_chars": sorted(r["intro_chars"] for r in rows)[N//2],
    "age_days": sorted(r["age_days"] for r in rows if r["age_days"] is not None)[N//2],
  },
}
json.dump(summary, open(os.path.join(OUT, "audit_summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False, indent=1))
