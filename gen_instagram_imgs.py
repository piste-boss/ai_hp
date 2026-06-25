import json, base64, urllib.request, sys, time

with open('/Users/ishikawasuguru/.claude/credentials/.env') as f:
    key = None
    for line in f:
        if line.startswith('openai_apikey'):
            key = line.split('=', 1)[1].strip()
KEY = key
IMGDIR = '/Users/ishikawasuguru/AI_コンサル/HP作成/site/images'
SLUG = 'claude-code-instagram-integration'
BASE = "Photorealistic professional business-technology photo, no text, no letters, no logos. Color tone: dark charcoal gray (#1a1a1a) with elegant gold (#c4a24e) accents, cinematic soft lighting, modern and clean atmosphere. "

def gen(prompt, out, retry=1):
    body = json.dumps({"model": "gpt-image-2", "prompt": prompt, "size": "1536x1024", "n": 1}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/images/generations", data=body,
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    for attempt in range(retry + 1):
        try:
            with urllib.request.urlopen(req, timeout=240) as r:
                d = json.load(r)
            if d.get('data') and d['data'][0].get('b64_json'):
                with open(f"{IMGDIR}/{out}", 'wb') as fo:
                    fo.write(base64.b64decode(d['data'][0]['b64_json']))
                print("OK:", out)
                return True
            print("FAIL(no data):", str(d)[:200])
        except Exception as e:
            print(f"ERR attempt{attempt}:", str(e)[:200])
            time.sleep(3)
    return False

prompts = [
    (BASE + "A small business owner or shop staff using a laptop and smartphone to manage an Instagram-style social media feed for marketing, cozy modern store or office workspace, abstract grid of photo posts on screen.", f"blog-{SLUG}.jpg"),
    (BASE + "Close-up of hands creating social media content on a smartphone and laptop: planning posts, captions and engagement analytics dashboards with charts and graphs, conveying AI-assisted content creation and customer engagement.", f"blog-{SLUG}-01.jpg"),
    (BASE + "A clean step-by-step onboarding concept: a person setting up an automation workflow on a laptop, simple connected nodes and gears representing easy 4-step setup for non-engineers, organized minimalist desk.", f"blog-{SLUG}-02.jpg"),
]
results = {}
for p, o in prompts:
    results[o] = gen(p, o)
print("RESULTS:", results)
sys.exit(0 if all(results.values()) else 2)
