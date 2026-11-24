#!/usr/bin/env python3
"""
make_image.py -- front page for Tuesday, 24 November 2026.

The page is composed at 2048 x 2048 and reduced to a 1024 x 1024 PNG.
Pillow is used when it can be found.  When it cannot, the same layout is
painted by a small built-in raster canvas and encoded with zlib, so the
generator has no hard third-party dependency.
"""

from __future__ import annotations

import base64
import glob
import math
import os
import struct
import sys
import zlib

# --------------------------------------------------------------------------
# Optional Pillow discovery (plain import first, then a few common locations)
# --------------------------------------------------------------------------

def _load_pillow():
    try:
        from PIL import Image, ImageDraw, ImageFont
        return Image, ImageDraw, ImageFont
    except Exception:
        pass
    patterns = [
        "/nix/store/*pillow*/lib/python3.13/site-packages",
        "/nix/store/*pillow*/lib/python3.*/site-packages",
        "/usr/lib/python3*/site-packages",
        "/usr/local/lib/python3*/site-packages",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"),
    ]
    for pattern in patterns:
        for path in sorted(glob.glob(pattern), reverse=True):
            if not os.path.isdir(path) or path in sys.path:
                continue
            sys.path.insert(0, path)
            try:
                from PIL import Image, ImageDraw, ImageFont
                return Image, ImageDraw, ImageFont
            except Exception:
                sys.path.remove(path)
    return None


PIL = _load_pillow()

# --------------------------------------------------------------------------
# Palette -- newsprint, deep navy sea, hot orange fire, sand map
# --------------------------------------------------------------------------

PAPER      = (250, 247, 239)
PANEL      = (244, 239, 227)
INK        = (18, 27, 39)
NAVY       = (10, 30, 50)
SEA        = (8, 38, 60)
SEA_DEEP   = (6, 27, 45)
SEA_LINE   = (24, 68, 94)
ORANGE     = (231, 88, 24)
AMBER      = (255, 172, 55)
SAND       = (216, 190, 139)
SAND_LIGHT = (231, 210, 168)
SAND_DARK  = (176, 145, 92)
WHITE      = (255, 255, 255)
GREY       = (104, 112, 123)
MID_GREY   = (150, 155, 160)
RULE       = (196, 190, 176)
RED        = (176, 42, 34)
GREEN      = (34, 112, 74)
TEAL       = (32, 104, 112)
STEEL      = (138, 150, 160)
SMOKE      = (92, 106, 118)

W = H = 2048
M = 72                  # page margin
RIGHT = W - M           # 1976
COL = RIGHT - M         # 1904

# --------------------------------------------------------------------------
# Font resolution for the Pillow backend
# --------------------------------------------------------------------------

FONT_PATTERNS = {
    "masthead": [
        "*dejavu-fonts-2.37/share/fonts/truetype/DejaVuSerifCondensed-Bold.ttf",
        "*dejavu*/share/fonts/truetype/DejaVuSerifCondensed-Bold.ttf",
        "*/DejaVuSerifCondensed-Bold.ttf",
        "*/DejaVuSerif-Bold.ttf",
        "*/LiberationSerif-Bold.ttf",
    ],
    "display": [
        "*dejavu-fonts-2.37/share/fonts/truetype/DejaVuSerifCondensed-Bold.ttf",
        "*dejavu*/share/fonts/truetype/DejaVuSerifCondensed-Bold.ttf",
        "*/DejaVuSerifCondensed-Bold.ttf",
        "*/DejaVuSerif-Bold.ttf",
        "*/LiberationSerif-Bold.ttf",
    ],
    "serif": [
        "*dejavu-fonts-2.37/share/fonts/truetype/DejaVuSerif.ttf",
        "*dejavu*/share/fonts/truetype/DejaVuSerif.ttf",
        "*/DejaVuSerif.ttf",
        "*/LiberationSerif-Regular.ttf",
    ],
    "serifbold": [
        "*dejavu-fonts-2.37/share/fonts/truetype/DejaVuSerif-Bold.ttf",
        "*dejavu*/share/fonts/truetype/DejaVuSerif-Bold.ttf",
        "*/DejaVuSerif-Bold.ttf",
        "*/LiberationSerif-Bold.ttf",
    ],
    "italic": [
        "*dejavu-fonts-2.37/share/fonts/truetype/DejaVuSerif-Italic.ttf",
        "*dejavu*/share/fonts/truetype/DejaVuSerif-Italic.ttf",
        "*/DejaVuSerif-Italic.ttf",
        "*/LiberationSerif-Italic.ttf",
    ],
    "sans": [
        "*dejavu-fonts-2.37/share/fonts/truetype/DejaVuSans.ttf",
        "*dejavu*/share/fonts/truetype/DejaVuSans.ttf",
        "*/DejaVuSans.ttf",
        "*/LiberationSans-Regular.ttf",
    ],
    "sansbold": [
        "*dejavu-fonts-2.37/share/fonts/truetype/DejaVuSans-Bold.ttf",
        "*dejavu*/share/fonts/truetype/DejaVuSans-Bold.ttf",
        "*/DejaVuSans-Bold.ttf",
        "*/LiberationSans-Bold.ttf",
    ],
}

_font_file_cache = {}
_pil_font_cache = {}


def _font_file(kind):
    if kind in _font_file_cache:
        return _font_file_cache[kind]
    for pattern in FONT_PATTERNS.get(kind, FONT_PATTERNS["sans"]):
        for base in ("/nix/store/", "/usr/share/fonts/", "/usr/local/share/fonts/", ""):
            hits = glob.glob(base + pattern)
            if hits:
                _font_file_cache[kind] = hits[0]
                return hits[0]
    _font_file_cache[kind] = None
    return None


# --------------------------------------------------------------------------
# A compact proportional bitmap face, used only by the dependency-free path
# --------------------------------------------------------------------------

_BITMAP_FONT = (
    "000000000000000000000000000000000000000000IC800saC00IC40000000sa600000000000000000jUA00jUA0000000000"
    "00000000000000000000pa7r%paJj)KmkAl;0HhgfC2yj00000000000000000001fCB&p00jUCzyUx3KmmXU009620000000000"
    "5C<RyAPqnTSO=^CqyQuVI0FCx000000000000000fCB&m00IC45C^aX-~?a<@B;t<00000000000000000aO800aO80000000000"
    "000000000000000000000000200IC600aO800aO800aOA00IC200000000000000400sa800IC400IC400IC400aO80000000000"
    "00Mvt00)2v00IC20000000000000000000000000fB=91fB=91@CSeZfB=91000000000000000000000000400aO40000000000"
    "0000000000000000000000sa60000000000000000000000000000000000000aO800000000000000000000000000000000000"
    "0096300IC400saA00aO800;mG000000000000000fCIn=Km<SpKm<SpKm@=9fCB&k00000000000000000RIA009620096200962"
    "zy|;T000000000000000fCs<?zyQDifB*mi00RI9zy|;T000000000000000fCs<;Kmfo1fCIn)Kmfo1fCm5o000000000000000"
    "fB=92fCGR6fCPX9zz=``fB*mh000000000000000fCm5s00e*szyv@5Kmfo1fCm5o000000000000000zykmV00e*qzy?4BKm<Sp"
    "fCB&k000000000000000zz4tpfB=91fB^sj0096400IC2000000000000000fCIn=Km@=BfCE4TKm<SpfCm5o000000000000000"
    "fCIn;Km<Spzy!bpKmfo1fCm5o00000000000000000006000000000000sa60000000000000000000000006000000000000aO8"
    "00000000000000000000FaY2HfCB&qzyWXo0000000000000000000000000@CWb*008g@000000000000000000000000000000"
    "00w{q@BlCXzySaU000000000000000000000000000)2tfB=9200RI500IC400IC2000000000000000KmhOo2m;guv;`Ce6b1MN"
    "Py`SH@Bsh-000000000000DpjfC9h*KmtGp;0GWKAP4{e000000000000000fCs<?Km<Spzz1LiU<6<Uzy|;T000000000000000"
    "zylx#00aO800aO800bZg-~#{v000000000000000fCu0NAOtW3Fa$6JFa%%(zy|;T000000000000000zy|;X00aO8zy|;X00aO8"
    "zy|;T000000000000000zy|;X00aO8fCm5s00aO800aO4000000000000000-~%8A00aO8U<7akFa$6L-~#{v000000000000000"
    "AOs);AOs);;0GWCAOs);AOrva00000000000000000aO800aO800aO800aO800aO400000000000000000aO800aO800aO800aO8"
    "00aO801N;C0000000000U<AMffCT^t00#gEfCRt<U<3dF00000000000000000aO800aO800aO800aO8zy|;T000000000000000"
    "5C$*?Fb8l2PzBHh&;$?!5Ci}K000000000000000AO;`?AO|1?paq}=-~?a<U<3dF000000000000000zyn|gFa!_;5CjkeFa#h5"
    "zykmP000000000000000fCs<?Km<Spzy|;a00aO800aO4000000000000000zyn|gFa!_;5CjkeFa#h5zym-4AOHXW0000000000"
    "fCs<?Km<Spzz4tvKm=d}AOrva000000000000000zym-800aOAfCIn)Kmb4hzy|;T000000000000000;12);009620096200962"
    "00961000000000000000AOs);AOs);AOs);AOv6rzykmP000000000000000AP67~U<5z}KnB19fC7L6fB^si000000000000000"
    "L=40P<OHk)s0OG9I0G017y|$R000000000000000AOt`Lzyg2)fB}F5zyd%7U<3dF000000000000000KnOqtfChjA00RI400962"
    "00961000000000000000;0Is;zyN>%0096400IC6;12)*0000000000000000000600aO800aO800aO800aO800aOA0000000000"
    "00;mG01N;G00aO800IC400IC50000000000000000000600IC400IC400IC400IC400IC80000000000fB?V&AOZjY0000000000"
    "0000000000000000000000000zz+Zb00000000000000000000000000000000aO600000000000000000000000000000000000"
    "00)2szyQDpzy!bqzy|;T000000000000000000000000400e*qzy?4BKm<SpKn8#Z000000000000000fCB&q00aO800aO8fCB&k"
    "00000000000000000000002M$Kmb4kzy?4BKm<Spzy!bt000000000000000fCIn=Km@=C00aO8zykmP00000000000000000000"
    "0000300aOJ00saA00aO800aO8000000000000000Km))AKm<SpKm@=9zym-4fCm5r0000000000000000000400e*qzy?4BKm<Sp"
    "Km<Sp000000000000000000040000400aO800aO800aO8000000000000000000040000400aO800aO800aO800aOG00;m800000"
    "0000400ck;fCK;q00saDfCaz=0000000000000000000400aO800aO800aO800aO8000000000000000m<8wtOax2>Oax2>OauS`"
    "00000000000000000000fCaz?Km<SpKm<SpKm-5)00000000000000000000fCIn=Km<SpKm@=9fCm5o00000000000000000000"
    "fCaz?Km<SpKm<SrfCm5s00aO8000000000000000Km))AKm<SpKm@=9zz0A8Kmb4h00000000000000000jUB00aO800aO800aO4"
    "00000000000000000000fCGR800aOBfB}F2fCm5o0000000000000000000000aO801p5J00aO800aO800#g7000000000000000"
    "Km<SpKm<SpKm@=9zy|;T00000000000000000000Kmb4lzyyE<fC2ym00RI300000000000000000000fB=vM&;?Kha0g%mU;+RD"
    "00000000000000000000Km>pUfCB&nfCGRAzytsQ00000000000000000000Kmb4lfCPXBfCB&n00RI600saA000000000000000"
    "fCqp90096400IC6fDZrw00000000000000000000004ji009620096200#g80096200F=O00000000000000400aO800aO800aO8"
    "00aO800aO800aO400000000070096200962zySaO009620096700000000005CiZB00000000000000000000000000000000000"
)

_raw_font_cache = None


_RAW_TRANSLATION = str.maketrans({
    "\u2014": "-", "\u2013": "-", "\u2018": "'", "\u2019": "'",
    "\u201c": '"', "\u201d": '"', "\u2022": "*", "\u2026": "...",
    "\u00a0": " ", "\u221e": "8", "\u00d7": "x", "\u20ac": "EUR",
})


def _raw_ascii(text):
    return text.translate(_RAW_TRANSLATION)


def _raw_glyphs():
    """Decode the embedded 12x16 proportional glyph strip."""
    global _raw_font_cache
    if _raw_font_cache is not None:
        return _raw_font_cache
    data = base64.b85decode(_BITMAP_FONT.encode())
    glyphs = {}
    pos = 0
    for code in range(32, 127):
        rows = []
        for _ in range(16):
            lo = data[pos]
            hi = data[pos + 1]
            pos += 2
            rows.append((hi << 8) | lo)
        # used width from the set pixels
        used = 0
        for row in rows:
            for x in range(12):
                if row & (1 << (11 - x)):
                    used = max(used, x + 1)
        glyphs[chr(code)] = (rows, used)
    _raw_font_cache = glyphs
    return glyphs


# --------------------------------------------------------------------------
# Canvas: one small drawing API over Pillow or the raw raster path
# --------------------------------------------------------------------------

class Canvas:
    def __init__(self, width, height, background):
        self.w = width
        self.h = height
        self.background = background
        self.pillow = PIL is not None
        if self.pillow:
            Image, ImageDraw, _ = PIL
            self.img = Image.new("RGB", (width, height), background)
            self.draw = ImageDraw.Draw(self.img)
        else:
            self.buf = bytearray(bytes(background) * (width * height))

    # ---- basic raster helpers -------------------------------------------
    def _span(self, y, x0, x1, color):
        if y < 0 or y >= self.h:
            return
        x0 = max(0, int(x0))
        x1 = min(self.w, int(x1))
        if x1 <= x0:
            return
        off = (y * self.w + x0) * 3
        self.buf[off:off + (x1 - x0) * 3] = bytes(color) * (x1 - x0)

    def rect(self, box, color):
        x0, y0, x1, y1 = [int(v) for v in box]
        if self.pillow:
            self.draw.rectangle([x0, y0, x1 - 1, y1 - 1], fill=color)
        else:
            for y in range(max(0, y0), min(self.h, y1)):
                self._span(y, x0, x1, color)

    def rrect(self, box, radius, color, outline=None, width=3):
        x0, y0, x1, y1 = [int(v) for v in box]
        r = int(radius)
        if self.pillow:
            self.draw.rounded_rectangle(
                [x0, y0, x1 - 1, y1 - 1], radius=r,
                fill=color, outline=outline, width=width,
            )
            return
        self.rect([x0 + r, y0, x1 - r, y1], color)
        self.rect([x0, y0 + r, x0 + r, y1 - r], color)
        self.rect([x1 - r, y0 + r, x1, y1 - r], color)
        for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r),
                       (x0 + r, y1 - r), (x1 - r, y1 - r)):
            self.ellipse([cx - r, cy - r, cx + r, cy + r], color)
        if outline is not None and width > 0:
            # a light outline is enough for the fallback
            self.rect([x0 + r, y0, x1 - r, y0 + width], outline)
            self.rect([x0 + r, y1 - width, x1 - r, y1], outline)
            self.rect([x0, y0 + r, x0 + width, y1 - r], outline)
            self.rect([x1 - width, y0 + r, x1, y1 - r], outline)

    def poly(self, points, color):
        pts = [(int(x), int(y)) for x, y in points]
        if self.pillow:
            self.draw.polygon(pts, fill=color)
            return
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            for i in range(len(pts)):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % len(pts)]
                if y0 == y1:
                    continue
                if min(y0, y1) <= y < max(y0, y1):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self._span(y, math.floor(xs[i]), math.ceil(xs[i + 1]) + 1, color)

    def ellipse(self, box, color, outline=None, width=3):
        x0, y0, x1, y1 = [int(v) for v in box]
        if x1 <= x0 or y1 <= y0:
            return
        if self.pillow:
            self.draw.ellipse([x0, y0, x1 - 1, y1 - 1], fill=color,
                              outline=outline, width=width)
            return
        if color is not None:
            cx = (x0 + x1) / 2.0
            cy = (y0 + y1) / 2.0
            rx = (x1 - x0) / 2.0
            ry = (y1 - y0) / 2.0
            for y in range(y0, y1):
                dy = (y - cy) / ry if ry else 0
                if abs(dy) > 1:
                    continue
                dx = rx * math.sqrt(max(0.0, 1 - dy * dy))
                self._span(y, cx - dx, cx + dx, color)
        if outline is not None:
            self.arc([x0, y0, x1, y1], 0, 360, outline, width)

    def line(self, points, color, width=3):
        pts = [(int(x), int(y)) for x, y in points]
        if self.pillow:
            self.draw.line(pts, fill=color, width=int(width), joint="curve")
            return
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]
            x1, y1 = pts[i + 1]
            steps = max(abs(x1 - x0), abs(y1 - y0), 1)
            half = max(0, int(width) // 2)
            for s in range(steps + 1):
                t = s / steps
                x = int(round(x0 + (x1 - x0) * t))
                y = int(round(y0 + (y1 - y0) * t))
                self.rect([x - half, y - half, x + half + 1, y + half + 1], color)

    def arc(self, box, start, end, color, width=3):
        if self.pillow:
            self.draw.arc([int(v) for v in box], start, end,
                          fill=color, width=int(width))
            return
        x0, y0, x1, y1 = box
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        rx, ry = (x1 - x0) / 2.0, (y1 - y0) / 2.0
        pts = []
        steps = max(12, int((end - start) / 4))
        for i in range(steps + 1):
            a = math.radians(start + (end - start) * i / steps)
            pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
        self.line(pts, color, width)

    def dashed(self, points, color, width=3, dash=18, gap=12):
        """Dashed polyline built from straight segments."""
        for i in range(len(points) - 1):
            x0, y0 = points[i]
            x1, y1 = points[i + 1]
            seg = math.hypot(x1 - x0, y1 - y0)
            if seg == 0:
                continue
            ux, uy = (x1 - x0) / seg, (y1 - y0) / seg
            pos = 0.0
            while pos < seg:
                a = pos
                b = min(seg, pos + dash)
                self.line([(x0 + ux * a, y0 + uy * a),
                           (x0 + ux * b, y0 + uy * b)], color, width)
                pos += dash + gap

    # ---- text ------------------------------------------------------------
    def _pil_font(self, size, kind):
        key = (int(size), kind)
        if key in _pil_font_cache:
            return _pil_font_cache[key]
        Image, ImageDraw, ImageFont = PIL
        path = _font_file(kind)
        font = None
        if path:
            try:
                font = ImageFont.truetype(path, int(size))
            except Exception:
                font = None
        if font is None:
            try:
                font = ImageFont.load_default(size=int(size))
            except Exception:
                font = ImageFont.load_default()
        _pil_font_cache[key] = font
        return font

    def text_width(self, text, size, kind="sans"):
        if self.pillow:
            font = self._pil_font(size, kind)
            try:
                return font.getlength(text)
            except AttributeError:
                return font.getsize(text)[0]
        glyphs = _raw_glyphs()
        scale = size / 16.0
        total = 0.0
        for ch in _raw_ascii(text):
            rows, used = glyphs.get(ch, glyphs["?"])
            total += (used + 1 if used else 4) * scale
        return total

    def text(self, x, y, text, size, kind, color):
        if self.pillow:
            font = self._pil_font(size, kind)
            try:
                self.draw.text((int(x), int(y)), text, font=font,
                               fill=color, anchor="lt")
            except (TypeError, ValueError):
                self.draw.text((int(x), int(y)), text, font=font, fill=color)
            return
        glyphs = _raw_glyphs()
        scale = size / 16.0
        pen = float(x)
        bold = "bold" in kind
        for ch in _raw_ascii(text):
            rows, used = glyphs.get(ch, glyphs["?"])
            adv = used + 1 if used else 4
            if used:
                for gy, bits in enumerate(rows):
                    for gx in range(used):
                        if bits & (1 << (11 - gx)):
                            px = pen + gx * scale
                            py = y + gy * scale
                            self.rect([px, py, px + scale + 0.6, py + scale + 0.6], color)
                            if bold:
                                self.rect([px + scale * 0.6, py, px + scale * 1.6,
                                           py + scale + 0.6], color)
            pen += adv * scale

    # ---- output ----------------------------------------------------------
    def finish(self, out_path, final=1024):
        if self.pillow:
            Image, _, _ = PIL
            try:
                resample = Image.Resampling.LANCZOS
            except AttributeError:
                resample = Image.LANCZOS
            small = self.img.resize((final, final), resample)
            small.save(out_path, format="PNG", optimize=True)
        else:
            small = _downscale_2x(self.buf, self.w, self.h)
            _write_png(out_path, final, final, small)


def _downscale_2x(buf, width, height):
    """Average each 2x2 block (2048 -> 1024)."""
    nw, nh = width // 2, height // 2
    out = bytearray(nw * nh * 3)
    for y in range(nh):
        r0 = y * 2 * width * 3
        r1 = r0 + width * 3
        orow = y * nw * 3
        for x in range(nw):
            a = r0 + x * 6
            b = r1 + x * 6
            o = orow + x * 3
            out[o] = (buf[a] + buf[a + 3] + buf[b] + buf[b + 3] + 2) >> 2
            out[o + 1] = (buf[a + 1] + buf[a + 4] + buf[b + 1] + buf[b + 4] + 2) >> 2
            out[o + 2] = (buf[a + 2] + buf[a + 5] + buf[b + 2] + buf[b + 5] + 2) >> 2
    return out


def _write_png(path, width, height, rgb):
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data +
                struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw.extend(rgb[y * stride:(y + 1) * stride])
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)


# --------------------------------------------------------------------------
# Typography helpers
# --------------------------------------------------------------------------

def wrap_text(c, text, size, kind, max_w):
    words = text.split()
    lines, current = [], []
    for word in words:
        trial = " ".join(current + [word])
        if c.text_width(trial, size, kind) <= max_w or not current:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def fit_size(c, text, size, kind, max_w, minimum=14, step=2):
    while size > minimum and c.text_width(text, size, kind) > max_w:
        size -= step
    return size


def paragraph(c, x, y, text, size, kind, color, max_w, max_lines=None,
              minimum=13, leading=1.18):
    """Draw wrapped text, shrinking gently if it would exceed max_lines."""
    chosen = size
    lines = wrap_text(c, text, chosen, kind, max_w)
    while max_lines and len(lines) > max_lines and chosen > minimum:
        chosen -= 1
        lines = wrap_text(c, text, chosen, kind, max_w)
    for line in lines:
        c.text(x, y, line, chosen, kind, color)
        y += chosen * leading
    return y


def right_text(c, right, y, text, size, kind, color):
    c.text(right - c.text_width(text, size, kind), y, text, size, kind, color)


def center_text(c, cx, y, text, size, kind, color):
    c.text(cx - c.text_width(text, size, kind) / 2, y, text, size, kind, color)


def spaced(c, x, y, text, size, kind, color, tracking=0.12):
    """Letter-spaced small caps, drawn one glyph at a time."""
    pen = x
    for ch in text:
        c.text(pen, y, ch, size, kind, color)
        pen += c.text_width(ch, size, kind) + size * tracking
    return pen


# --------------------------------------------------------------------------
# Small pictorial elements
# --------------------------------------------------------------------------

def draw_iran_flag(c, x, y, w, h):
    third = h / 3
    c.rect([x, y, x + w, y + third], GREEN)
    c.rect([x, y + third, x + w, y + 2 * third], WHITE)
    c.rect([x, y + 2 * third, x + w, y + h], RED)
    # stylised central emblem
    cx, cy = x + w / 2, y + h / 2
    c.ellipse([cx - h * 0.10, cy - h * 0.12, cx + h * 0.10, cy + h * 0.12], RED)
    c.line([(cx, cy - h * 0.22), (cx, cy + h * 0.22)], RED, max(2, int(h * 0.045)))
    c.line([(cx - h * 0.16, cy + h * 0.12), (cx, cy - h * 0.06),
            (cx + h * 0.16, cy + h * 0.12)], RED, max(2, int(h * 0.04)))


def draw_us_flag(c, x, y, w, h):
    stripe = h / 13.0
    c.rect([x, y, x + w, y + h], WHITE)
    for i in range(0, 13, 2):
        c.rect([x, y + i * stripe, x + w, y + (i + 1) * stripe], RED)
    cw, ch = w * 0.44, stripe * 7
    c.rect([x, y, x + cw, y + ch], NAVY)
    for row in range(4):
        for col in range(5):
            px = x + cw * (0.11 + col * 0.19)
            py = y + ch * (0.16 + row * 0.22)
            r = max(1, h * 0.018)
            c.ellipse([px - r, py - r, px + r, py + r], WHITE)


def draw_flagpole(c, x, y, h):
    c.line([(x, y), (x, y + h)], (57, 47, 35), max(2, int(h * 0.028)))
    c.ellipse([x - h * 0.035, y - h * 0.035, x + h * 0.035, y + h * 0.035],
              AMBER)


def draw_tanker(c, cx, waterline, scale=1.0, number="1"):
    """A laden crude tanker in side view, with fire and smoke."""
    L = 168 * scale
    Hh = 30 * scale
    left, right = cx - L / 2, cx + L / 2

    # wake / reflection
    c.ellipse([left - 10 * scale, waterline + 4 * scale,
               right + 10 * scale, waterline + 20 * scale], SEA_DEEP)
    c.line([(left - 24 * scale, waterline + 12 * scale),
            (right + 26 * scale, waterline + 12 * scale)], SEA_LINE, max(1, int(2 * scale)))

    # hull, bow pointing right
    hull = [
        (left, waterline - Hh * 0.55),
        (right - 18 * scale, waterline - Hh * 0.55),
        (right, waterline),
        (right - 18 * scale, waterline + Hh * 0.55),
        (left, waterline + Hh * 0.55),
    ]
    c.poly(hull, (14, 20, 28))
    c.rect([left + 2 * scale, waterline + Hh * 0.24,
            right - 20 * scale, waterline + Hh * 0.42], (150, 38, 32))
    # deck piping
    c.rect([left + 10 * scale, waterline - Hh * 0.62,
            right - 30 * scale, waterline - Hh * 0.50], (203, 121, 48))
    # superstructure and funnel at the stern
    c.rect([left + L * 0.14, waterline - Hh * 1.55,
            left + L * 0.34, waterline - Hh * 0.5], (240, 236, 224))
    c.rect([left + L * 0.19, waterline - Hh * 1.48,
            left + L * 0.29, waterline - Hh * 1.02], (68, 79, 90))
    c.rect([left + L * 0.19, waterline - Hh * 1.20,
            left + L * 0.29, waterline - Hh * 1.10], ORANGE)
    # mast
    c.line([(left + L * 0.24, waterline - Hh * 1.55),
            (left + L * 0.24, waterline - Hh * 2.05)], (220, 216, 204),
           max(1, int(2 * scale)))
    # bow mast
    c.line([(right - L * 0.10, waterline - Hh * 0.55),
            (right - L * 0.10, waterline - Hh * 1.10)], (220, 216, 204),
           max(1, int(2 * scale)))

    # fire glow and flames amidships
    fx = left + L * 0.56
    c.ellipse([fx - L * 0.22, waterline - Hh * 3.4,
               fx + L * 0.22, waterline - Hh * 0.4], (96, 45, 20))
    flames = [
        [(fx - 30 * scale, waterline - Hh * 0.55),
         (fx - 14 * scale, waterline - Hh * 2.9),
         (fx - 2 * scale, waterline - Hh * 1.6),
         (fx + 10 * scale, waterline - Hh * 3.5),
         (fx + 20 * scale, waterline - Hh * 1.7),
         (fx + 36 * scale, waterline - Hh * 2.5),
         (fx + 30 * scale, waterline - Hh * 0.55)],
        [(fx - 18 * scale, waterline - Hh * 0.55),
         (fx - 4 * scale, waterline - Hh * 2.1),
         (fx + 6 * scale, waterline - Hh * 1.1),
         (fx + 14 * scale, waterline - Hh * 2.4),
         (fx + 24 * scale, waterline - Hh * 0.55)],
    ]
    c.poly(flames[0], ORANGE)
    c.poly(flames[1], AMBER)
    # white-hot core
    c.poly([(fx - 5 * scale, waterline - Hh * 0.6),
            (fx + 1 * scale, waterline - Hh * 1.7),
            (fx + 8 * scale, waterline - Hh * 0.6)], (255, 232, 170))

    # smoke
    for i, (dx, dy, r) in enumerate(((0.10, 3.9, 0.24), (0.22, 4.5, 0.29),
                                     (0.06, 5.1, 0.33), (0.26, 5.7, 0.27))):
        c.ellipse([fx + L * (dx - r), waterline - Hh * dy - L * r * 0.45,
                   fx + L * (dx + r), waterline - Hh * dy + L * r * 0.45],
                  (74 + i * 6, 89 + i * 6, 102 + i * 6))

    # number badge
    bx, by = left + L * 0.05, waterline - Hh * 2.35
    c.ellipse([bx - 17 * scale, by - 17 * scale, bx + 17 * scale, by + 17 * scale],
              ORANGE)
    c.text(bx - c.text_width(number, 24 * scale, "sansbold") / 2,
           by - 15 * scale, number, 24 * scale, "sansbold", WHITE)


def draw_warship(c, cx, waterline, scale=1.0):
    L = 104 * scale
    left, right = cx - L / 2, cx + L / 2
    c.ellipse([left, waterline + 2 * scale, right, waterline + 12 * scale], SEA_DEEP)
    c.poly([(left, waterline - 8 * scale), (right - 12 * scale, waterline - 8 * scale),
            (right, waterline), (right - 12 * scale, waterline + 8 * scale),
            (left, waterline + 8 * scale)], STEEL)
    c.poly([(left + L * 0.34, waterline - 8 * scale),
            (left + L * 0.60, waterline - 8 * scale),
            (left + L * 0.56, waterline - 30 * scale),
            (left + L * 0.38, waterline - 30 * scale)], (218, 222, 224))
    c.line([(left + L * 0.47, waterline - 30 * scale),
            (left + L * 0.47, waterline - 48 * scale)], (218, 222, 224),
           max(1, int(2 * scale)))
    c.ellipse([left + L * 0.43, waterline - 54 * scale,
               left + L * 0.51, waterline - 46 * scale], AMBER)


def draw_mine(c, x, y, r):
    c.ellipse([x - r, y - r, x + r, y + r], (23, 29, 36))
    for a in range(0, 360, 45):
        dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
        c.line([(x + dx * r * 0.7, y + dy * r * 0.7),
                (x + dx * r * 1.7, y + dy * r * 1.7)], (23, 29, 36),
               max(2, int(r * 0.34)))


def draw_plane_icon(c, x, y, s, color=NAVY):
    """Small top-down jet plus approach arcs."""
    for r in (0.55, 0.9, 1.25):
        c.arc([x - s * r, y - s * r, x + s * r, y + s * r], 205, 335, color, 3)
    c.poly([(x, y - s * 0.62), (x + s * 0.10, y - s * 0.10),
            (x + s * 0.55, y + s * 0.20), (x + s * 0.55, y + s * 0.30),
            (x + s * 0.10, y + s * 0.16), (x + s * 0.08, y + s * 0.52),
            (x + s * 0.22, y + s * 0.62), (x + s * 0.22, y + s * 0.68),
            (x, y + s * 0.60), (x - s * 0.22, y + s * 0.68),
            (x - s * 0.22, y + s * 0.62), (x - s * 0.08, y + s * 0.52),
            (x - s * 0.10, y + s * 0.16), (x - s * 0.55, y + s * 0.30),
            (x - s * 0.55, y + s * 0.20), (x - s * 0.10, y - s * 0.10)],
           color)


def draw_un_icon(c, x, y, s):
    c.ellipse([x - s * 0.7, y - s * 0.7, x + s * 0.7, y + s * 0.7],
              None, outline=NAVY, width=4)
    c.ellipse([x - s * 0.52, y - s * 0.52, x + s * 0.52, y + s * 0.52],
              None, outline=NAVY, width=2)
    for a in (-60, -20, 20, 60):
        c.line([(x - s * 0.5, y + s * 0.12), (x + s * 0.5, y + s * 0.12)],
               NAVY, 2)
        c.line([(x, y - s * 0.7), (x, y + s * 0.7)], NAVY, 2)
    # laurel suggestion and a ship below
    c.arc([x - s * 0.9, y - s * 0.9, x + s * 0.9, y + s * 0.9], 110, 250, GREEN, 4)
    c.arc([x - s * 0.9, y - s * 0.9, x + s * 0.9, y + s * 0.9], 290, 70, GREEN, 4)
    c.poly([(x - s * 0.5, y + s * 0.55), (x + s * 0.5, y + s * 0.55),
            (x + s * 0.34, y + s * 0.78), (x - s * 0.34, y + s * 0.78)], NAVY)
    c.rect([x - s * 0.12, y + s * 0.28, x + s * 0.12, y + s * 0.55], NAVY)


def draw_chip_icon(c, x, y, s):
    c.rrect([x - s * 0.55, y - s * 0.55, x + s * 0.55, y + s * 0.55],
            s * 0.10, NAVY)
    c.rrect([x - s * 0.34, y - s * 0.34, x + s * 0.34, y + s * 0.34],
            s * 0.05, (27, 47, 68))
    c.rect([x - s * 0.18, y - s * 0.18, x + s * 0.18, y - s * 0.10], AMBER)
    c.rect([x - s * 0.18, y - s * 0.02, x + s * 0.08, y + s * 0.07], ORANGE)
    c.rect([x - s * 0.18, y + s * 0.14, x + s * 0.18, y + s * 0.20], STEEL)
    for i in range(4):
        off = (-0.33 + i * 0.22) * s
        c.line([(x - s * 0.75, y + off), (x - s * 0.55, y + off)], AMBER, 4)
        c.line([(x + s * 0.55, y + off), (x + s * 0.75, y + off)], AMBER, 4)
        c.line([(x + off, y - s * 0.75), (x + off, y - s * 0.55)], AMBER, 4)
        c.line([(x + off, y + s * 0.55), (x + off, y + s * 0.75)], AMBER, 4)
    c.arc([x + s * 0.48, y - s * 0.95, x + s * 1.05, y - s * 0.38],
          300, 180, ORANGE, 4)
    c.poly([(x + s * 0.50, y - s * 0.92), (x + s * 0.50, y - s * 0.62),
            (x + s * 0.78, y - s * 0.78)], ORANGE)


# --------------------------------------------------------------------------
# Page sections
# --------------------------------------------------------------------------

def draw_masthead(c):
    c.rect([M, 42, RIGHT, 49], INK)
    c.text(M, 62, "VOL. XII  •  NO. 328", 23, "sansbold", GREY)
    right_text(c, RIGHT, 62, "FINAL EDITION  •  $4.00", 23, "sansbold", GREY)

    mast = "THE WORLD TODAY"
    size = fit_size(c, mast, 138, "masthead", COL)
    center_text(c, W / 2, 96, mast, size, "masthead", INK)

    # thin flourish under the masthead
    c.rect([W / 2 - 210, 238, W / 2 + 210, 243], ORANGE)

    c.text(M, 258, "Tuesday, 24 November 2026", 40, "serifbold", INK)
    right_text(c, RIGHT, 266, "WORLD NEWS  •  THE GULF CRISIS  •  32 PAGES",
               24, "sansbold", GREY)

    c.rect([M, 310, RIGHT, 316], INK)
    c.rect([M, 322, RIGHT, 325], INK)

    # navy kicker band
    c.rect([M, 338, RIGHT, 392], NAVY)
    c.rect([M, 338, M + 14, 392], ORANGE)
    center_text(c, W / 2 + 6, 350,
                "THREE TANKERS ABLAZE  •  A US BLOCKADE IN FORCE  •  OIL AT THE CENTRE",
                27, "sansbold", WHITE)


def draw_lead(c):
    lx, lw = M, 1226
    kill_y = 414
    c.rect([lx, kill_y + 5, lx + 18, kill_y + 23], ORANGE)
    spaced(c, lx + 32, kill_y, "LEAD STORY  /  MIDDLE EAST  /  THE STRAIT", 25,
           "sansbold", ORANGE, 0.10)

    # Display headline, two very large lines
    h1, h2 = "HORMUZ", "ON FIRE"
    s1 = fit_size(c, h1, 226, "display", lw, 120)
    s2 = fit_size(c, h2, 226, "display", lw, 120)
    c.text(lx, kill_y + 34, h1, s1, "display", INK)
    c.text(lx, kill_y + 228, h2, s2, "display", INK)

    # tally stamp to the right of the second line
    sx = lx + 1032
    c.rect([sx, kill_y + 234, sx + 184, kill_y + 398], NAVY)
    c.rect([sx, kill_y + 234, sx + 184, kill_y + 240], ORANGE)
    center_text(c, sx + 92, kill_y + 244, "3", 82, "display", AMBER)
    center_text(c, sx + 92, kill_y + 332, "TANKERS", 19, "sansbold", WHITE)
    center_text(c, sx + 92, kill_y + 356, "ABLAZE", 19, "sansbold", AMBER)

    # orange underline block under ON FIRE
    c.rect([lx, kill_y + 416, lx + 300, kill_y + 426], ORANGE)

    deck = ("Iran says three oil tankers caught fire after hitting mines in the "
            "Strait of Hormuz. A US naval blockade is in force; President Trump "
            "has threatened to sink Iranian vessels.")
    paragraph(c, lx, kill_y + 444, deck, 35, "serif", (42, 52, 64), lw - 12,
              max_lines=3, minimum=27, leading=1.20)

    # scene
    scene = [lx, 992, lx + lw, 1438]
    draw_scene(c, scene)

    # caption
    c.rect([lx, 1452, lx + lw, 1520], NAVY)
    c.rect([lx, 1452, lx + 8, 1520], ORANGE)
    paragraph(c, lx + 22, 1463,
              "THE STRAIT: Iran's coast (top) faces Oman's Musandam peninsula across "
              "21 miles of water. Three tankers are ablaze after hitting mines; the US line seals the Gulf.",
              22, "sans", WHITE, lw - 44, max_lines=2, minimum=18, leading=1.18)


def draw_scene(c, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    c.rect(box, SEA)

    # water texture
    for i in range(9):
        yy = y0 + h * (0.34 + i * 0.072)
        c.line([(x0, yy), (x0 + w * 0.16, yy - h * 0.008),
                (x0 + w * 0.31, yy + h * 0.006)], SEA_LINE, 2)
        c.line([(x0 + w * 0.72, yy - h * 0.01), (x0 + w * 0.86, yy + h * 0.006),
                (x1, yy - h * 0.004)], SEA_LINE, 2)

    # Iran, along the top
    iran = [
        (x0, y0), (x1, y0), (x1, y0 + h * 0.17),
        (x0 + w * 0.82, y0 + h * 0.19), (x0 + w * 0.74, y0 + h * 0.27),
        (x0 + w * 0.63, y0 + h * 0.23), (x0 + w * 0.53, y0 + h * 0.29),
        (x0 + w * 0.43, y0 + h * 0.22), (x0 + w * 0.33, y0 + h * 0.25),
        (x0 + w * 0.24, y0 + h * 0.19), (x0 + w * 0.13, y0 + h * 0.26),
        (x0 + w * 0.05, y0 + h * 0.22), (x0, y0 + h * 0.25),
    ]
    c.poly(iran, SAND)
    coast = iran[3:]
    c.line(coast, SAND_DARK, 5)

    # UAE / Arabia, bottom left
    uae = [
        (x0, y1), (x0 + w * 0.46, y1), (x0 + w * 0.43, y0 + h * 0.87),
        (x0 + w * 0.37, y0 + h * 0.82), (x0 + w * 0.31, y0 + h * 0.85),
        (x0 + w * 0.25, y0 + h * 0.79), (x0 + w * 0.19, y0 + h * 0.83),
        (x0 + w * 0.13, y0 + h * 0.86), (x0 + w * 0.07, y0 + h * 0.92),
        (x0, y1),
    ]
    c.poly(uae, SAND)
    c.line(uae[2:8], SAND_DARK, 5)

    # Musandam peninsula, bottom right
    oman = [
        (x0 + w * 0.735, y1), (x1, y1), (x1, y0 + h * 0.48),
        (x0 + w * 0.93, y0 + h * 0.46), (x0 + w * 0.88, y0 + h * 0.51),
        (x0 + w * 0.85, y0 + h * 0.60), (x0 + w * 0.81, y0 + h * 0.69),
        (x0 + w * 0.78, y0 + h * 0.80), (x0 + w * 0.75, y0 + h * 0.91),
    ]
    c.poly(oman, SAND)
    c.line(oman[2:], SAND_DARK, 5)

    # map labels
    c.text(x0 + w * 0.145, y0 + h * 0.048, "IRAN", 34, "sansbold", INK)
    c.text(x0 + w * 0.200, y1 - h * 0.075, "UAE", 28, "sansbold", INK)
    c.text(x0 + w * 0.80, y1 - h * 0.095, "OMAN", 31, "sansbold", INK)

    # the strait
    c.text(x0 + w * 0.395, y0 + h * 0.345, "STRAIT OF HORMUZ", 32, "sansbold",
           WHITE)

    # blockade arc across the narrows (quadratic curve sampled into a polyline)
    def qpoint(t):
        p0 = (x0 + w * 0.760, y0 + h * 0.235)
        p1 = (x0 + w * 0.690, y0 + h * 0.430)
        p2 = (x0 + w * 0.855, y0 + h * 0.585)
        return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
                (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])

    bpts = [qpoint(i / 24) for i in range(25)]
    c.dashed(bpts, ORANGE, 8, 22, 14)
    c.dashed([(x, y + 6) for x, y in bpts], (255, 205, 140), 2, 22, 14)

    # blockade label in the water, tied to the arc with a leader line
    bx, by = x0 + w * 0.505, y0 + h * 0.415
    bw, bh = 222, 46
    c.rect([bx, by, bx + bw, by + bh], NAVY)
    c.rect([bx, by, bx + bw, by + 5], ORANGE)
    center_text(c, bx + bw / 2, by + 12, "US BLOCKADE", 22, "sansbold", WHITE)
    c.line([(bx + bw, by + bh / 2), (x0 + w * 0.735, y0 + h * 0.405)],
           (255, 205, 140), 2)

    # two flags on the opposing shores
    draw_flagpole(c, x0 + 34, y0 + 32, 70)
    draw_iran_flag(c, x0 + 42, y0 + 40, 100, 60)

    draw_flagpole(c, x0 + 52, y1 - 140, 122)
    draw_us_flag(c, x0 + 60, y1 - 132, 104, 62)
    c.text(x0 + 66, y1 - 26, "USA", 24, "sansbold", NAVY)

    # mines in the channel, to the right of the blockade tag
    for mx, my in ((0.700, 0.545), (0.725, 0.600), (0.755, 0.650),
                   (0.785, 0.585)):
        draw_mine(c, x0 + w * mx, y0 + h * my, 10)

    # three burning tankers
    draw_tanker(c, x0 + w * 0.400, y0 + h * 0.700, 0.95, "1")
    draw_tanker(c, x0 + w * 0.580, y0 + h * 0.830, 1.00, "2")
    draw_tanker(c, x0 + w * 0.220, y0 + h * 0.660, 0.90, "3")

    # blockade warships on the arc
    draw_warship(c, x0 + w * 0.742, y0 + h * 0.320, 0.66)
    draw_warship(c, x0 + w * 0.752, y0 + h * 0.445, 0.70)
    draw_warship(c, x0 + w * 0.802, y0 + h * 0.505, 0.72)

    # timestamp tag
    tx, ty = x1 - 270, y0 + 20
    c.rect([tx, ty, x1 - 14, ty + 44], (8, 24, 40))
    c.text(tx + 12, ty + 11, "24 NOV 2026  •  18:00 GMT", 20, "sansbold", AMBER)

    # thin frame
    c.rect([x0, y0, x1, y0 + 4], NAVY)
    c.rect([x0, y1 - 4, x1, y1], NAVY)
    c.rect([x0, y0, x0 + 4, y1], NAVY)
    c.rect([x1 - 4, y0, x1, y1], NAVY)


def draw_crisis_rail(c):
    """Right-hand rail: five points, the quote, markets."""
    x0, x1 = 1328, RIGHT
    y = 414
    w = x1 - x0

    # -- five points box ---------------------------------------------------
    box_h = 650
    c.rrect([x0, y, x1, y + box_h], 4, PANEL, RULE, 3)
    c.rect([x0, y, x1, y + 58], NAVY)
    c.rect([x0, y, x0 + 10, y + 58], ORANGE)
    c.text(x0 + 24, y + 16, "THE CRISIS IN FIVE POINTS", 24, "sansbold", WHITE)
    c.text(x1 - 74, y + 18, "01—05", 19, "sansbold", AMBER)

    points = [
        ("1", "TANKERS ABLAZE",
         "Iran says the ships hit Hormuz mines and caught fire."),
        ("2", "US BLOCKADE",
         "American warships enforce a naval blockade in the Gulf."),
        ("3", "TRUMP'S THREAT",
         "The president vows to sink Iranian vessels and mocks Iran as "
         "\u201cprofessional tap dancers.\u201d"),
        ("4", "IRAN'S VOW",
         "Tehran vowed to use \u201call means,\u201d without saying what that entails."),
        ("5", "QATAR TALKS",
         "VP Vance and Secretary Rubio meet the Qatari prime minister."),
    ]
    iy = y + 78
    for num, head, body in points:
        c.ellipse([x0 + 20, iy + 4, x0 + 62, iy + 46], ORANGE)
        c.text(x0 + 41 - c.text_width(num, 23, "sansbold") / 2, iy + 10,
               num, 23, "sansbold", WHITE)
        c.text(x0 + 80, iy, head, 26, "sansbold", INK)
        paragraph(c, x0 + 80, iy + 34, body, 23, "serif", (55, 64, 76),
                  w - 104, max_lines=2, minimum=19, leading=1.16)
        iy += 112

    # -- quote box ---------------------------------------------------------
    y = 1082
    qh = 204
    c.rect([x0, y, x1, y + qh], NAVY)
    c.rect([x0, y, x0 + 12, y + qh], ORANGE)
    c.text(x0 + 24, y - 2, "\u201c", 96, "display", AMBER)
    paragraph(c, x0 + 74, y + 20,
              "Professional tap dancers.",
              36, "italic", WHITE, w - 100, max_lines=1, minimum=26,
              leading=1.18)
    paragraph(c, x0 + 74, y + 76,
              "Trump's mocking description of Iran \u2014 delivered with a threat "
              "to sink its vessels.",
              23, "serif", (216, 224, 232), w - 100, max_lines=2,
              minimum=19, leading=1.16)
    c.text(x0 + 74, y + 158,
           "\u2014 DONALD TRUMP, US PRESIDENT", 19, "sansbold", AMBER)

    # -- markets box -------------------------------------------------------
    y = 1304
    mh = 204
    c.rrect([x0, y, x1, y + mh], 4, (238, 228, 204), RULE, 3)
    c.text(x0 + 22, y + 18, "MARKETS WATCH OIL", 25, "sansbold", INK)
    c.text(x1 - 92, y + 19, "RISK", 20, "sansbold", ORANGE)
    paragraph(c, x0 + 22, y + 58,
              "About a fifth of the world's crude moves through Hormuz. "
              "Traders are pricing the danger.",
              23, "serif", (55, 64, 76), w - 150, max_lines=3,
              minimum=19, leading=1.16)
    base = y + mh - 26
    for i, bh in enumerate((18, 32, 44, 62, 86)):
        bx = x1 - 116 + i * 19
        c.rect([bx, base - bh, bx + 12, base], ORANGE if i != 4 else NAVY)
    c.line([(x1 - 122, base + 2), (x1 - 12, base + 2)], INK, 2)


def draw_secondary(c):
    y0, y1 = 1530, 1824
    gap = 26
    pw = (COL - 2 * gap) // 3
    xs = [M, M + pw + gap, M + 2 * (pw + gap)]

    panels = [
        dict(
            tag="ASIA  •  AIRSPACE", colour=TEAL,
            head="SEOUL TELLS ISLANDS TO TAKE SHELTER",
            body="Russian military aircraft approached; residents were ordered "
                 "to cover. The fourth known incursion this year \u2014 and the "
                 "second in a week.",
            icon="plane",
        ),
        dict(
            tag="EUROPE  •  UNITED NATIONS", colour=NAVY,
            head="RUSSIA AND UKRAINE CLASH AT UN",
            body="Moscow and Kyiv traded accusations at the Security Council "
                 "over Black Sea shipping and energy strikes.",
            icon="un",
        ),
        dict(
            tag="AMERICAS  •  BUSINESS", colour=ORANGE,
            head="JENSEN HUANG BACK AS NVIDIA CEO",
            body="The chipmaker's board reinstated its founder as chief "
                 "executive, returning him to the top of the AI boom.",
            icon="chip",
        ),
    ]

    for i, p in enumerate(panels):
        x0 = xs[i]
        x1 = x0 + pw
        c.rrect([x0, y0, x1, y1], 4, PANEL, RULE, 3)
        c.rect([x0, y0, x1, y0 + 8], p["colour"])

        c.text(x0 + 22, y0 + 26, p["tag"], 20, "sansbold", p["colour"])
        c.rect([x0 + 22, y0 + 54, x1 - 22, y0 + 57], RULE)

        # headline, with room for the icon at lower right
        hs = 33
        lines = wrap_text(c, p["head"], hs, "display", pw - 160)
        while len(lines) > 3 and hs > 26:
            hs -= 1
            lines = wrap_text(c, p["head"], hs, "display", pw - 160)
        hy = y0 + 70
        for line in lines:
            c.text(x0 + 22, hy, line, hs, "display", INK)
            hy += hs * 1.03

        # icon sits to the right of the headline block
        ix = x1 - 76
        iy = y0 + 112
        if p["icon"] == "plane":
            draw_plane_icon(c, ix, iy, 38)
        elif p["icon"] == "un":
            draw_un_icon(c, ix, iy, 52)
        else:
            draw_chip_icon(c, ix, iy + 4, 46)

        body_y = max(hy + 10, y0 + 168)
        paragraph(c, x0 + 22, body_y, p["body"], 24, "serif", (52, 61, 72),
                  pw - 44, max_lines=3, minimum=19, leading=1.17)


def draw_world_strip(c):
    y0, y1 = 1848, 1932
    c.rect([M, y0, RIGHT, y1], (26, 38, 52))
    c.rect([M, y0, M + 10, y1], ORANGE)

    c.text(M + 24, y0 + 14, "WORLD WATCH", 23, "sansbold", AMBER)
    c.text(M + 24, y0 + 46, "THE DAY IN FOUR LINES", 17, "sansbold",
           (186, 196, 206))

    items = [
        ("GULF", "US tanker struck; oil markets tense"),
        ("KOREA", "Shelter alert as Russian jets near"),
        ("UN", "Black Sea shipping row at UN"),
        ("TECH", "Nvidia brings Jensen Huang back"),
    ]
    ix = M + 330
    iw = (RIGHT - ix - 10) // 4
    for i, (tag, text) in enumerate(items):
        xx = ix + i * iw
        c.text(xx, y0 + 16, tag, 19, "sansbold", ORANGE)
        c.text(xx, y0 + 44, text, 22, "sans", WHITE)
        if i:
            c.line([(xx - 18, y0 + 16), (xx - 18, y1 - 14)], (70, 84, 98), 2)


def draw_footer(c):
    y = 1956
    c.rect([M, y, RIGHT, y + 5], ORANGE)
    c.text(M, y + 20,
           "SOURCES: Reuters, AP, BBC, Al Jazeera, UN News and market reports.",
           21, "sans", GREY)
    right_text(c, RIGHT, y + 20, "PAGE 1 OF 32", 21, "sansbold", INK)
    c.text(M, y + 50,
           "Tuesday, 24 November 2026 \u2014 final edition, 23:00 GMT. "
           "All reports datelined on the day.",
           22, "italic", (70, 78, 88))
    right_text(c, RIGHT - 2, y + 50, "THE WORLD TODAY", 20, "masthead", NAVY)


def draw_background(c):
    c.rect([0, 0, W, H], PAPER)
    # faint vertical column rules for broadsheet texture
    c.rect([0, 0, W, 12], NAVY)


def render_page(c):
    draw_background(c)
    draw_masthead(c)
    draw_lead(c)
    draw_crisis_rail(c)
    draw_secondary(c)
    draw_world_strip(c)
    draw_footer(c)


# --------------------------------------------------------------------------
# Public entry points
# --------------------------------------------------------------------------

def render(out_path):
    c = Canvas(W, H, PAPER)
    render_page(c)
    c.finish(out_path, 1024)
    return out_path


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "entry.png")
    render(out)
    print(f"wrote {out} ({os.path.getsize(out)} bytes, Pillow={PIL is not None})")


if __name__ == "__main__":
    main()
