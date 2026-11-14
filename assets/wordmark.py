#!/usr/bin/env python3
"""Regenerate the profile wordmark.

Text is converted to SVG paths with HarfBuzz + fontTools so the header renders
identically on every OS instead of falling back to whatever sans-serif the
viewer happens to have. Inter is SIL OFL 1.1.

    pip install uharfbuzz fonttools
    curl -LO https://github.com/rsms/inter/releases/download/v4.1/Inter-4.1.zip
    unzip -j Inter-4.1.zip 'extras/ttf/Inter-SemiBold.ttf'
    python3 assets/wordmark.py

Writes assets/wordmark-{light,dark}.svg. Colours are GitHub's own
fg.default / border.default tokens for each theme.
"""
import os
import pathlib
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

NAME = "Sourav P Bijoy"
FONT = os.environ.get("INTER_SEMIBOLD", "Inter-SemiBold.ttf")
SIZE = 46
TRACKING = -0.022      # em
HEIGHT = 92
BASELINE = 58

THEMES = {
    "light": ("#1f2328", "#d0d7de"),
    "dark": ("#e6edf3", "#30363d"),
}


def shape(font_path, text, size, tracking):
    blob = hb.Blob.from_file_path(font_path)
    face = hb.Face(blob)
    font = hb.Font(face)
    font.scale = (face.upem, face.upem)

    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True})

    tt = TTFont(font_path)
    glyphs, order = tt.getGlyphSet(), tt.getGlyphOrder()
    scale = size / face.upem

    parts, x = [], 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        pen = SVGPathPen(glyphs)
        glyphs[order[info.codepoint]].draw(
            TransformPen(pen, Transform(scale, 0, 0, -scale, x + pos.x_offset * scale, 0))
        )
        d = pen.getCommands()
        if d:
            parts.append(d)
        x += pos.x_advance * scale + tracking * size
    return " ".join(parts), x


def main():
    d, width = shape(FONT, NAME, SIZE, TRACKING)
    w = round(width)
    out = pathlib.Path(__file__).parent
    for theme, (fg, rule) in THEMES.items():
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{HEIGHT}" '
            f'viewBox="0 0 {w} {HEIGHT}" role="img" aria-label="{NAME}">\n'
            f'  <g transform="translate(0 {BASELINE})" fill="{fg}"><path d="{d}"/></g>\n'
            f'  <rect x="0" y="{HEIGHT - 1}" width="{w}" height="1" fill="{rule}"/>\n'
            f"</svg>\n"
        )
        (out / f"wordmark-{theme}.svg").write_text(svg)
        print(f"wordmark-{theme}.svg  {w}x{HEIGHT}  {len(svg)} bytes")


if __name__ == "__main__":
    main()
