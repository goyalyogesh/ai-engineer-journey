# Leonardo.ai Prompts — YouTube Branding

Reusable prompts for generating channel icon + banner. Use directly in Leonardo.ai web UI.

## Brand colors (referenced in prompts)

| Color | Hex | Use |
|-------|-----|-----|
| Background | `#0F172A` | Deep navy |
| Accent | `#10B981` | Emerald green |
| Text | `#FFFFFF` | White |
| Muted | `#94A3B8` | Slate gray |

---

# 🟢 ICON (no text, abstract symbol)

**Use:** YouTube channel profile picture (will be cropped to circle)

## Settings

| Setting | Value |
|---------|-------|
| Model | Leonardo Phoenix 1.0 |
| Size | 1024 × 1024 |
| Alchemy | ON |
| Preset style | Dynamic |
| Guidance scale | 7 |
| Number of images | 4 (pick best) |

## Prompt — Option A (geometric/minimalist) ⭐ RECOMMENDED

```
Minimalist abstract logo symbol, single bold geometric icon centered on deep navy background hex 0F172A, glowing emerald green hex 10B981 hexagonal node connected with thin lines to surrounding white dots, neural network aesthetic, ultra clean vector style, flat design, perfect symmetry, centered composition with strong negative space, high contrast, professional tech brand mark, premium quality, sharp edges
```

## Prompt — Option B (brain/AI-themed)

```
Abstract minimalist brain logo, glowing emerald green hex 10B981 stylized brain made of geometric circuit pattern lines, white accent dots, deep navy background hex 0F172A, centered composition, vector flat design, modern AI tech brand symbol, ultra clean, premium professional, sharp lines, perfectly centered, plenty of dark negative space around the symbol
```

## Prompt — Option C (cube/3D geometric)

```
Single floating 3D isometric cube logo, glowing emerald green hex 10B981 wireframe cube with white inner core, deep navy background hex 0F172A, modern minimalist tech aesthetic, centered composition, sharp clean edges, soft glow effect, premium AI brand symbol, vector style, perfectly symmetrical, lots of dark negative space, no extras
```

## Negative prompt (CRITICAL — paste into negative prompt field)

```
text, letters, words, numbers, typography, watermark, logo text, signature, brand name, captions, labels, characters, alphabet, written, calligraphy, font
```

---

# 🟢 BANNER ("AI Engineer" text)

**Use:** YouTube channel banner art

## ⚠️ Reality check

AI image generation often mangles text ("ENGIINEER", "ENGEER", etc.). Two paths:

- **Path 1 (RECOMMENDED):** Generate text-free background → add "AI Engineer" text in Canva. Guaranteed clean.
- **Path 2:** Bake text into prompt → ~30-40% success rate → regenerate until clean.

## Settings

| Setting | Value |
|---------|-------|
| Model | Flux Dev (better text) OR Phoenix 1.0 |
| Size | 1472 × 832 (Phoenix) OR 1568 × 864 (Flux) |
| Alchemy | ON |
| Preset style | Dynamic |
| Guidance scale | 7 |
| Number of images | 4 (regenerate if text mangled) |

---

## Prompt — Path 1: Text-free background ⭐ RECOMMENDED

```
Wide cinematic YouTube banner background, deep navy hex 0F172A with subtle dark dot grid pattern, abstract geometric circuit board patterns flowing from all four corners toward center, glowing emerald green hex 10B981 neon accent lines and bright dots in corners, large empty negative space in center for text overlay, modern AI tech developer brand aesthetic, professional, ultra wide horizontal 16:9 cinematic composition, no people, no faces, vector flat design, clean minimalist, premium quality, soft glow effects
```

**Negative prompt:**
```
text, letters, words, numbers, typography, watermark, signature, captions, labels, written, calligraphy, font, characters, person, face, hands
```

**Then in Canva:** add text "AI Engineer" centered, white `#FFFFFF`, Space Grotesk Bold 200pt + green `#10B981` underline.

---

## Prompt — Path 2: Text baked in (risky)

```
Wide cinematic YouTube banner, large bold white text "AI Engineer" centered in middle, dark navy background hex 0F172A, emerald green hex 10B981 underline accent below text, modern minimalist tech aesthetic, abstract circuit pattern in corners, professional developer brand, ultra wide horizontal 16:9 composition, clean typography, sharp readable text, premium quality, no other text, no extra words
```

**Negative prompt for Path 2:**
```
misspelled text, garbled text, gibberish, double letters, distorted typography, blurry text, multiple text instances, extra words, watermark, signature, person, face, hands, multiple lines of text
```

**Tip:** if text comes out "AI Engineerr" or "AI Engineee" → regenerate (same prompt, new seed). Often clean by attempt 2-3.

---

# 🚀 Workflow on leonardo.ai

1. Go to https://leonardo.ai → **Image Generation**
2. Top selector: **Phoenix 1.0** (icon) or **Flux Dev** (banner with text)
3. Right sidebar:
   - Set **Image Dimensions** (1024×1024 for icon, 1472×832 for banner)
   - Toggle **Alchemy ON**
   - Set **Preset Style: Dynamic**
   - Set **Guidance Scale: 7**
4. Main prompt box: paste **Prompt**
5. Click **Add a negative prompt** (toggle below prompt) → paste **Negative prompt**
6. Set **Number of Images: 4**
7. Click **Generate**
8. Pick favorite from 4 generations → click → **Download** as PNG

## Credit cost estimate

| Generation | Credits |
|------------|---------|
| Icon, 4 images, Alchemy ON | ~30 credits |
| Banner, 4 images, Alchemy ON | ~40 credits |
| Banner regen 1-2x (if text baked in) | +40-80 credits |
| **Total** | **~70-150 credits** |

Free tier: 150 credits/day. Should be fine.

---

# 📐 After generating

## Icon
- Download PNG (1024×1024)
- YouTube Studio → Customization → Branding → Picture → Upload
- Adjust circle crop preview if needed

## Banner
- Download PNG (1472×832)
- If used Path 1 (text-free): upload to Canva, add "AI Engineer" text per `README.md` specs
- If used Path 2 (text baked in): may need to upscale to 2560×1440 (use waifu2x.io free, or upscale.media)
- YouTube Studio → Customization → Branding → Banner image → Upload

## Final asset specs

| Asset | Final size | Where uploaded |
|-------|------------|----------------|
| Channel icon | 1024×1024 (YouTube auto-resizes to 800×800 circle) | YouTube profile picture |
| Channel banner | 2560×1440 minimum | YouTube banner |

---

# 🎨 Iterating on prompts

If first generation isn't right:

- **Too busy:** add "minimalist, clean, simple, lots of negative space"
- **Too dark:** lower guidance scale to 5-6
- **Too saturated:** add "muted, soft, subtle"
- **Wrong colors:** be more explicit ("hex 0F172A navy not blue", "hex 10B981 emerald not lime")
- **Wrong aspect:** Phoenix is limited — try Flux for more flexible dimensions
- **Wrong style:** add "vector flat design" OR "3D rendered" OR "photorealistic" depending on want

## Seed control

To reproduce a generation you liked, save the seed (Leonardo shows it under each image). Reuse seed + same prompt = same result.

---

# Anti-patterns

- ❌ Don't ask for too many elements — pick ONE icon style, not "brain AND cube AND circuit"
- ❌ Don't use text in icon (will mangle)
- ❌ Don't mix multiple aesthetics ("photorealistic vector flat design 3D")
- ❌ Don't skip the negative prompt for icon (text leaks easily)
- ❌ Don't use long sentences — keep prompts as comma-separated keywords
