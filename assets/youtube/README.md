# YouTube Channel Assets

Generated via Leonardo.ai (Phoenix model). See `scripts/generate_youtube_branding.py`.

## Files

| File | Use | Size | Notes |
|------|-----|------|-------|
| `channel-icon-v1.png` | Channel profile picture | 1024×1024 | Bold "AI" white text + green ring on navy. Use as-is. |
| `banner-bg-v1.png` | Channel banner background | 1472×832 | Tech corner frames + center negative space. Add text in Canva. |
| `banner-bg-v2.png` | Channel banner background (alt) | 1472×832 | Diagonal circuit lines, more dramatic. Add text in Canva. |

## Upload to YouTube

### Profile icon
1. YouTube Studio → Customization → Branding → Picture
2. Upload `channel-icon-v1.png`
3. Position circle crop on center (default works)

### Banner
1. Upload `banner-bg-v1.png` (or v2) to Canva (canva.com)
2. Add text:
   - **Headline:** "Building AI in Public" — Space Grotesk Bold, 120pt, white `#FFFFFF`
   - **Subhead:** ".NET → AI Engineer · 150 days · 5 fintech projects" — Inter Regular, 36pt, gray `#94A3B8`
   - **Bottom:** "New videos: Wed + Sat" — Inter Bold, 28pt, green `#10B981`
3. Export PNG at 2560×1440
4. YouTube Studio → Customization → Branding → Banner image → Upload

### Brand colors (use everywhere)
- Background: `#0F172A` (deep navy)
- Text: `#FFFFFF` (white)
- Accent: `#10B981` (emerald green)
- Muted text: `#94A3B8` (slate gray)

## Regenerate

If you want different versions:

```bash
LEONARDO_API_KEY=xxx python3 scripts/generate_youtube_branding.py
```

Edit `ICON_PROMPT` / `BANNER_PROMPT` in the script to iterate.

## Credits used (so far)

~80-100 Leonardo credits across 6 generated images (4 kept, 2 rejected sets discarded).
