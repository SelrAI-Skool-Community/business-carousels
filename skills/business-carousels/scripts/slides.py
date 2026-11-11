#!/usr/bin/env python3
"""The fixed steps of a business carousel, done the same way every time.

  slides.py sizes                                  platform sizes and slide limits
  slides.py render <plan.json> --out <folder>      type-led or photo-led slides, text fitted
  slides.py check <folder> --platform <name>       every image the right size, count and order
  slides.py finalise <image>... --project <folder> --name <slug> --platform <name>
                                                   approved files into final/, in posting order
  slides.py selftest                               render one test slide in a temporary folder

Python 3.9 or newer, standard library only, on Mac, Windows (py) and Linux. `render`
uses a Chrome, Edge, Chromium or Brave already on the computer, headless; it
installs nothing. Add --dry-run to render or finalise to see what would happen.

A plan for `render` (paths are relative to the plan file; only "headline" is required):

  {
    "platform": "instagram-portrait",
    "name": "drain tips",
    "brand": {"background": "#0B1F33", "accent": "#F5C518", "text": "#FFFFFF",
              "font_file": "fonts/Brand-Bold.ttf", "body_font_file": "fonts/Brand-Regular.ttf",
              "handle": "@harbourplumbing"},
    "slides": [
      {"headline": "Your drain keeps blocking", "support": "Here's why.", "image": "scene.jpg", "place": "bottom"},
      {"label": "Cause 1", "headline": "Tree roots in old clay pipes", "place": "center"},
      {"headline": "Want the checklist?", "support": "Comment DRAINS", "keyword": "DRAINS"}
    ]
  }

"place" is top, center or bottom. Without a font file, "font" names an installed font.
Text is sized as large as fits and never below about 20 points (headline) or 12
points (other text) on a phone; a slide that cannot fit saves nothing and says so.
Files come out as 01-<name>.png, 02-<name>.png ... at the platform's exact size.
"""
import argparse
import base64
import html
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
from pathlib import Path

PLATFORMS = {
    "instagram-portrait": (1080, 1350, 20, "Instagram feed carousel, 4:5"),
    "instagram-square": (1080, 1080, 20, "Instagram square, 1:1"),
    "instagram-tall": (1080, 1440, 20, "Instagram feed, 3:4"),
    "linkedin-portrait": (1080, 1350, 20, "LinkedIn image post, 4:5"),
    "linkedin-square": (1080, 1080, 20, "LinkedIn image post, 1:1"),
    "facebook-portrait": (1080, 1350, 10, "Facebook carousel, 4:5"),
    "facebook-square": (1080, 1080, 10, "Facebook carousel, 1:1"),
    "story": (1080, 1920, 20, "Story or reel, 9:16"),
}
# At 1080 pixels wide a feed slide shows about 390 points wide on a phone, so
# these floors keep text at about 20, 12 and 10 points there.
FLOOR = {"headline": 56, "support": 32, "label": 28}
BASE = {"headline": 112, "support": 42, "label": 34}
IMAGE_TYPES = {".png", ".jpg", ".jpeg", ".webp"}


class Stop(Exception):
    """A plain message for the person; nothing more was changed."""


# ── Images ──────────────────────────────────────────────────────────────
def image_size(path):
    """(width, height) from a PNG, JPEG or WebP header, or None."""
    with open(path, "rb") as f:
        head = f.read(32)
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">II", head[16:24])
        if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
            kind = head[12:16]
            if kind == b"VP8X":
                w = int.from_bytes(head[24:27], "little") + 1
                h = int.from_bytes(head[27:30], "little") + 1
                return w, h
            if kind == b"VP8 ":
                f.seek(26)
                w, h = struct.unpack("<HH", f.read(4))
                return w & 0x3FFF, h & 0x3FFF
            if kind == b"VP8L":
                b = head[21:25]
                w = 1 + (((b[1] & 0x3F) << 8) | b[0])
                h = 1 + (((b[3] & 0x0F) << 10) | (b[2] << 2) | ((b[1] & 0xC0) >> 6))
                return w, h
            return None
        if head[:2] == b"\xff\xd8":
            f.seek(2)
            while True:
                marker = f.read(2)
                if len(marker) < 2 or marker[0] != 0xFF:
                    return None
                if marker[1] in (0xD8, 0x01) or 0xD0 <= marker[1] <= 0xD7:
                    continue
                length = struct.unpack(">H", f.read(2))[0]
                if marker[1] in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    h, w = struct.unpack(">xHH", f.read(5))
                    return w, h
                f.seek(length - 2, 1)
    return None


def platform(name):
    if name not in PLATFORMS:
        raise Stop(f'Unknown platform "{name}". Use one of: {", ".join(PLATFORMS)}.')
    return PLATFORMS[name]


def check_images(paths, platform_name):
    """Problems with a set of slide images, as plain sentences. Empty means fine."""
    w, h, most, label = platform(platform_name)
    problems = []
    if not paths:
        return ["No slide images were given."]
    if len(paths) > most:
        problems.append(f"{label} takes at most {most} slides; there are {len(paths)}.")
    for p in paths:
        p = Path(p)
        if not p.is_file():
            problems.append(f"{p} is not there.")
            continue
        if p.suffix.lower() not in IMAGE_TYPES:
            problems.append(f"{p.name} is not a PNG, JPEG or WebP image.")
            continue
        size = image_size(p)
        if not size:
            problems.append(f"{p.name} cannot be read as an image.")
        elif size != (w, h):
            if size[0] * h == size[1] * w:
                problems.append(f"{p.name} is {size[0]}x{size[1]}: the right shape, but {label} wants {w}x{h}. Export it at that size.")
            else:
                problems.append(f"{p.name} is {size[0]}x{size[1]}, a different shape from {label} ({w}x{h}); the app would crop it. Remake or re-crop it.")
    return problems


def numbered(folder):
    """Images in a folder whose names start with a slide number, in posting order."""
    found = []
    for p in Path(folder).iterdir():
        m = re.match(r"^(\d{1,3})[-_ ]", p.name)
        if m and p.suffix.lower() in IMAGE_TYPES and p.is_file():
            found.append((int(m.group(1)), p.name, p))
    found.sort()
    return [p for _, _, p in found]


# ── Colour ──────────────────────────────────────────────────────────────
def _lum(hexcolour):
    rgb = [int(hexcolour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    hi, lo = sorted((_lum(a), _lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def is_hex(v):
    return isinstance(v, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", v) is not None


def readable_text(preferred, background):
    """The preferred text colour if it reads on the background, else black or white."""
    if is_hex(preferred) and contrast(preferred, background) >= 4.5:
        return preferred
    return "#FFFFFF" if contrast("#FFFFFF", background) >= contrast("#111111", background) else "#111111"


# ── Plans ───────────────────────────────────────────────────────────────
SLIDE_KEYS = {"headline", "support", "label", "image", "place", "keyword", "note"}
BRAND_KEYS = {"background", "text", "accent", "font", "font_file", "body_font", "body_font_file", "handle"}


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return s[:50] or "carousel"


def load_plan(path):
    try:
        raw = Path(path).read_text(encoding="utf-8-sig")
    except OSError as e:
        raise Stop(f"Cannot read the plan {path}: {e.strerror}.")
    try:
        plan = json.loads(raw)
    except json.JSONDecodeError as e:
        raise Stop(f"The plan {path} is not valid JSON (line {e.lineno}): {e.msg}.")
    return check_plan(plan, Path(path).parent)


def check_plan(plan, base=Path(".")):
    if not isinstance(plan, dict) or not isinstance(plan.get("slides"), list) or not plan["slides"]:
        raise Stop('The plan needs a "slides" list with at least one slide.')
    w, h, most, label = platform(plan.get("platform", "instagram-portrait"))
    errors, notes = [], []
    if len(plan["slides"]) > most:
        errors.append(f"{label} takes at most {most} slides; the plan has {len(plan['slides'])}.")
    brand = plan.get("brand") or {}
    for key in brand:
        if key not in BRAND_KEYS:
            notes.append(f'brand key "{key}" is not one the renderer reads.')
    for key in ("background", "text", "accent"):
        if key in brand and not is_hex(brand[key]):
            errors.append(f'brand "{key}" must be a colour like #1D4E89, not {brand[key]!r}.')
    for key in ("font_file", "body_font_file"):
        if brand.get(key) and not (base / Path(os.path.expanduser(brand[key]))).is_file():
            errors.append(f"The font file {brand[key]} is not there.")
    for n, s in enumerate(plan["slides"], 1):
        if not isinstance(s, dict) or not str(s.get("headline", "")).strip():
            errors.append(f'Slide {n} needs a "headline".')
            continue
        for key in s:
            if key not in SLIDE_KEYS:
                notes.append(f'slide {n}: key "{key}" is not one the renderer reads.')
        if s.get("place", "bottom") not in ("top", "center", "bottom"):
            errors.append(f'Slide {n}: "place" is top, center or bottom.')
        if s.get("image") and not (base / Path(os.path.expanduser(s["image"]))).is_file():
            errors.append(f"Slide {n}: the image {s['image']} is not there.")
        if s.get("keyword") and s["keyword"].lower() not in (s["headline"] + " " + s.get("support", "")).lower():
            errors.append(f'Slide {n}: the keyword "{s["keyword"]}" is not in its headline or support line.')
        for key in ("headline", "support", "label"):
            if re.search("[–—]", str(s.get(key, ""))):
                notes.append(f"slide {n}: {key} has a long dash; a comma or full stop reads better.")
    if errors:
        raise Stop("The plan cannot render yet:\n" + "\n".join(f"  - {e}" for e in errors))
    plan["_notes"] = notes
    plan["_base"] = str(base)
    return plan


def _data_url(path):
    ext = path.suffix.lower().lstrip(".")
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp",
            "ttf": "font/ttf", "otf": "font/otf", "woff": "font/woff", "woff2": "font/woff2"}.get(ext, "application/octet-stream")
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


FIT_JS = r"""
document.fonts.ready.then(() => {
  const el = document.getElementById('block');
  const safe = document.getElementById('safe').getBoundingClientRect();
  const over = () => {
    const r = el.getBoundingClientRect();
    if (r.top < safe.top - 1 || r.bottom > safe.bottom + 1) return true;
    for (const d of el.querySelectorAll('div')) if (d.scrollWidth > d.clientWidth + 1) return true;
    return false;
  };
  const set = v => el.style.setProperty('--s', v);
  const min = parseFloat(el.dataset.min);
  let lo = min, hi = 1.15, result = 'ok';
  set(hi);
  if (over()) {
    set(lo);
    if (over()) result = 'nofit';
    else { for (let i = 0; i < 14; i++) { const m = (lo + hi) / 2; set(m); if (over()) hi = m; else lo = m; } set(lo); }
  }
  const s = parseFloat(getComputedStyle(el).getPropertyValue('--s'));
  document.title = 'FIT ' + result + ' ' + s.toFixed(3);
  document.body.dataset.fit = result;
});
"""


def slide_html(plan, index):
    """One slide as a self-contained page at the platform's exact pixel size."""
    w, h, _, _ = platform(plan.get("platform", "instagram-portrait"))
    base = Path(plan["_base"])
    b = plan.get("brand") or {}
    s = plan["slides"][index]
    u = w / 1080
    bg = b.get("background", "#111111")
    accent = b.get("accent", "#F5C518")
    faces = []
    head_font, body_font = "system-ui, sans-serif", "system-ui, sans-serif"
    if b.get("font_file"):
        faces.append(f"@font-face {{ font-family: 'BrandHead'; src: url({_data_url(base / os.path.expanduser(b['font_file']))}); }}")
        head_font = "'BrandHead', sans-serif"
    elif b.get("font"):
        head_font = f"'{b['font']}', system-ui, sans-serif"
    if b.get("body_font_file"):
        faces.append(f"@font-face {{ font-family: 'BrandBody'; src: url({_data_url(base / os.path.expanduser(b['body_font_file']))}); }}")
        body_font = "'BrandBody', sans-serif"
    elif b.get("body_font"):
        body_font = f"'{b['body_font']}', system-ui, sans-serif"
    place = s.get("place", "bottom")
    pad = round(72 * u)
    if s.get("image"):
        backdrop = f"background:#000 url({_data_url(base / os.path.expanduser(s['image']))}) center/cover;"
        # A scrim behind the text, so it reads on any photo.
        direction = {"top": "to bottom", "bottom": "to top", "center": "to top"}[place]
        strength = "0.82" if place != "center" else "0.6"
        scrim = f'<div style="position:absolute;inset:0;background:linear-gradient({direction}, rgba(0,0,0,{strength}) 0%, rgba(0,0,0,0.45) 45%, rgba(0,0,0,0) 75%)"></div>' if place != "center" else '<div style="position:absolute;inset:0;background:rgba(0,0,0,0.5)"></div>'
        text = readable_text(b.get("text", "#FFFFFF"), "#1A1A1A")
        accent_text = accent if contrast(accent, "#1A1A1A") >= 3 else text
    else:
        backdrop = f"background:{bg};"
        scrim = ""
        text = readable_text(b.get("text"), bg)
        accent_text = accent if contrast(accent, bg) >= 3 else text

    def sized(kind, extra=""):
        return f"font-size:calc(var(--s) * {BASE[kind] * u:.1f}px);{extra}"

    headline = html.escape(s["headline"])
    support = html.escape(s.get("support", ""))
    if s.get("keyword"):
        kw = html.escape(s["keyword"])
        box = (f'<span style="background:{accent};color:{readable_text("#111111", accent)};padding:0 0.18em;'
               f'border-radius:0.12em;box-decoration-break:clone;-webkit-box-decoration-break:clone">{kw}</span>')
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        headline = pattern.sub(box, headline, count=1) if pattern.search(headline) else headline
        support = pattern.sub(box, support, count=1) if pattern.search(support) else support
    footer_h = round(110 * u) if b.get("handle") else pad
    justify = {"top": "flex-start", "center": "center", "bottom": "flex-end"}[place]
    smallest = min(FLOOR[k] / BASE[k] for k in ("headline", "support", "label"))
    parts = []
    if s.get("label"):
        parts.append(f'<div style="{sized("label", f"font-family:{body_font};font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:{accent_text};margin-bottom:calc(var(--s) * {18*u:.1f}px)")}">{html.escape(s["label"])}</div>')
    parts.append(f'<div style="{sized("headline", f"font-family:{head_font};font-weight:800;line-height:1.02;letter-spacing:-0.01em;color:{text};overflow-wrap:normal;word-break:normal")}">{headline}</div>')
    if support:
        parts.append(f'<div style="{sized("support", f"font-family:{body_font};font-weight:500;line-height:1.35;color:{text};opacity:0.92;margin-top:calc(var(--s) * {26*u:.1f}px)")}">{support}</div>')
    handle = (f'<div style="position:absolute;left:{pad}px;bottom:{round(48*u)}px;font-family:{body_font};font-weight:700;'
              f'font-size:{round(30*u)}px;color:{text};opacity:0.9">{html.escape(b["handle"])}</div>') if b.get("handle") else ""
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>slide</title><style>
{"".join(faces)}
* {{ margin:0; padding:0; box-sizing:border-box; font-synthesis:none; }}
html, body {{ width:{w}px; height:{h}px; overflow:hidden; }}
body {{ position:relative; {backdrop} -webkit-font-smoothing:antialiased; }}
#safe {{ position:absolute; left:{pad}px; right:{pad}px; top:{pad}px; bottom:{footer_h}px; display:flex; flex-direction:column; justify-content:{justify}; }}
#block {{ --s:1; }}
</style></head><body>{scrim}
<div id="safe"><div id="block" data-min="{max(FLOOR[k] / BASE[k] for k in ("headline", "support", "label")):.3f}">{"".join(parts)}</div></div>
{handle}
<script>{FIT_JS}</script></body></html>""", smallest


# ── Browser ─────────────────────────────────────────────────────────────
def find_browser(env=os.environ, exists=os.path.isfile, which=shutil.which, system=sys.platform):
    if env.get("CAROUSEL_BROWSER"):
        return env["CAROUSEL_BROWSER"] if exists(env["CAROUSEL_BROWSER"]) else None
    if system == "darwin":
        apps = ["Google Chrome", "Microsoft Edge", "Chromium", "Brave Browser"]
        roots = ["/Applications", os.path.expanduser("~/Applications")]
        for root in roots:
            for app in apps:
                p = f"{root}/{app}.app/Contents/MacOS/{app}"
                if exists(p):
                    return p
    if system.startswith("win"):
        for root in (env.get("ProgramFiles"), env.get("ProgramFiles(x86)"), env.get("LOCALAPPDATA")):
            if not root:
                continue
            for rel in (r"Google\Chrome\Application\chrome.exe", r"Microsoft\Edge\Application\msedge.exe",
                        r"BraveSoftware\Brave-Browser\Application\brave.exe"):
                p = os.path.join(root, rel)
                if exists(p):
                    return p
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "brave-browser"):
        p = which(name)
        if p:
            return p
    return None


def _browser(browser, args, timeout=60):
    profile = tempfile.mkdtemp(prefix="slides-profile-")
    try:
        cmd = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run", "--no-default-browser-check",
               "--force-device-scale-factor=1", f"--user-data-dir={profile}", "--virtual-time-budget=4000", *args]
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    finally:
        shutil.rmtree(profile, ignore_errors=True)


def render(plan, out, browser=None, dry_run=False, log=print):
    w, h, _, label = platform(plan.get("platform", "instagram-portrait"))
    name = slug(plan.get("name", "carousel"))
    out = Path(out)
    names = [f"{i + 1:02d}-{name}.png" for i in range(len(plan["slides"]))]
    for note in plan.get("_notes", []):
        log(f"  note: {note}")
    if dry_run:
        log(f"Would render {len(names)} slide(s) at {w}x{h} ({label}) into {out}:")
        for n in names:
            log(f"  {n}")
        return names
    browser = browser or find_browser()
    if not browser:
        raise Stop("No Chrome, Edge, Chromium or Brave found on this computer, so nothing was rendered. "
                   "Install one of them, or set CAROUSEL_BROWSER to its program file.")
    work = Path(tempfile.mkdtemp(prefix=f"slides-{name}-"))
    problems = []
    try:
        for i in range(len(names)):
            page, _ = slide_html(plan, i)
            src = work / f"{i + 1:02d}.html"
            src.write_text(page, encoding="utf-8")
            url = src.resolve().as_uri()
            dom = _browser(browser, ["--dump-dom", url])
            m = re.search(r"<title>FIT (\w+)", dom.stdout or "")
            if not m:
                raise Stop(f"The browser did not finish drawing slide {i + 1}: {(dom.stderr or '').strip()[:300]}")
            if m.group(1) != "ok":
                problems.append(f"Slide {i + 1}: the words do not fit even at the smallest size that reads on a phone. Cut words or split the slide.")
                continue
            shot = work / names[i]
            r = _browser(browser, [f"--window-size={w},{h}", f"--screenshot={shot}", url])
            if not shot.is_file():
                raise Stop(f"The browser did not save slide {i + 1}: {(r.stderr or '').strip()[:300]}")
            size = image_size(shot)
            if size != (w, h):
                raise Stop(f"Slide {i + 1} came out at {size}, not {w}x{h}. Nothing was saved.")
        if problems:
            raise Stop("Nothing was saved, because:\n" + "\n".join(f"  - {p}" for p in problems))
        out.mkdir(parents=True, exist_ok=True)
        moved = set_aside(out, name)
        if moved:
            log(f"The earlier render of these slides is now in {moved}")
        for n in names:
            shutil.copy2(work / n, out / n)
        log(f"Saved {len(names)} slide(s), {w}x{h} each, in posting order, in {out}")
        return names
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _stamp():
    return time.strftime("%Y%m%d-%H%M%S")


def set_aside(folder, name):
    """Move this carousel's earlier numbered files into earlier/<time>/. Nothing else moves."""
    pattern = re.compile(rf"^\d{{2}}-{re.escape(name)}\.png$")
    old = sorted(p for p in Path(folder).iterdir() if p.is_file() and pattern.match(p.name))
    if not old:
        return None
    dest = Path(folder) / "earlier" / _stamp()
    k = 2
    while dest.exists():
        dest = Path(folder) / "earlier" / f"{_stamp()}-{k}"
        k += 1
    dest.mkdir(parents=True)
    for p in old:
        p.rename(dest / p.name)
    return dest


def finalise(files, project, name, platform_name, dry_run=False, log=print):
    """Copy approved files, in the order given, to <project>/final/NN-<name>.<ext>.
    Earlier finals move to alternates/replaced-<time>/ first; nothing is overwritten."""
    problems = check_images(files, platform_name)
    if problems:
        raise Stop("Not finalised, because:\n" + "\n".join(f"  - {p}" for p in problems))
    final = Path(project) / "final"
    name = slug(name)
    targets = [final / f"{i + 1:02d}-{name}{Path(f).suffix.lower().replace('.jpeg', '.jpg')}" for i, f in enumerate(files)]
    sources = [Path(f).resolve() for f in files]
    if len(set(sources)) != len(sources):
        raise Stop("The same file is listed twice. Give each slide once, in posting order.")
    if any(s.parent == final.resolve() for s in sources):
        raise Stop(f"These files are already in {final}. Give the approved files from where they were made.")
    existing = sorted(p for p in final.iterdir() if p.is_file()) if final.is_dir() else []
    aside = Path(project) / "alternates" / f"replaced-{_stamp()}"
    if dry_run:
        if existing:
            log(f"Would move {len(existing)} earlier final file(s) to {aside}")
        for s, t in zip(sources, targets):
            log(f"Would copy {s} to {t}")
        return targets
    if existing:
        k = 2
        while aside.exists():
            aside = Path(project) / "alternates" / f"replaced-{_stamp()}-{k}"
            k += 1
        aside.mkdir(parents=True)
        for p in existing:
            p.rename(aside / p.name)
        log(f"Moved the earlier final files to {aside}")
    final.mkdir(parents=True, exist_ok=True)
    for s, t in zip(sources, targets):
        tmp = t.with_name(f".{t.name}.tmp")
        shutil.copy2(s, tmp)
        os.replace(tmp, t)
    log(f"{len(targets)} slide(s) in {final}, numbered in posting order:")
    for t in targets:
        log(f"  {t.name}")
    return targets


def main(argv=None):
    ap = argparse.ArgumentParser(prog="slides.py", description="The fixed steps of a business carousel.", allow_abbrev=False)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("sizes", allow_abbrev=False, help="platform sizes and slide limits")
    sub.add_parser("selftest", allow_abbrev=False, help="render one test slide in a temporary folder")
    r = sub.add_parser("render", allow_abbrev=False, help="render a plan's slides with text fitted")
    r.add_argument("plan")
    r.add_argument("--out", required=True)
    r.add_argument("--dry-run", action="store_true")
    c = sub.add_parser("check", allow_abbrev=False, help="check a folder of slide images")
    c.add_argument("folder")
    c.add_argument("--platform", required=True)
    f = sub.add_parser("finalise", allow_abbrev=False, help="copy approved slides into final/ in posting order")
    f.add_argument("images", nargs="+")
    f.add_argument("--project", required=True)
    f.add_argument("--name", required=True)
    f.add_argument("--platform", required=True)
    f.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "sizes":
            for key, (w, h, most, label) in PLATFORMS.items():
                print(f"{key:20} {w}x{h}  {label}, up to {most} slides")
            print("A cover or single image: use the same size, one slide.")
        elif args.cmd == "selftest":
            browser = find_browser()
            if not browser:
                raise Stop("No Chrome, Edge, Chromium or Brave found, so render cannot draw slides here. "
                           "Everything else works; slides from an image tool can still be checked and finalised.")
            with tempfile.TemporaryDirectory() as tmp:
                plan = check_plan({"name": "test", "slides": [{"headline": "Test slide", "support": "If you can read this, rendering works."}]}, Path(tmp))
                names = render(plan, Path(tmp) / "out", browser=browser, log=lambda *_: None)
                size = image_size(Path(tmp) / "out" / names[0])
            print(f"ok: rendered a {size[0]}x{size[1]} test slide with {browser}")
        elif args.cmd == "render":
            plan = load_plan(args.plan)
            render(plan, args.out, dry_run=args.dry_run)
        elif args.cmd == "check":
            folder = Path(args.folder)
            if not folder.is_dir():
                raise Stop(f"{folder} is not a folder.")
            files = numbered(folder)
            problems = check_images(files, args.platform)
            if problems:
                print("Not ready to post:")
                for p in problems:
                    print(f"  - {p}")
                return 1
            w, h, _, label = PLATFORMS[args.platform]
            print(f"{len(files)} slide(s), all {w}x{h} ({label}), in this order:")
            for p in files:
                print(f"  {p.name}")
        elif args.cmd == "finalise":
            finalise(args.images, args.project, args.name, args.platform, dry_run=args.dry_run)
    except Stop as e:
        print(str(e), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
