"""Offline tests for skills/business-carousels/scripts/slides.py.
Run: python3 -m unittest discover -s tests   (Windows: py -m unittest discover -s tests)"""
import contextlib
import importlib.util
import io
import json
import os
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "skills" / "business-carousels" / "scripts" / "slides.py"
spec = importlib.util.spec_from_file_location("slides", SCRIPT)
slides = importlib.util.module_from_spec(spec)
spec.loader.exec_module(slides)


def png(path, w, h):
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    raw = zlib.compress((b"\x00" + b"\x80\x80\x80" * w) * h)
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + chunk(b"IDAT", raw) + chunk(b"IEND", b""))


def jpeg(path, w, h):
    sof = b"\xff\xc0" + struct.pack(">HBHHB", 11, 8, h, w, 1) + b"\x01\x11\x00"
    Path(path).write_bytes(b"\xff\xd8" + b"\xff\xe0" + struct.pack(">H", 16) + b"JFIF\x00" + b"\x00" * 9 + sof + b"\xff\xd9")


def webp(path, w, h):
    body = b"VP8X" + struct.pack("<I", 10) + b"\x00\x00\x00\x00" + (w - 1).to_bytes(3, "little") + (h - 1).to_bytes(3, "little")
    Path(path).write_bytes(b"RIFF" + struct.pack("<I", 4 + len(body)) + b"WEBP" + body)


def snapshot(root):
    return {str(p.relative_to(root)): (p.read_bytes() if p.is_file() else None) for p in sorted(Path(root).rglob("*"))}


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = slides.main(list(argv))
        except SystemExit as e:
            code = e.code
    return code, out.getvalue() + err.getvalue()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)


class Sizes(Base):
    def test_png_jpeg_and_webp_sizes_come_from_the_header(self):
        png(self.root / "a.png", 1080, 1350)
        jpeg(self.root / "b.jpg", 1024, 1536)
        webp(self.root / "c.webp", 1080, 1080)
        self.assertEqual(slides.image_size(self.root / "a.png"), (1080, 1350))
        self.assertEqual(slides.image_size(self.root / "b.jpg"), (1024, 1536))
        self.assertEqual(slides.image_size(self.root / "c.webp"), (1080, 1080))
        (self.root / "d.png").write_text("not an image")
        self.assertIsNone(slides.image_size(self.root / "d.png"))

    def test_a_generated_2_by_3_image_is_flagged_as_the_wrong_shape(self):
        png(self.root / "1.png", 1080, 1350)
        png(self.root / "2.png", 1024, 1536)
        png(self.root / "3.png", 2160, 2700)
        problems = slides.check_images([self.root / "1.png", self.root / "2.png", self.root / "3.png"], "instagram-portrait")
        self.assertEqual(len(problems), 2)
        self.assertIn("2.png is 1024x1536, a different shape", problems[0])
        self.assertIn("3.png is 2160x2700: the right shape", problems[1])

    def test_slide_limits_per_platform(self):
        files = []
        for i in range(11):
            png(self.root / f"{i}.png", 1080, 1080)
            files.append(self.root / f"{i}.png")
        self.assertEqual(slides.check_images(files, "instagram-square"), [])
        self.assertIn("at most 10 slides", slides.check_images(files, "facebook-square")[0])
        self.assertEqual(slides.check_images([], "instagram-square"), ["No slide images were given."])
        with self.assertRaises(slides.Stop):
            slides.check_images(files, "tiktok")

    def test_numbered_files_sort_as_numbers_and_others_are_ignored(self):
        for name in ["10-end.png", "2-two.png", "1-cover.png", "notes.png", "03-three.jpg", "4-four.txt"]:
            png(self.root / name, 10, 10)
        self.assertEqual([p.name for p in slides.numbered(self.root)], ["1-cover.png", "2-two.png", "03-three.jpg", "10-end.png"])


class Plans(Base):
    def plan(self, **kw):
        p = {"platform": "instagram-portrait", "name": "x", "slides": [{"headline": "Hello"}]}
        p.update(kw)
        return p

    def test_a_good_plan_passes_with_notes_for_typos_and_dashes(self):
        p = slides.check_plan(self.plan(slides=[{"headline": "Fast \u2014 cheap", "suport": "x"}]), self.root)
        self.assertTrue(any("suport" in n for n in p["_notes"]))
        self.assertTrue(any("long dash" in n for n in p["_notes"]))

    def test_plan_errors_are_named_before_anything_renders(self):
        cases = [
            (self.plan(slides=[]), "at least one slide"),
            (self.plan(platform="tiktok"), 'Unknown platform "tiktok"'),
            (self.plan(slides=[{"support": "no headline"}]), 'needs a "headline"'),
            (self.plan(slides=[{"headline": "Hi", "place": "left"}]), "top, center or bottom"),
            (self.plan(slides=[{"headline": "Hi", "image": "missing.jpg"}]), "missing.jpg is not there"),
            (self.plan(slides=[{"headline": "Comment now", "keyword": "GUIDE"}]), 'keyword "GUIDE" is not in'),
            (self.plan(slides=[{"headline": "Roots in pipes", "highlight": "drains"}]), 'highlight "drains" is not in'),
            (self.plan(brand={"accent": "yellow"}), "must be a colour"),
            (self.plan(brand={"font_file": "nope.ttf"}), "nope.ttf is not there"),
            (self.plan(slides=[{"headline": "x"}] * 21), "at most 20 slides"),
        ]
        for plan, message in cases:
            with self.subTest(message=message):
                with self.assertRaises(slides.Stop) as ctx:
                    slides.check_plan(plan, self.root)
                self.assertIn(message, str(ctx.exception))

    def test_a_plan_that_is_not_json_is_a_plain_error(self):
        (self.root / "plan.json").write_text("{not json")
        with self.assertRaises(slides.Stop) as ctx:
            slides.load_plan(self.root / "plan.json")
        self.assertIn("not valid JSON", str(ctx.exception))
        (self.root / "bom.json").write_bytes(b"\xef\xbb\xbf" + json.dumps(self.plan()).encode())
        self.assertEqual(slides.load_plan(self.root / "bom.json")["name"], "x")

    def test_text_is_escaped_and_the_keyword_is_highlighted(self):
        p = slides.check_plan(self.plan(slides=[{"headline": "Tom & Jo <b>", "support": "Comment GUIDE below", "keyword": "GUIDE"}]), self.root)
        page, _ = slides.slide_html(p, 0)
        self.assertIn("Tom &amp; Jo &lt;b&gt;", page)
        self.assertRegex(page, r"<span style=\"background:#F5C518[^>]*>GUIDE</span>")
        self.assertIn("width:1080px; height:1350px", page)

    def test_the_highlight_prints_in_the_brand_colour(self):
        p = slides.check_plan(self.plan(brand={"background": "#0B1F33", "accent": "#F5C518"}, slides=[{"headline": "Your drain keeps blocking. Here's why.", "highlight": "Here's why."}]), self.root)
        page, _ = slides.slide_html(p, 0)
        self.assertIn('<span style="color:#F5C518">Here&#x27;s why.</span>', page)

    def test_text_colour_always_reads_on_the_background(self):
        self.assertEqual(slides.readable_text("#F5C518", "#F5F0EB"), "#111111")
        self.assertEqual(slides.readable_text("#F5C518", "#0B1F33"), "#F5C518")
        self.assertEqual(slides.readable_text(None, "#0B1F33"), "#FFFFFF")


class Files(Base):
    def test_finalise_numbers_in_the_given_order_and_never_overwrites(self):
        project = self.root / "proj"
        trials = project / "trials"
        trials.mkdir(parents=True)
        for name in ["b.png", "a.png"]:
            png(trials / name, 1080, 1350)
        slides.finalise([trials / "b.png", trials / "a.png"], project, "Drain Tips", "instagram-portrait", log=lambda *_: None)
        self.assertEqual(sorted(p.name for p in (project / "final").iterdir()), ["01-drain-tips.png", "02-drain-tips.png"])
        self.assertEqual((project / "final" / "01-drain-tips.png").read_bytes(), (trials / "b.png").read_bytes())
        first = (project / "final" / "01-drain-tips.png").read_bytes()
        png(trials / "c.png", 1080, 1350)
        slides.finalise([trials / "c.png"], project, "Drain Tips", "instagram-portrait", log=lambda *_: None)
        moved = list((project / "alternates").glob("replaced-*/01-drain-tips.png"))
        self.assertEqual(len(moved), 1)
        self.assertEqual(moved[0].read_bytes(), first)
        self.assertEqual(sorted(p.name for p in (project / "final").iterdir()), ["01-drain-tips.png"])

    def test_finalise_stops_on_a_wrong_size_and_changes_nothing(self):
        project = self.root / "proj"
        (project / "trials").mkdir(parents=True)
        png(project / "trials" / "1.png", 1080, 1350)
        png(project / "trials" / "2.png", 1024, 1536)
        before = snapshot(project)
        with self.assertRaises(slides.Stop) as ctx:
            slides.finalise([project / "trials" / "1.png", project / "trials" / "2.png"], project, "x", "instagram-portrait")
        self.assertIn("2.png is 1024x1536", str(ctx.exception))
        self.assertEqual(snapshot(project), before)

    def test_finalise_refuses_duplicates_and_files_already_final(self):
        project = self.root / "proj"
        (project / "final").mkdir(parents=True)
        png(project / "final" / "01-x.png", 1080, 1350)
        png(self.root / "a.png", 1080, 1350)
        with self.assertRaises(slides.Stop):
            slides.finalise([self.root / "a.png", self.root / "a.png"], project, "x", "instagram-portrait")
        with self.assertRaises(slides.Stop):
            slides.finalise([project / "final" / "01-x.png"], project, "x", "instagram-portrait")

    def test_dry_runs_write_nothing(self):
        project = self.root / "proj"
        (project / "final").mkdir(parents=True)
        png(project / "final" / "01-old.png", 1080, 1350)
        png(self.root / "a.png", 1080, 1350)
        (self.root / "plan.json").write_text(json.dumps({"name": "x", "slides": [{"headline": "Hi"}]}))
        before = snapshot(self.root)
        code, out = run("finalise", str(self.root / "a.png"), "--project", str(project), "--name", "x", "--platform", "instagram-portrait", "--dry-run")
        self.assertEqual(code, 0)
        self.assertIn("Would move 1 earlier final", out)
        code, out = run("render", str(self.root / "plan.json"), "--out", str(self.root / "out"), "--dry-run")
        self.assertEqual(code, 0)
        self.assertIn("01-x.png", out)
        self.assertEqual(snapshot(self.root), before)

    def test_set_aside_moves_only_this_carousels_numbered_files(self):
        for name in ["01-tips.png", "02-tips.png", "01-other.png", "notes.txt"]:
            (self.root / name).write_text(name)
        dest = slides.set_aside(self.root, "tips")
        self.assertEqual(sorted(p.name for p in dest.iterdir()), ["01-tips.png", "02-tips.png"])
        self.assertEqual(sorted(p.name for p in self.root.iterdir() if p.is_file()), ["01-other.png", "notes.txt"])
        self.assertIsNone(slides.set_aside(self.root, "tips"))


class CommandLine(Base):
    def test_help_prints_usage_and_a_misspelt_option_stops(self):
        before = snapshot(self.root)
        code, out = run("--help")
        self.assertEqual(code, 0)
        self.assertIn("usage: slides.py", out)
        code, out = run("finalise", "a.png", "--projekt", str(self.root), "--name", "x", "--platform", "instagram-portrait")
        self.assertEqual(code, 2)
        self.assertIn("error:", out)
        code, out = run("check", str(self.root), "--plat", "instagram-portrait")
        self.assertEqual(code, 2, "an abbreviated option is not guessed")
        code, out = run("render", "plan.json")
        self.assertEqual(code, 2)
        self.assertIn("--out", out)
        self.assertEqual(snapshot(self.root), before)

    def test_check_reports_a_folder(self):
        png(self.root / "1-a.png", 1080, 1350)
        png(self.root / "2-b.png", 1080, 1080)
        code, out = run("check", str(self.root), "--platform", "instagram-portrait")
        self.assertEqual(code, 1)
        self.assertIn("2-b.png is 1080x1080", out)
        code, out = run("check", str(self.root / "missing"), "--platform", "instagram-portrait")
        self.assertEqual(code, 2)

    def test_selftest_without_a_browser_says_what_still_works(self):
        os.environ["CAROUSEL_BROWSER"] = str(self.root / "no-browser")
        self.addCleanup(os.environ.pop, "CAROUSEL_BROWSER", None)
        code, out = run("selftest")
        self.assertEqual(code, 2)
        self.assertIn("can still be checked and finalised", out)

    def test_finding_a_browser_on_each_system(self):
        mac = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        self.assertEqual(slides.find_browser(env={}, exists=lambda p: p == mac, which=lambda n: None, system="darwin"), mac)
        edge = os.path.join(r"C:\Program Files (x86)", r"Microsoft\Edge\Application\msedge.exe")
        self.assertEqual(slides.find_browser(env={"ProgramFiles(x86)": r"C:\Program Files (x86)"}, exists=lambda p: p == edge, which=lambda n: None, system="win32"), edge)
        self.assertEqual(slides.find_browser(env={}, exists=lambda p: False, which=lambda n: "/usr/bin/chromium" if n == "chromium" else None, system="linux"), "/usr/bin/chromium")
        self.assertIsNone(slides.find_browser(env={}, exists=lambda p: False, which=lambda n: None, system="linux"))
        self.assertIsNone(slides.find_browser(env={"CAROUSEL_BROWSER": "/nope"}, exists=lambda p: False, which=lambda n: None))


@unittest.skipUnless(slides.find_browser(), "no Chrome, Edge, Chromium or Brave on this computer")
class Render(Base):
    def test_slides_render_at_the_exact_size_and_an_overfull_slide_saves_nothing(self):
        plan = slides.check_plan({"platform": "instagram-portrait", "name": "Drain tips", "brand": {"background": "#0B1F33", "handle": "@shop"},
                                  "slides": [{"headline": "Your drain keeps blocking", "support": "Here's why."}, {"headline": "Comment DRAINS", "keyword": "DRAINS"}]}, self.root)
        names = slides.render(plan, self.root / "out", log=lambda *_: None)
        self.assertEqual(names, ["01-drain-tips.png", "02-drain-tips.png"])
        for n in names:
            self.assertEqual(slides.image_size(self.root / "out" / n), (1080, 1350))
        long = slides.check_plan({"name": "long", "slides": [{"headline": "Why " * 60, "support": "words " * 120}]}, self.root)
        with self.assertRaises(slides.Stop) as ctx:
            slides.render(long, self.root / "out2", log=lambda *_: None)
        self.assertIn("do not fit", str(ctx.exception))
        self.assertFalse((self.root / "out2").exists())


if __name__ == "__main__":
    unittest.main()
