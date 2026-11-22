#!/usr/bin/env python3
"""The World Today - Sunday, 22 November 2026.

Draws a newspaper front page summing up the day's world news in one
1024x1024 PNG image. Pure Python 3.13 standard library: a hand-written
5x7 bitmap font, a hand-written PNG encoder, and simple geometric
illustrations drawn pixel by pixel. No network, no files read, no
randomness: every run writes identical bytes.

Usage:
    MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# Newsprint palette.
PAPER = (247, 241, 222)
INK = (25, 23, 19)
RED = (166, 30, 34)
BLUE = (39, 76, 119)
GREY = (107, 101, 90)
TINT = (238, 230, 208)

# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 rows of 5 pixels, '#' on, '.' off.
# Written from scratch for this entry; capitals, digits and punctuation.
# ---------------------------------------------------------------------------
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "01110", "00000", "01110", "00000", "00000"),
    '•': ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
    '—': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
}


def text_width(text, scale):
    """Pixel width of text at the given scale (1px gap between glyphs)."""
    return len(text) * 6 * scale - scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.split(' ')
    lines = []
    current = ''
    for word in words:
        trial = word if not current else current + ' ' + word
        if text_width(trial, scale) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------------------
# Canvas: a flat RGB buffer with small drawing helpers.
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = color

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill_rect(x, y, thick, h, color)

    def rect(self, x, y, w, h, color, thick=1):
        self.hline(x, y, w, color, thick)
        self.hline(x, y + h - thick, w, color, thick)
        self.vline(x, y, h, color, thick)
        self.vline(x + w - thick, y, h, color, thick)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color):
        x = 0
        y = r
        d = 3 - 2 * r
        while x <= y:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                           (cx + x, cy - y), (cx - x, cy - y),
                           (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                self.set(px, py, color)
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1

    def fill_circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            half = int((r * r - (yy - cy) * (yy - cy)) ** 0.5)
            self.hline(cx - half, yy, 2 * half + 1, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        # Filled triangle via scanlines.
        ys = sorted(((x0, y0), (x1, y1), (x2, y2)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = ys
        def edge(xa, ya, xb, yb, y):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) / (yb - ya)
        for y in range(ay, cy + 1):
            if y < by:
                xa = edge(ax, ay, bx, by, y)
                xb = edge(ax, ay, cx, cy, y)
            else:
                xa = edge(bx, by, cx, cy, y)
                xb = edge(ax, ay, cx, cy, y)
            x_start, x_end = int(min(xa, xb)), int(max(xa, xb))
            self.hline(x_start, y, x_end - x_start + 1, color)

    def text(self, x, y, s, scale, color, bold=False):
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        px = x + col * scale
                        py = y + row * scale
                        self.fill_rect(px, py, scale, scale, color)
                        if bold:
                            self.fill_rect(px + scale, py, scale, scale, color)
            x += 6 * scale

    def text_centered(self, y, s, scale, color, bold=False):
        x = (self.w - text_width(s, scale)) // 2
        self.text(x, y, s, scale, color, bold)


# ---------------------------------------------------------------------------
# Illustrations: small geometric scenes, one per story.
# ---------------------------------------------------------------------------
def draw_gaza_lead(c, x, y, w, h):
    """Flooded tent camp: tent, rain, standing water."""
    c.fill_rect(x, y, w, h, TINT)
    # Rain slashes.
    for i in range(14):
        rx = x + 12 + i * 20
        ry = y + 8 + (i % 3) * 12
        c.line(rx, ry, rx - 6, ry + 12, BLUE)
    # Tent.
    tx, ty = x + 30, y + h - 78
    c.triangle(tx, ty, tx + 90, ty, tx + 45, ty - 62, RED)
    c.triangle(tx + 32, ty, tx + 58, ty, tx + 45, ty - 30, INK)
    c.hline(tx - 6, ty, 102, INK, 3)
    # Second tent, smaller, behind.
    tx2, ty2 = x + w - 110, y + h - 58
    c.triangle(tx2, ty2, tx2 + 70, ty2, tx2 + 35, ty2 - 44, BLUE)
    c.hline(tx2 - 4, ty2, 78, INK, 3)
    # Flood water: wavy lines.
    wy = y + h - 26
    for i in range(5):
        xx = x + 10 + i * 52
        c.line(xx, wy, xx + 18, wy - 5, BLUE)
        c.line(xx + 18, wy - 5, xx + 36, wy, BLUE)
    c.hline(x + 8, wy + 8, w - 16, BLUE, 2)


def draw_gulf(c, x, y, w, h):
    """Missile intercepted in the sky over the desert."""
    c.fill_rect(x, y, w, h, TINT)
    # Ground and dunes.
    gy = y + h - 22
    c.hline(x, gy, w, INK, 3)
    c.line(x + 10, gy, x + 90, gy - 14, INK)
    c.line(x + 90, gy - 14, x + 170, gy, INK)
    c.line(x + 260, gy, x + 330, gy - 12, INK)
    c.line(x + 330, gy - 12, x + 420, gy, INK)
    # Missile climbing, trail behind (drawn large so it reads).
    mx, my = x + w // 2 + 60, y + 18
    c.line(mx, my, mx - 44, my + 44, GREY)
    c.line(mx - 6, my + 6, mx - 50, my + 50, GREY)
    c.line(mx, my, mx + 12, my + 22, INK)
    c.line(mx + 12, my + 22, mx - 4, my + 34, INK)
    c.line(mx - 4, my + 34, mx - 12, my + 12, INK)
    c.triangle(mx - 4, my + 34, mx - 12, my + 12, mx + 2, my + 40, RED)
    # Burst where the interceptor hit.
    bx, by = x + w // 2 - 70, y + 34
    for dx, dy in ((0, -22), (16, -16), (22, 0), (16, 16), (0, 22),
                   (-16, 16), (-22, 0), (-16, -16)):
        c.line(bx, by, bx + dx, by + dy, RED)
    c.fill_circle(bx, by, 7, RED)
    # Shield arc above the ground.
    c.line(x + 30, gy - 40, x + 120, gy - 58, BLUE)
    c.line(x + 120, gy - 58, x + 210, gy - 58, BLUE)
    c.line(x + 210, gy - 58, x + 300, gy - 40, BLUE)


def draw_cop(c, x, y, w, h):
    """Globe with a rising sun and a thermometer."""
    c.fill_rect(x, y, w, h, TINT)
    cx, cy, r = x + w // 2 - 40, y + h // 2 + 6, 34
    c.fill_circle(cx, cy, r, BLUE)
    # Land blobs.
    c.fill_circle(cx - 12, cy - 8, 9, (90, 140, 90))
    c.fill_circle(cx + 12, cy + 10, 8, (90, 140, 90))
    c.circle(cx, cy, r, INK)
    c.line(cx - r, cy, cx + r, cy, INK)
    c.line(cx, cy - r, cx, cy + r, INK)
    # Sun rays top right.
    sx, sy = x + w - 70, y + 18
    c.fill_circle(sx, sy, 10, RED)
    for dx, dy in ((0, -18), (13, -13), (18, 0), (13, 13), (0, 18),
                   (-13, 13), (-18, 0), (-13, -13)):
        c.line(sx, sy, sx + dx, sy + dy, RED)
    # Thermometer bottom right.
    tx, ty = x + w - 46, y + h - 52
    c.fill_rect(tx, ty, 8, 34, INK)
    c.fill_circle(tx + 4, ty + 38, 9, RED)
    c.fill_rect(tx + 2, ty + 18, 4, 18, RED)


def draw_israel(c, x, y, w, h):
    """Parliament building with columns and two speech bubbles.

    The scene must stay inside its strip (h px tall): the base sits 8 px
    above the strip bottom, columns are 30 px tall, the pediment 12 px.
    """
    c.fill_rect(x, y, w, h, TINT)
    bx, by = x + 60, y + h - 8
    # Steps.
    c.hline(bx - 14, by, 150, INK, 3)
    c.hline(bx - 8, by - 7, 138, INK, 3)
    # Columns, 30 px tall.
    for i in range(4):
        cx = bx + 8 + i * 34
        c.fill_rect(cx, by - 37, 10, 30, INK)
    # Pediment and roof.
    c.triangle(bx - 6, by - 37, bx + 128, by - 37, bx + 61, by - 51, INK)
    c.hline(bx - 6, by - 37, 134, INK, 3)
    # Speech bubbles with tails.
    c.circle(x + w - 70, y + 20, 14, RED)
    c.line(x + w - 78, y + 32, x + w - 88, y + 44, RED)
    c.circle(x + w - 108, y + 30, 11, BLUE)
    c.line(x + w - 114, y + 40, x + w - 122, y + 50, BLUE)
    c.fill_circle(x + w - 70, y + 20, 3, PAPER)
    c.fill_circle(x + w - 108, y + 30, 2, PAPER)


def draw_myanmar(c, x, y, w, h):
    """Seismograph zigzag over cracked ground."""
    c.fill_rect(x, y, w, h, TINT)
    # Seismograph trace.
    pts = [(x + 8, y + 30), (x + 60, y + 30), (x + 80, y + 14),
           (x + 100, y + 52), (x + 120, y + 18), (x + 140, y + 48),
           (x + 160, y + 26), (x + 180, y + 34), (x + 230, y + 34),
           (x + 250, y + 12), (x + 270, y + 56), (x + 290, y + 30),
           (x + 340, y + 30), (x + 360, y + 20), (x + 380, y + 40),
           (x + w - 10, y + 30)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        c.line(x0, y0, x1, y1, RED)
    # Cracked ground.
    gy = y + h - 24
    c.hline(x, gy, w, INK, 3)
    c.line(x + 120, gy, x + 140, gy + 14, INK)
    c.line(x + 140, gy + 14, x + 128, gy + 22, INK)
    c.line(x + 300, gy, x + 316, gy + 12, INK)
    c.line(x + 316, gy + 12, x + 306, gy + 22, INK)
    # Small leaning house, kept inside the strip.
    hx, hy = x + 200, gy - 28
    c.line(hx, hy, hx + 44, hy - 6, INK)
    c.line(hx + 44, hy - 6, hx + 44, hy + 28, INK)
    c.line(hx, hy, hx, hy + 28, INK)
    c.line(hx, hy, hx + 22, hy - 16, INK)
    c.line(hx + 22, hy - 16, hx + 44, hy - 6, INK)


def draw_atp(c, x, y, w, h):
    """Tennis court, net and ball."""
    c.fill_rect(x, y, w, h, TINT)
    # Court lines.
    cy = y + h - 26
    c.hline(x + 10, cy, w - 20, INK, 3)
    c.hline(x + 10, cy - 44, w - 20, INK, 2)
    c.vline(x + 40, cy - 44, 44, INK, 2)
    c.vline(x + w - 40, cy - 44, 44, INK, 2)
    # Net.
    nx = x + w // 2
    c.vline(nx, cy - 70, 44, INK, 3)
    c.hline(nx - 60, cy - 70, 120, INK, 3)
    for i in range(7):
        c.vline(nx - 54 + i * 18, cy - 70, 44, GREY, 1)
    # Ball with seam.
    bx, by = x + 56, y + 26
    c.fill_circle(bx, by, 18, (200, 220, 60))
    c.circle(bx, by, 18, INK)
    c.line(bx - 14, by - 10, bx - 2, by, INK)
    c.line(bx - 2, by, bx - 14, by + 10, INK)
    c.line(bx + 14, by - 10, bx + 2, by, INK)
    c.line(bx + 2, by, bx + 14, by + 10, INK)
    # Trophy.
    tx, ty = x + w - 66, y + 16
    c.fill_rect(tx, ty, 26, 22, (212, 175, 55))
    c.line(tx - 8, ty + 4, tx, ty + 4, INK)
    c.line(tx + 26, ty + 4, tx + 34, ty + 4, INK)
    c.line(tx + 4, ty + 22, tx + 22, ty + 22, INK)
    c.fill_rect(tx + 8, ty + 22, 10, 8, (212, 175, 55))
    c.fill_rect(tx + 2, ty + 30, 22, 5, (212, 175, 55))


def draw_hongkong(c, x, y, w, h):
    """Ballot box, ballot slip and a check mark."""
    c.fill_rect(x, y, w, h, TINT)
    # Ballot box.
    bx, by = x + w // 2 - 55, y + h - 62
    c.fill_rect(bx, by, 110, 44, BLUE)
    c.rect(bx, by, 110, 44, INK, 2)
    c.hline(bx + 30, by + 2, 50, INK, 4)
    c.text(bx + 38, by + 18, 'VOTE', 2, PAPER)
    # Ballot slip going in.
    c.fill_rect(bx + 34, by - 34, 42, 32, PAPER)
    c.rect(bx + 34, by - 34, 42, 32, INK, 2)
    c.hline(bx + 40, by - 24, 30, INK, 2)
    c.hline(bx + 40, by - 16, 30, INK, 2)
    # Check mark.
    c.line(x + 26, y + 30, x + 40, y + 46, RED)
    c.line(x + 40, y + 46, x + 66, y + 12, RED)
    c.line(x + 27, y + 31, x + 41, y + 47, RED)
    c.line(x + 41, y + 47, x + 67, y + 13, RED)
    # Small flags / slips right.
    c.fill_rect(x + w - 52, y + 18, 30, 20, PAPER)
    c.rect(x + w - 52, y + 18, 30, 20, INK, 2)
    c.hline(x + w - 46, y + 26, 18, RED, 2)
    c.hline(x + w - 46, y + 32, 18, INK, 2)


# ---------------------------------------------------------------------------
# The front page.
# ---------------------------------------------------------------------------
LEAD = {
    'kicker': 'GAZA - THE LEAD STORY',
    'headline': 'FOUR NATIONS TELL ISRAEL: OPEN GAZA TO AID',
    'deck': ('Australia, Canada, Italy and Britain jointly demand immediate, '
             'unhindered humanitarian access, as floods swamp shelters and '
             '150,000 tents wait at the border.'),
}

PANELS = [
    {
        'kicker': 'THE GULF',
        'headline': "SAUDI DEFENCES DOWN HOUTHI MISSILE NEAR MECCA",
        'deck': ('The Saudi-led coalition says it destroyed a ballistic '
                 'missile aimed at western Saudi Arabia in the early hours '
                 'of Sunday, after civil defence warned the Mecca region.'),
        'art': draw_gulf,
    },
    {
        'kicker': 'CLIMATE - COP31',
        'headline': 'COP31 TALKS RESUME IN ANTALYA, STILL DEADLOCKED',
        'deck': ('Negotiators return on Sunday after talks ran into overtime '
                 'with no deal. Fossil-fuel wording and adaptation finance '
                 'still divide nearly 200 nations.'),
        'art': draw_cop,
    },
    {
        'kicker': 'ISRAEL',
        'headline': "EISENKOT OPENS UNITY TALKS WITH NETANYAHU'S LIKUD",
        'deck': ("The prime minister-designate invites Likud to negotiate a "
                 'broad coalition, after last month\'s election left no bloc '
                 'with a majority. Talks open today.'),
        'art': draw_israel,
    },
    {
        'kicker': 'MYANMAR',
        'headline': 'EARTHQUAKE OF 4.1 SHAKES MYANMAR BEFORE DAWN',
        'deck': ('A magnitude 4.1 quake struck in the early hours, 95 km '
                 'deep in the north of the country. Seismologists recorded '
                 'it at 2:35 a.m. local time.'),
        'art': draw_myanmar,
    },
    {
        'kicker': 'SPORT - TURIN',
        'headline': 'ZVEREV AND ALCARAZ MEET FOR TURIN CROWN TONIGHT',
        'deck': ('World No. 1 Zverev, unbeaten all week, faces Alcaraz for '
                 'the season-ending title at 6 p.m. Alcaraz seeks his first '
                 'Finals crown on a 13-match win streak.'),
        'art': draw_atp,
    },
    {
        'kicker': 'HONG KONG',
        'headline': 'HONG KONG VOTES FOR ITS POWERFUL ELECTION BODY',
        'deck': ('Some 5,700 voters cast ballots for the Election Committee, '
                 'the body that helps choose Hong Kong\'s leader and some of '
                 'its lawmakers.'),
        'art': draw_hongkong,
    },
]


def draw_panel(c, x, y, w, h, panel):
    c.rect(x, y, w, h, INK, 2)
    px = x + 12
    # Kicker with a red square.
    c.fill_rect(px, y + 12, 8, 8, RED)
    c.text(px + 14, y + 11, panel['kicker'], 1, RED)
    # Headline, bold, up to two lines.
    lines = wrap_text(panel['headline'].upper(), w - 24, 2)
    hy = y + 30
    for line in lines[:2]:
        c.text(px, hy, line, 2, INK, bold=True)
        hy += 18
    # Deck, three lines. The font holds capitals only, so decks are
    # uppercased here to keep every letter visible.
    dlines = wrap_text(panel['deck'].upper(), w - 24, 1)
    dy = hy + 6
    for line in dlines[:3]:
        c.text(px, dy, line, 1, INK)
        dy += 10
    # Illustration strip at the bottom.
    art_y = y + h - 84
    c.hline(x + 12, art_y - 6, w - 24, GREY, 1)
    panel['art'](c, x + 12, art_y, w - 24, 72)


def draw_page():
    c = Canvas(WIDTH, HEIGHT, PAPER)
    # Double outer border.
    c.rect(14, 14, WIDTH - 28, HEIGHT - 28, INK, 2)
    c.rect(20, 20, WIDTH - 40, HEIGHT - 40, INK, 1)
    # Masthead.
    c.text_centered(38, 'THE WORLD TODAY', 7, INK, bold=True)
    c.hline(60, 104, WIDTH - 120, RED, 4)
    c.text_centered(118, 'SUNDAY, 22 NOVEMBER 2026', 2, INK, bold=True)
    c.text_centered(140, 'THE DAY IN SEVEN STORIES', 1, GREY)
    c.hline(60, 158, WIDTH - 120, INK, 2)
    # Lead story, full width.
    lx, ly, lw, lh = 36, 172, WIDTH - 72, 196
    c.rect(lx, ly, lw, lh, INK, 2)
    c.fill_rect(lx + 12, ly + 12, 8, 8, RED)
    c.text(lx + 26, ly + 11, LEAD['kicker'], 1, RED)
    head_lines = wrap_text(LEAD['headline'].upper(), 560, 3)
    hy = ly + 32
    for line in head_lines[:2]:
        c.text(lx + 14, hy, line, 3, INK, bold=True)
        hy += 26
    deck_lines = wrap_text(LEAD['deck'].upper(), 560, 2)
    dy = hy + 8
    for line in deck_lines[:4]:
        c.text(lx + 14, dy, line, 2, INK)
        dy += 18
    # Lead illustration on the right.
    ix = lx + 600
    c.vline(ix - 8, ly + 12, lh - 24, GREY, 1)
    draw_gaza_lead(c, ix, ly + 10, lw - 612, lh - 20)
    # Grid of six panels: 2 columns x 3 rows.
    gx, gy = 36, 384
    pw, ph = (WIDTH - 72 - 12) // 2, 200
    for i, panel in enumerate(PANELS):
        px = gx + (i % 2) * (pw + 12)
        py = gy + (i // 2) * (ph + 8)
        draw_panel(c, px, py, pw, ph, panel)
    return c


# ---------------------------------------------------------------------------
# Hand-written PNG encoder (zlib from the standard library).
# ---------------------------------------------------------------------------
def encode_png(c):
    raw = bytearray()
    for yy in range(c.h):
        raw.append(0)  # filter: none
        raw += c.px[yy * c.w * 3:(yy + 1) * c.w * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack('>I', len(data)) + tag + data
        return out + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack('>IIBBBBB', c.w, c.h, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', comp)
            + chunk(b'IEND', b''))


def main():
    outdir = os.environ.get('MAKEFUN_OUTPUT_DIR') or '/output'
    os.makedirs(outdir, exist_ok=True)
    data = encode_png(draw_page())
    with open(os.path.join(outdir, 'entry.png'), 'wb') as f:
        f.write(data)


if __name__ == '__main__':
    main()
