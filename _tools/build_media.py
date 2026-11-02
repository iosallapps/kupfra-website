"""Regenerate every image under img/ and the favicons from the app's own assets.

    python3 _tools/build_media.py [TURNTABLE_DIR]

Sources are read-only: the app icon and design art from the Treppenwerk project and the
QA screenshots (iPhone 17 Pro Max, English). Output is WebP only, sized for the page.
TURNTABLE_DIR, when given, holds the 48-frame orbit renders (<type>-<preset>-NN.png) made by a
temporary SceneKit test; they become img/turn/<type>-<size>-NN.webp over the site background.
"""
import glob
import os
import sys
from PIL import Image, ImageDraw, ImageFont

APP = os.path.expanduser("~/Developer/Treppenwerk")
ART = APP + "/Treppenwerk/Assets.xcassets/Design"
SHOTS = APP + "/.launch-work/qa-truth/fixed/INT/ProMax"
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = SITE + "/img"
Q = 80
BG = (14, 12, 11)  # --carbon in styles.css


def save(im, name, q=Q):
    path = f"{OUT}/{name}.webp"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, "WEBP", quality=q, method=6)


def sized(im, widths, base, q=Q):
    for w in widths:
        h = round(im.height * w / im.width)
        save(im.resize((w, h), Image.LANCZOS), f"{base}-{w}", q)


def art(name):
    return Image.open(f"{ART}/{name}.imageset/{name}.png").convert("RGBA")


def trimmed(im, pad=8):
    box = im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
    l, t, r, b = box
    return im.crop((max(l - pad, 0), max(t - pad, 0), min(r + pad, im.width), min(b + pad, im.height)))


icon = Image.open(APP + "/Treppenwerk/Assets.xcassets/AppIcon.appiconset/AppIcon.png").convert("RGB")
for w in (64, 128, 256):
    save(icon.resize((w, w), Image.LANCZOS), f"app-icon-{w}", 90)
icon.resize((180, 180), Image.LANCZOS).save(SITE + "/apple-touch-icon.png", optimize=True)
icon.resize((32, 32), Image.LANCZOS).save(SITE + "/favicon-32.png", optimize=True)
icon.resize((16, 16), Image.LANCZOS).save(SITE + "/favicon-16.png", optimize=True)
icon.resize((48, 48), Image.LANCZOS).save(SITE + "/favicon.ico", sizes=[(48, 48)])

# Phone screens.
for src, base in [("home", "shot-home"), ("stairsStraight_top", "shot-stair3d"), ("hubElectrical", "shot-electrical"),
                  ("concrete_en_US_top", "shot-concrete"), ("stairsStraight_checks", "shot-checks"),
                  ("cableSize_en_GB_top", "shot-cable"), ("reportPages", "shot-pdf"), ("cutList_default", "shot-cutlist")]:
    sized(Image.open(f"{SHOTS}/{src}.png").convert("RGB"), (360, 600), base)

# Cutouts with alpha: hero floats, module art, the sixteen calculators.
for name, base, widths in [("ModuleElectrical", "float-cable", (480,)), ("ToolBreaker", "float-breaker", (400,)),
                           ("ModuleConstruction", "float-blocks", (480,)), ("ModuleStairs", "float-stair", (480,)),
                           ("HubElectrical", "art-electrical", (900,)), ("HomeHeroStairs", "art-stairs", (900,))]:
    sized(trimmed(art(name)), widths, base)

for name in ["CableSize", "VoltageDrop", "Breaker", "ShortCircuit", "Earthing", "ConduitFill", "LineSizing", "OhmsLaw",
             "Concrete", "Tiles", "Paint", "Drywall", "Masonry", "Insulation", "Flooring", "Roof"]:
    im = art(f"Tool{name}").resize((320, 320), Image.LANCZOS)
    save(im, f"tool/{name.lower()}", 78)

# Turntable frames, flattened onto the page background so they need no alpha.
if len(sys.argv) > 1:
    for path in sorted(glob.glob(os.path.join(sys.argv[1], "*-??.png"))):
        stem = os.path.basename(path)[:-4]
        kind, _, frame = stem.split("-")
        im = Image.open(path).convert("RGBA")
        flat = Image.new("RGBA", im.size, BG + (255,))
        flat.alpha_composite(im)
        flat = flat.convert("RGB")
        for w, q in ((420, 70), (760, 72)):
            save(flat.resize((w, w), Image.LANCZOS), f"turn/{kind}-{w}-{frame}", q)

# Open Graph card 1200x630: carbon, copper glow, icon, name, line, stair art.
W, H = 1200, 630
bg = Image.new("RGB", (W, H), (12, 11, 10))
hero = Image.open(f"{ART}/HomeHeroStairs.imageset/HomeHeroStairs.png").convert("RGB")
hero = hero.resize((760, round(hero.height * 760 / hero.width)), Image.LANCZOS)
mask = Image.linear_gradient("L").rotate(90).resize(hero.size)
bg.paste(hero, (W - hero.width, (H - hero.height) // 2 + 20), mask)
d = ImageDraw.Draw(bg)


def font(size, bold=False):
    for p in ("/System/Library/Fonts/HelveticaNeue.ttc", "/System/Library/Fonts/Helvetica.ttc"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size, index=1 if bold else 0)
    return ImageFont.load_default()


bg.paste(icon.resize((120, 120), Image.LANCZOS), (72, 72))
d.text((212, 98), "Kupfra", font=font(64, True), fill=(245, 240, 234))
d.text((72, 290), "Stairs, cables", font=font(68, True), fill=(245, 240, 234))
d.text((72, 372), "and concrete.", font=font(68, True), fill=(240, 150, 80))
d.text((72, 478), "Construction and electrical calculators", font=font(30), fill=(176, 168, 160))
d.text((72, 522), "with a 3D stair designer.", font=font(30), fill=(176, 168, 160))
bg.save(SITE + "/og-image.png", optimize=True)
