#!/usr/bin/env python3
"""画像最適化: site/images 配下の参照画像から WebP と OGP 用 JPG を生成する（冪等）。

- blog-*.jpg            → blog-*.webp（幅1200）
- blog-{slug}.jpg（サムネ）→ blog-{slug}-card.webp（幅640）, blog-{slug}-og.jpg（幅1200・JPEG q80）
- icon-*.png            → icon-*.webp（幅160）
- logo.png              → logo.webp（幅240）
- service-*.jpg / hero-bg.jpg / ogp.jpg → 同名 .webp（幅640まで）
- profile.jpg           → profile.webp（幅800）

既に出力が存在し、元画像より新しければスキップする。
"""
from pathlib import Path
from PIL import Image, ImageOps
import re, sys, time

ROOT = Path(__file__).resolve().parent.parent / "site"
IMG = ROOT / "images"

FORCE = "--force" in sys.argv

def newer(out: Path, src: Path) -> bool:
    return (not FORCE) and out.exists() and out.stat().st_mtime >= src.stat().st_mtime

def load(src: Path) -> Image.Image:
    im = Image.open(src)
    im = ImageOps.exif_transpose(im)
    return im

def save_webp(src: Path, out: Path, width: int, quality: int = 78):
    if newer(out, src):
        return False
    im = load(src)
    if im.width > width:
        h = round(im.height * width / im.width)
        im = im.resize((width, h), Image.LANCZOS)
    if im.mode in ("P", "LA"):
        im = im.convert("RGBA")
    im.save(out, "WEBP", quality=quality, method=6)
    return True

def save_jpg(src: Path, out: Path, width: int, quality: int = 80):
    if newer(out, src):
        return False
    im = load(src).convert("RGB")
    if im.width > width:
        h = round(im.height * width / im.width)
        im = im.resize((width, h), Image.LANCZOS)
    im.save(out, "JPEG", quality=quality, optimize=True, progressive=True)
    return True

def main():
    t0 = time.time()
    done = 0
    for src in sorted(IMG.iterdir()):
        n = src.name
        if src.suffix.lower() not in (".jpg", ".jpeg", ".png"):
            continue
        stem = src.stem
        try:
            if n.startswith("blog-"):
                if n.endswith("-og.jpg"):
                    continue
                done += save_webp(src, IMG / f"{stem}.webp", 1200)
                if not re.search(r"-\d\d$", stem) or stem.startswith("blog-thumb-"):  # サムネイル
                    done += save_webp(src, IMG / f"{stem}-card.webp", 640, 75)
                    done += save_jpg(src, IMG / f"{stem}-og.jpg", 1200)
            elif n.startswith("icon-"):
                done += save_webp(src, IMG / f"{stem}.webp", 160, 85)
            elif n == "logo.png":
                done += save_webp(src, IMG / "logo.webp", 240, 90)
            elif n == "profile.jpg":
                done += save_webp(src, IMG / "profile.webp", 800)
            elif n.startswith("service-") or n in ("hero-bg.jpg", "ogp.jpg"):
                done += save_webp(src, IMG / f"{stem}.webp", 640)
        except Exception as e:
            print("ERROR", n, e, file=sys.stderr)
    print(f"generated {done} files in {time.time()-t0:.1f}s")

if __name__ == "__main__":
    main()
