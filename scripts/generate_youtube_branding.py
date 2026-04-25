"""Generate YouTube channel icon + banner via Leonardo.ai API.

Usage:
    LEONARDO_API_KEY=xxx python3 scripts/generate_youtube_branding.py

Outputs to assets/youtube/.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API_KEY = os.environ.get("LEONARDO_API_KEY")
if not API_KEY:
    sys.exit("ERROR: set LEONARDO_API_KEY env var")

BASE_URL = "https://cloud.leonardo.ai/api/rest/v1"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

OUT_DIR = Path(__file__).parent.parent / "assets" / "youtube"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Leonardo Phoenix 1.0 — best for stylized branding
PHOENIX_MODEL_ID = "6b645e3a-d64f-4341-a6d8-7a3690fbf042"
# Flux Dev — better text rendering, good for typography
FLUX_DEV_MODEL_ID = "1dd50843-d653-4516-a8e3-f0238ee453ff"

ICON_PROMPT = (
    "Minimalist tech logo, bold 'AI' text in modern geometric sans-serif font, "
    "white letters on deep navy background hex 0F172A, subtle emerald green "
    "underline accent hex 10B981, flat vector design, professional, clean, "
    "centered composition, high contrast, optimized for circular crop, "
    "1:1 aspect ratio, no people, no faces, just bold typography on dark "
    "background, thick stroke, geometric, modern developer brand"
)

BANNER_PROMPT = (
    "Wide cinematic banner for AI engineer YouTube channel, dark navy "
    "background hex 0F172A with subtle dot grid pattern, large bold white "
    "headline text 'Building AI in Public', emerald green hex 10B981 "
    "accent underline beneath text, modern minimalist tech aesthetic, "
    "developer brand, professional, lots of negative space around text, "
    "horizontal 16:9 cinematic composition, abstract geometric circuit "
    "pattern in corners, neon glow effect, digital art style, no people, "
    "no faces, ultra wide, clean typography focus"
)


def http(method, path, body=None):
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        sys.exit(f"HTTP {e.code} on {method} {path}: {body}")


def download(url, out_path):
    """Download with browser-like headers (Leonardo's CDN rejects default UA)."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept": "image/png,image/*,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        out_path.write_bytes(r.read())


def generate(name, prompt, width, height, model_id=PHOENIX_MODEL_ID, alchemy=True):
    print(f"\n=== {name} ({width}x{height}) ===")
    res = http("POST", "/generations", {
        "prompt": prompt,
        "modelId": model_id,
        "width": width,
        "height": height,
        "num_images": 2,
        "alchemy": alchemy,
        "presetStyle": "DYNAMIC",
        "guidance_scale": 7,
    })
    gen_id = res["sdGenerationJob"]["generationId"]
    print(f"Generation ID: {gen_id}")

    # Poll for completion (5 sec interval, 6 min max)
    for attempt in range(72):
        time.sleep(5)
        status = http("GET", f"/generations/{gen_id}")
        gen = status["generations_by_pk"]
        if gen["status"] == "COMPLETE":
            images = gen["generated_images"]
            print(f"Got {len(images)} images")
            for i, img in enumerate(images):
                out_path = OUT_DIR / f"{name}-v{i + 1}.png"
                download(img["url"], out_path)
                print(f"  Saved: {out_path}")
            return
        elif gen["status"] == "FAILED":
            sys.exit(f"Generation failed: {gen}")
        if attempt % 6 == 0:
            print(f"  Still {gen['status']}... ({(attempt + 1) * 5}s)")
    sys.exit("Generation timed out after 6 min")


def main():
    # YouTube icon — square, will be cropped to circle
    # Leonardo Phoenix supports 1024x1024
    generate("channel-icon", ICON_PROMPT, 1024, 1024)

    # YouTube banner — 16:9 cinematic
    # Leonardo Phoenix supports 1472x832 (close to 16:9, will upscale to 2560x1440 later)
    generate("channel-banner", BANNER_PROMPT, 1472, 832)

    print(f"\n{'=' * 50}")
    print(f"Done. Check {OUT_DIR}")
    print("\nNext steps:")
    print("1. Pick the best variant (v1 or v2) for each")
    print("2. Banner needs upscale to 2560x1440 for YouTube")
    print("   - Use waifu2x.io (free), upscale.media, or imagemagick")
    print("3. Upload to YouTube Studio → Customization")


if __name__ == "__main__":
    main()
