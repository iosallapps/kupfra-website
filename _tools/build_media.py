"""Regenerate every image under img/ and the favicons from the app's own assets.

    python3 _tools/build_media.py

Sources are read-only: the app icon and design art from the Treppenwerk project and the
QA screenshots (iPhone 17 Pro Max, English). Output is WebP only, sized for the page.
"""
import os
from PIL import Image, ImageDraw, ImageFont

APP = os.path.expanduser("~/Developer/Treppenwerk")
ART = APP + "/Treppenwerk/Assets.xcassets/Design"
SHOTS = APP + "/.launch-work/qa-truth/fixed/INT/ProMax"
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = SITE + "/img"
Q = 80


def save(im, name, q=Q):
    im.save(f"{OUT}/{name}.webp", "WEBP", quality=q, method=6)


def sized(im, widths, base):
    for w in widths:
        h = round(im.height * w / im.width)
        save(im.resize((w, h), Image.LANCZOS), f"{base}-{w}")


icon = Image.open(APP + "/Treppenwerk/Assets.xcassets/AppIcon.appiconset/AppIcon.png").convert("RGB")
for w in (64, 128, 256):
    save(icon.resize((w, w), Image.LANCZOS), f"app-icon-{w}", 90)
icon.resize((180, 180), Image.LANCZOS).save(SITE + "/apple-touch-icon.png", optimize=True)
icon.resize((32, 32), Image.LANCZOS).save(SITE + "/favicon-32.png", optimize=True)
icon.resize((16, 16), Image.LANCZOS).save(SITE + "/favicon-16.png", optimize=True)
icon.resize((48, 48), Image.LANCZOS).save(SITE + "/favicon.ico", sizes=[(48, 48)])

for src, base in [("home", "shot-home"), ("stairsStraight_design", "shot-stairs"),
                  ("cableSize_en_GB_top", "shot-cable"), ("concrete_en_US_top", "shot-concrete"),
                  ("stairsStraight_checks", "shot-checks"), ("reportPages", "shot-pdf"),
                  ("cutList_default", "shot-cutlist")]:
    sized(Image.open(f"{SHOTS}/{src}.png").convert("RGB"), (360, 600), base)

for src, base, widths in [("HomeHeroStairs.imageset/HomeHeroStairs.png", "art-stairs", (640, 1200)),
                          ("ModuleConstruction.imageset/ModuleConstruction.png", "art-construction", (480, 900)),
                          ("HubElectrical.imageset/HubElectrical.png", "art-electrical", (480, 900)),
                          ("OnboardingOverview.imageset/OnboardingOverview.png", "art-overview", (480, 900))]:
    sized(Image.open(f"{ART}/{src}").convert("RGB"), widths, base)

# Open Graph card 1200x630: carbon, copper glow, icon, name, line, stair art.
W, H = 1200, 630
bg = Image.new("RGB", (W, H), (12, 11, 10))
art = Image.open(f"{ART}/HomeHeroStairs.imageset/HomeHeroStairs.png").convert("RGB")
art = art.resize((760, round(art.height * 760 / art.width)), Image.LANCZOS)
mask = Image.linear_gradient("L").rotate(90).resize(art.size)  # fades to the left
bg.paste(art, (W - art.width, (H - art.height) // 2 + 20), mask.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_LEFT_RIGHT))
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
