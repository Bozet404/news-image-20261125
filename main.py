#!/usr/bin/env python3
"""THE DAY IN ONE IMAGE -- Wednesday 25 November 2026.

A program that draws one newspaper-style front page summing up the
world's news of 25 November 2026 and writes it to /output/entry.png.

Pure Python 3 standard library: no network, no clock, no randomness,
no external files. The same input always produces the same bytes.

Stories pictured (all first reported on 25 November 2026):
  * Ukraine's drone strikes on Russian ships in the Gulf of Finland
    and off Libya; Moscow calls them "terrorism".
  * The COP31 climate summit collapses in Antalya with no deal.
  * Three oil tankers hit by naval mines in the Strait of Hormuz.
  * NATO to send early-warning aircraft to Poland.
  * BJP and Shiromani Akali Dal reunite for Punjab's 2027 election.
  * Also: 266 million face acute food insecurity (WFP);
    Gaza's death toll reaches 74,746.
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)   # newsprint
INK = (22, 22, 22)        # headline ink
NAVY = (22, 50, 79)       # masthead band
NAVY_DARK = (14, 36, 58)
RED = (178, 38, 30)       # accent rule / alerts
BLUE = (31, 95, 168)
SKY = (168, 205, 232)
SKY_PALE = (214, 232, 244)
SEA = (24, 84, 138)
SEA_DARK = (16, 62, 104)
SAND = (226, 205, 160)
GREEN = (46, 125, 50)
GREEN_DARK = (27, 94, 32)
GREY = (120, 120, 118)
GREY_DARK = (74, 74, 72)
WHITE = (255, 255, 255)
YELLOW = (244, 196, 48)
ORANGE = (232, 116, 24)
BROWN = (122, 82, 42)
TEAL = (0, 121, 107)

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph is 7 rows of 5 cells; "#" is ink, "." is empty.
# Uppercase letters, digits and common punctuation, drawn from scratch.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
}

# ------------------------------------------------------------- RGB canvas
class Canvas:
    """A plain RGB pixel buffer with tiny drawing helpers."""

    def __init__(self, width, height, colour):
        self.width = width
        self.height = height
        self.pixels = bytearray(colour * (width * height))

    def set_px(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i:i + 3] = bytes(colour)

    def fill_rect(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.width + x0) * 3
            self.pixels[i:i + len(row)] = row

    def hline(self, x, y, w, colour):
        self.fill_rect(x, y, w, 1, colour)

    def vline(self, x, y, h, colour):
        self.fill_rect(x, y, 1, h, colour)

    def line(self, x0, y0, x1, y1, colour):
        """Bresenham line, inclusive of both ends."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set_px(x0, y0, colour)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def thick_line(self, x0, y0, x1, y1, colour, thick=2):
        for ox in range(thick):
            for oy in range(thick):
                self.line(x0 + ox, y0 + oy, x1 + ox, y1 + oy, colour)

    def disc(self, cx, cy, r, colour):
        """Filled circle."""
        for dy in range(-r, r + 1):
            half = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - half, cy + dy, half * 2 + 1, 1, colour)

    def ring(self, cx, cy, r, colour):
        """Circle outline, one pixel thick."""
        steps = max(8, int(6.28 * r))
        for k in range(steps):
            a = 6.283185307179586 * k / steps
            self.set_px(int(cx + r * _cos(a)), int(cy + r * _sin(a)), colour)

    def fill_polygon(self, points, colour):
        """Scanline fill for a simple polygon."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[k]), y, int(xs[k + 1]) - int(xs[k]) + 1, 1, colour)


def _sin(a):
    # Tiny sine via the standard library-free Taylor series is overkill;
    # use a short lookup-free approximation through repeated halving.
    # (Kept deterministic; only used for ring points.)
    x = a
    while x > 3.141592653589793:
        x -= 6.283185307179586
    while x < -3.141592653589793:
        x += 6.283185307179586
    term = x
    total = x
    x2 = x * x
    for n in range(1, 8):
        term *= -x2 / ((2 * n) * (2 * n + 1))
        total += term
    return total


def _cos(a):
    return _sin(a + 1.5707963267948966)


# ------------------------------------------------------------------- text
def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(canvas, x, y, text, scale, colour):
    """Draw uppercase text; unknown glyphs become a blank."""
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    canvas.fill_rect(cx + col * scale, y + row * scale,
                                     scale, scale, colour)
        cx += 6 * scale
    return cx


def draw_text_centred(canvas, cx, y, text, scale, colour):
    draw_text(canvas, cx - text_width(text, scale) // 2, y, text, scale, colour)


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    for raw in text.split("\n"):
        words = raw.split(" ")
        line = ""
        for word in words:
            trial = word if not line else line + " " + word
            if text_width(trial, scale) <= max_width or not line:
                line = trial
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines


def draw_paragraph(canvas, x, y, text, max_width, scale, colour, leading=None):
    """Draw a wrapped paragraph; returns the y just below the last line."""
    if leading is None:
        leading = 7 * scale + 4
    for line in wrap_text(text, max_width, scale):
        draw_text(canvas, x, y, line, scale, colour)
        y += leading
    return y


# ------------------------------------------------------------ PNG encoding
def png_bytes(canvas):
    """Encode the canvas as a plain RGB PNG (filter 0 on every row)."""
    raw = bytearray()
    stride = canvas.width * 3
    for y in range(canvas.height):
        raw.append(0)
        start = y * stride
        raw += canvas.pixels[start:start + stride]

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height,
                       8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


# ------------------------------------------------------------ panel frame
def panel(canvas, x, y, w, h):
    canvas.fill_rect(x, y, w, h, WHITE)
    canvas.fill_rect(x, y, w, 2, INK)
    canvas.fill_rect(x, y + h - 2, w, 2, INK)
    canvas.fill_rect(x, y, 2, h, INK)
    canvas.fill_rect(x + w - 2, y, 2, h, INK)


def kicker(canvas, x, y, text, colour=RED):
    """Small red section label above a picture."""
    draw_text(canvas, x, y, text, 2, colour)
    return y + 7 * 2 + 6


# ------------------------------------------------------- scene: two seas
def scene_sea(canvas, x, y, w, h):
    """Two ships on open water, drones overhead, one blast of smoke."""
    horizon = y + int(h * 0.52)
    canvas.fill_rect(x, y, w, horizon - y, SKY)
    canvas.fill_rect(x, horizon, w, y + h - horizon, SEA)
    # sun and light cloud
    canvas.disc(x + w - 52, y + 34, 22, YELLOW)
    canvas.disc(x + w - 58, y + 30, 18, (250, 214, 90))
    canvas.fill_rect(x + 18, y + 26, 120, 10, WHITE)
    canvas.fill_rect(x + 44, y + 38, 90, 10, WHITE)
    # waves
    for wy in range(horizon + 14, y + h - 6, 16):
        for wx in range(x + 8, x + w - 30, 46):
            canvas.hline(wx, wy, 26, (120, 180, 215))
    # big cargo ship, left
    ship_y = horizon + 26
    canvas.fill_polygon([(x + 30, ship_y), (x + 250, ship_y),
                         (x + 232, ship_y + 34), (x + 48, ship_y + 34)],
                        (32, 32, 34))
    canvas.fill_rect(x + 52, ship_y - 26, 120, 26, (70, 70, 74))
    canvas.fill_rect(x + 62, ship_y - 20, 18, 12, SKY_PALE)
    canvas.fill_rect(x + 92, ship_y - 20, 18, 12, SKY_PALE)
    canvas.fill_rect(x + 122, ship_y - 20, 18, 12, SKY_PALE)
    canvas.fill_rect(x + 178, ship_y - 40, 26, 40, RED)
    canvas.fill_rect(x + 178, ship_y - 46, 26, 6, INK)
    # smaller naval vessel, right, with a hit: smoke and fire
    ship2_y = horizon + 44
    canvas.fill_polygon([(x + w - 250, ship2_y), (x + w - 60, ship2_y),
                         (x + w - 78, ship2_y + 26), (x + w - 232, ship2_y + 26)],
                        GREY_DARK)
    canvas.fill_rect(x + w - 210, ship2_y - 18, 90, 18, (52, 52, 56))
    canvas.fill_rect(x + w - 150, ship2_y - 32, 14, 32, GREY)
    # blast starburst above the second ship
    bx, by = x + w - 150, ship2_y - 52
    for dx, dy in ((-26, -14), (-8, -26), (12, -24), (28, -10),
                   (30, 8), (10, 20), (-12, 18), (-28, 6)):
        canvas.thick_line(bx, by, bx + dx, by + dy, ORANGE, 3)
    canvas.disc(bx, by, 10, YELLOW)
    canvas.disc(bx - 34, by - 34, 12, GREY)
    canvas.disc(bx - 16, by - 46, 15, (150, 150, 148))
    canvas.disc(bx + 6, by - 52, 11, GREY)
    # three drones in the sky with dotted paths
    for dx, dy in ((70, 66), (150, 44), (230, 76)):
        px, py = x + dx, y + dy
        canvas.fill_rect(px - 2, py - 2, 16, 5, INK)
        canvas.fill_rect(px + 4, py - 6, 4, 13, INK)
        canvas.hline(px - 8, py - 8, 28, INK)
        canvas.hline(px - 8, py + 8, 28, INK)
        canvas.set_px(px - 16, py + 12, GREY)
        canvas.set_px(px - 24, py + 16, GREY)


# ----------------------------------------------------- scene: climate
def scene_climate(canvas, x, y, w, h):
    """A warming globe over factory smoke, sun in the corner."""
    canvas.fill_rect(x, y, w, h, SKY_PALE)
    # sun with rays
    sx, sy = x + w - 40, y + 30
    for dx, dy in ((-22, 0), (22, 0), (0, -22), (0, 22),
                   (-15, -15), (15, -15), (-15, 15), (15, 15)):
        canvas.thick_line(sx, sy, sx + dx, sy + dy, YELLOW, 3)
    canvas.disc(sx, sy, 15, YELLOW)
    # globe
    gx, gy, gr = x + w // 2 - 8, y + 66, 50
    canvas.disc(gx, gy, gr + 3, WHITE)
    canvas.disc(gx, gy, gr, BLUE)
    # land blobs
    canvas.disc(gx - 20, gy - 18, 14, GREEN)
    canvas.disc(gx + 6, gy - 24, 10, GREEN)
    canvas.disc(gx + 20, gy + 6, 12, GREEN)
    canvas.disc(gx - 4, gy + 24, 11, GREEN_DARK)
    canvas.disc(gx - 30, gy + 12, 7, GREEN)
    # cloud strokes
    canvas.fill_rect(gx - 36, gy - 4, 30, 4, WHITE)
    canvas.fill_rect(gx + 4, gy + 10, 28, 4, WHITE)
    canvas.fill_rect(gx - 12, gy - 32, 24, 4, WHITE)
    # factory stacks at the foot of the globe
    base = y + h - 14
    canvas.fill_rect(x + 18, base - 34, 16, 34, GREY_DARK)
    canvas.fill_rect(x + 40, base - 26, 16, 26, GREY_DARK)
    canvas.fill_rect(x + 62, base - 20, 24, 20, GREY_DARK)
    canvas.disc(x + 26, base - 42, 7, GREY)
    canvas.disc(x + 36, base - 52, 8, (150, 150, 148))
    # thermometer rising beside the globe
    tx = x + w - 26
    canvas.fill_rect(tx, y + 84, 8, 44, WHITE)
    canvas.fill_rect(tx - 1, y + 84, 10, 44, INK)
    canvas.disc(tx + 4, y + 130, 8, RED)
    canvas.fill_rect(tx + 1, y + 104, 6, 24, RED)


# ------------------------------------------------------ scene: Hormuz
def scene_hormuz(canvas, x, y, w, h):
    """A tanker threading a narrow strait; a spiked mine in the water."""
    canvas.fill_rect(x, y, w, h, SAND)
    # the strait: a diagonal band of water
    canvas.fill_polygon([(x + 40, y + h), (x + w - 40, y),
                         (x + w, y), (x + w, y + h),
                         (x + 150, y + h)], SEA)
    canvas.fill_polygon([(x, y), (x + 150, y),
                         (x + 40, y + h), (x, y + h)], SAND)
    # shoreline strokes
    canvas.thick_line(x + 40, y + h, x + w - 40, y, (210, 186, 138), 3)
    canvas.thick_line(x + 150, y + h, x + w, y, (210, 186, 138), 3)
    # tanker crossing the strait
    ty = y + h // 2 - 6
    canvas.fill_polygon([(x + 62, ty), (x + 218, ty),
                         (x + 204, ty + 24), (x + 76, ty + 24)], (32, 32, 34))
    canvas.fill_rect(x + 84, ty - 20, 60, 20, WHITE)
    canvas.fill_rect(x + 92, ty - 14, 12, 8, SKY)
    canvas.fill_rect(x + 112, ty - 14, 12, 8, SKY)
    canvas.fill_rect(x + 152, ty - 30, 16, 30, RED)
    canvas.fill_rect(x + 152, ty - 34, 16, 4, INK)
    # spiked mine in the water ahead of the tanker
    mx, my = x + 238, y + h // 2 + 34
    for dx, dy in ((-14, 0), (14, 0), (0, -14), (0, 14),
                   (-10, -10), (10, -10), (-10, 10), (10, 10)):
        canvas.thick_line(mx, my, mx + dx, my + dy, INK, 3)
    canvas.disc(mx, my, 11, INK)
    canvas.disc(mx - 3, my - 3, 4, GREY)
    # warning triangle
    wx, wy = x + 18, y + 14
    canvas.fill_polygon([(wx, wy + 34), (wx + 17, wy), (wx + 34, wy + 34)],
                        YELLOW)
    canvas.fill_polygon([(wx + 4, wy + 30), (wx + 17, wy + 7),
                         (wx + 30, wy + 30)], (232, 190, 20))
    draw_text(canvas, wx + 13, wy + 16, "!", 2, INK)


# -------------------------------------------------------- scene: NATO
def scene_nato(canvas, x, y, w, h):
    """An early-warning plane with its radar dome over a radar sweep."""
    canvas.fill_rect(x, y, w, h, SKY)
    # clouds
    canvas.disc(x + 36, y + 22, 11, WHITE)
    canvas.disc(x + 54, y + 18, 13, WHITE)
    canvas.disc(x + 230, y + 30, 10, WHITE)
    canvas.disc(x + 246, y + 26, 12, WHITE)
    # ground strip
    gy = y + h - 26
    canvas.fill_rect(x, gy, w, 26, GREEN)
    canvas.fill_rect(x + 16, gy - 10, 13, 10, GREY_DARK)
    canvas.fill_rect(x + 40, gy - 14, 10, 14, GREY_DARK)
    canvas.fill_rect(x + 240, gy - 8, 16, 8, GREY_DARK)
    # radar sweep arcs
    cx, cy = x + w - 48, gy
    for r in (20, 34, 48):
        canvas.ring(cx, cy, r, WHITE)
    canvas.line(cx, cy, cx - 34, cy - 34, WHITE)
    # AWACS plane
    px, py = x + 24, y + 36
    canvas.fill_polygon([(px, py + 6), (px + 120, py + 6),
                         (px + 156, py + 12), (px + 120, py + 18),
                         (px, py + 18)], WHITE)
    canvas.disc(px + 5, py + 12, 6, WHITE)
    canvas.fill_rect(px + 16, py + 9, 88, 3, SKY)
    canvas.fill_polygon([(px + 96, py + 6), (px + 120, py - 16),
                         (px + 130, py - 16), (px + 120, py + 6)], WHITE)
    canvas.fill_polygon([(px + 32, py + 18), (px + 56, py + 40),
                         (px + 74, py + 40), (px + 62, py + 18)], WHITE)
    canvas.fill_polygon([(px + 96, py + 18), (px + 120, py + 36),
                         (px + 134, py + 36), (px + 124, py + 18)], WHITE)
    # radar dome on a strut
    canvas.fill_rect(px + 62, py - 10, 5, 16, GREY_DARK)
    canvas.disc(px + 64, py - 13, 15, GREY)
    canvas.disc(px + 64, py - 13, 10, (200, 200, 198))


# ------------------------------------------------------ scene: ballot
def scene_ballot(canvas, x, y, w, h):
    """A ballot box with a marked paper and a rising sun."""
    canvas.fill_rect(x, y, w, h, (250, 236, 205))
    # rising sun
    sx, sy = x + w - 44, y + 26
    for dx, dy in ((-18, 0), (18, 0), (0, -18), (-13, -13), (13, -13)):
        canvas.thick_line(sx, sy, sx + dx, sy + dy, ORANGE, 3)
    canvas.disc(sx, sy, 13, YELLOW)
    # ballot box
    bx, by = x + 48, y + 58
    canvas.fill_rect(bx, by, 130, 50, BROWN)
    canvas.fill_rect(bx - 8, by - 10, 146, 10, (94, 62, 30))
    canvas.fill_rect(bx + 34, by - 8, 62, 3, INK)
    # paper sticking out of the slot, marked with a tick
    canvas.fill_rect(bx + 46, by - 44, 38, 36, WHITE)
    canvas.thick_line(bx + 51, by - 22, bx + 61, by - 13, GREEN_DARK, 3)
    canvas.thick_line(bx + 61, by - 13, bx + 79, by - 38, GREEN_DARK, 3)
    # small stars and the year
    for sx2, sy2 in ((x + 24, y + 22), (x + 20, y + 96), (x + 250, y + 64)):
        canvas.fill_rect(sx2, sy2, 3, 3, RED)
        canvas.fill_rect(sx2 - 4, sy2 + 1, 11, 1, RED)
        canvas.fill_rect(sx2 + 1, sy2 - 4, 1, 11, RED)
    draw_text(canvas, x + 196, y + h - 26, "2027", 3, NAVY)


# ------------------------------------------------------------- the page
def build_page():
    canvas = Canvas(WIDTH, HEIGHT, PAPER)
    # outer frame
    canvas.fill_rect(0, 0, WIDTH, 3, INK)
    canvas.fill_rect(0, HEIGHT - 3, WIDTH, 3, INK)
    canvas.fill_rect(0, 0, 3, HEIGHT, INK)
    canvas.fill_rect(WIDTH - 3, 0, 3, HEIGHT, INK)

    # ---- masthead ------------------------------------------------
    canvas.fill_rect(16, 16, 992, 128, NAVY)
    canvas.fill_rect(16, 140, 992, 4, RED)
    draw_text_centred(canvas, 512, 32, "THE DAY IN ONE IMAGE", 6, WHITE)
    canvas.hline(212, 92, 600, (120, 160, 195))
    draw_text_centred(canvas, 512, 104, "WEDNESDAY 25 NOVEMBER 2026", 2,
                      (214, 232, 244))
    draw_text_centred(canvas, 512, 124, "THE WORLD'S NEWS IN A SINGLE PICTURE",
                      2, (168, 205, 232))

    # ---- lead row ------------------------------------------------
    lead_x, lead_y, lead_w, lead_h = 16, 160, 600, 396
    side_x, side_w = 632, 376
    panel(canvas, lead_x, lead_y, lead_w, lead_h)
    panel(canvas, side_x, lead_y, side_w, lead_h)

    # lead story: drones hit Russian ships in two seas
    lx, ly = lead_x + 16, lead_y + 14
    kicker(canvas, lx, ly, "UKRAINE - RUSSIA")
    scene_sea(canvas, lx, ly + 22, lead_w - 32, 208)
    hy = ly + 22 + 208 + 12
    hy = draw_paragraph(canvas, lx, hy,
                        "KYIV CONFIRMS DRONE STRIKES ON RUSSIAN SHIPS",
                        lead_w - 32, 3, INK)
    draw_paragraph(canvas, lx, hy + 6,
                   "ZELENSKIY CONFIRMS KYIV STRUCK A CARGO SHIP IN THE "
                   "GULF OF FINLAND. MOSCOW CALLS THE STRIKES 'TERRORISM' "
                   "AND WARNS OF CONSEQUENCES.",
                   lead_w - 32, 2, (40, 40, 40))

    # side story: COP31 collapses
    sx, sy = side_x + 16, lead_y + 14
    kicker(canvas, sx, sy, "CLIMATE - ANTALYA")
    scene_climate(canvas, sx, sy + 22, side_w - 32, 148)
    hy = sy + 22 + 148 + 12
    hy = draw_paragraph(canvas, sx, hy,
                        "CLIMATE TALKS COLLAPSE IN ANTALYA",
                        side_w - 32, 3, INK)
    draw_paragraph(canvas, sx, hy + 6,
                   "NO DEAL AS OIL AND GAS PRODUCERS BLOCK A FOSSIL-FUEL "
                   "PHASEOUT.",
                   side_w - 32, 2, (40, 40, 40))

    # ---- middle row: three stories -------------------------------
    mid_y, mid_h = 572, 304
    panels = [
        (16, "ENERGY - HORMUZ", scene_hormuz,
         "MINES HIT THREE TANKERS IN HORMUZ",
         "IRAN SAYS THREE TANKERS WERE HIT BY NAVAL MINES IN THE STRAIT."),
        (356, "SECURITY - POLAND", scene_nato,
         "NATO SENDS EARLY-WARNING JETS TO POLAND",
         "AFTER MISSILES LANDED IN POLAND DURING AN ATTACK ON UKRAINE."),
        (696, "INDIA - PUNJAB", scene_ballot,
         "BJP AND AKALI DAL REUNITE FOR PUNJAB",
         "ALLIANCE FOR THE 2027 ELECTION, AFTER A SIX-YEAR SPLIT."),
    ]
    for px, kick, scene, headline, caption in panels:
        panel(canvas, px, mid_y, 312, mid_h)
        ix, iy = px + 14, mid_y + 12
        kicker(canvas, ix, iy, kick)
        scene(canvas, ix, iy + 20, 312 - 28, 118)
        hy = iy + 20 + 118 + 10
        hy = draw_paragraph(canvas, ix, hy, headline, 312 - 28, 3, INK)
        draw_paragraph(canvas, ix, hy + 6, caption, 312 - 28, 2,
                       (40, 40, 40))

    # ---- bottom strip --------------------------------------------
    canvas.fill_rect(16, 892, 992, 116, NAVY_DARK)
    canvas.fill_rect(16, 892, 992, 3, RED)
    draw_text(canvas, 36, 912, "ALSO TODAY:", 2, YELLOW)
    draw_paragraph(canvas, 36, 936,
                   "266 MILLION PEOPLE FACE ACUTE FOOD INSECURITY, SAYS "
                   "THE WFP. GAZA'S DEATH TOLL REACHES 74,746.",
                   992 - 40, 2, WHITE)
    return canvas


# ------------------------------------------------------------------ main
def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(png_bytes(build_page()))


if __name__ == "__main__":
    main()
