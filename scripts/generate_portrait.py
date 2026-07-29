#!/usr/bin/env python3
"""Turn a local portrait photo into an animated, self-contained ASCII SVG.

Requires ImageMagick (``magick`` or ``convert``), which is intentionally used
instead of a Python image dependency.  The generated SVG uses only SMIL, so the
line-by-line reveal works in GitHub READMEs.

Examples:
  python3 scripts/generate_portrait.py portrait/source.jpg
  python3 scripts/generate_portrait.py portrait/source.png --columns 76 --rows 76
  python3 scripts/generate_portrait.py --placeholder
"""

from __future__ import annotations

import argparse
import html
import math
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RAMP = " .`-:=+*cs#%@"
CHAR_WIDTH = 7.74  # JetBrains Mono at 12.9 px, whose advance is 0.600 em.
FONT_SIZE = 12.9
LINE_HEIGHT = 15
PADDING = 14


def imagemagick() -> str:
    """Return a supported ImageMagick executable or a useful error."""
    for command in ("magick", "convert"):
        if shutil.which(command):
            return command
    raise SystemExit(
        "ImageMagick is required. Install it, then retry "
        "(for example: sudo apt install imagemagick)."
    )


def pixels_from_photo(source: Path, columns: int, rows: int) -> bytes:
    """Centre-crop, normalize, and downsample an image to grayscale bytes."""
    command = [
        imagemagick(), str(source), "-auto-orient", "-colorspace", "Gray",
        "-resize", f"{columns}x{rows}^", "-gravity", "center", "-extent",
        f"{columns}x{rows}", "-contrast-stretch", "1%x1%", "-depth", "8",
        "gray:-",
    ]
    result = subprocess.run(command, check=True, stdout=subprocess.PIPE)
    expected = columns * rows
    if len(result.stdout) != expected:
        raise SystemExit(
            f"ImageMagick returned {len(result.stdout)} pixels; expected {expected}."
        )
    return result.stdout


def placeholder_pixels(columns: int, rows: int) -> bytes:
    """A neutral silhouette used only until a real photo is supplied."""
    values: list[int] = []
    for y in range(rows):
        for x in range(columns):
            nx = (x - (columns - 1) / 2) / columns
            ny = (y - rows * 0.44) / rows
            head = (nx / 0.21) ** 2 + (ny / 0.29) ** 2
            shoulders = (nx / 0.44) ** 2 + ((y / rows - 0.82) / 0.25) ** 2
            if head < 1:
                shade = int(85 + head * 50)
            elif shoulders < 1 and y > rows * 0.57:
                shade = int(105 + shoulders * 55)
            else:
                shade = 252
            values.append(shade)
    return bytes(values)


def ascii_lines(pixels: bytes, columns: int, rows: int) -> list[str]:
    """Map dark pixels to dense characters and light pixels to spaces."""
    lines = []
    for y in range(rows):
        row = pixels[y * columns:(y + 1) * columns]
        lines.append("".join(
            RAMP[round((255 - value) / 255 * (len(RAMP) - 1))]
            for value in row
        ))
    return lines


def svg(lines: list[str], columns: int, rows: int) -> str:
    """Draw the character grid with a one-time line-by-line SMIL reveal."""
    width = math.ceil(PADDING * 2 + columns * CHAR_WIDTH)
    height = PADDING * 2 + rows * LINE_HEIGHT
    duration = 0.055
    style = (
        ".a{fill:#6e7681}"
        "@media(prefers-color-scheme:dark){.a{fill:#c9d1d9}}"
    )
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}" '
        'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'
        '&apos;Liberation Mono&apos;,monospace">',
        f"<style>{style}</style>",
    ]
    for index, line in enumerate(lines):
        y = PADDING + index * LINE_HEIGHT
        delay = index * duration
        reveal_width = columns * CHAR_WIDTH
        escaped = html.escape(line)
        parts.extend([
            f'<clipPath id="line-{index}"><rect x="{PADDING}" y="{y}" '
            f'height="{LINE_HEIGHT}" width="0"><animate attributeName="width" '
            f'from="0" to="{reveal_width:.1f}" begin="{delay:.2f}s" '
            f'dur="{duration:.2f}s" fill="freeze"/></rect></clipPath>',
            f'<g clip-path="url(#line-{index})"><text xml:space="preserve" '
            f'x="{PADDING}" y="{y + FONT_SIZE - 1.7:.1f}" class="a" '
            f'font-size="{FONT_SIZE}">{escaped}</text></g>',
            f'<rect y="{y + 1}" width="6" height="{FONT_SIZE - 1:.1f}" '
            'class="a" opacity="0">'
            f'<animate attributeName="x" from="{PADDING}" '
            f'to="{PADDING + reveal_width:.1f}" begin="{delay:.2f}s" '
            f'dur="{duration:.2f}s" fill="freeze"/>'
            f'<set attributeName="opacity" to=".8" begin="{delay:.2f}s"/>'
            f'<set attributeName="opacity" to="0" begin="{delay + duration:.2f}s"/>'
            '</rect>',
        ])
    return "".join(parts) + "</svg>"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", type=Path,
                        help="Path to a locally stored portrait photo")
    parser.add_argument("--output", type=Path, default=ROOT / "ascii.svg",
                        help="SVG to write (default: ./ascii.svg)")
    parser.add_argument("--columns", type=int, default=72)
    parser.add_argument("--rows", type=int, default=72)
    parser.add_argument("--placeholder", action="store_true",
                        help="Create a neutral silhouette while waiting for a photo")
    args = parser.parse_args()

    if args.columns < 16 or args.rows < 16:
        parser.error("--columns and --rows must both be at least 16")
    if args.placeholder == (args.source is not None):
        parser.error("provide a source photo, or use --placeholder (but not both)")
    if args.source is not None and not args.source.is_file():
        parser.error(f"portrait source does not exist: {args.source}")

    pixels = (placeholder_pixels(args.columns, args.rows) if args.placeholder
              else pixels_from_photo(args.source, args.columns, args.rows))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg(ascii_lines(pixels, args.columns, args.rows),
                               args.columns, args.rows), encoding="utf-8")

    # Embed the exact ramp subset: image documents cannot fetch external fonts,
    # and JetBrains Mono keeps each generated character cell at a fixed width.
    subprocess.run([sys.executable, str(HERE / "embed_portrait_font.py"),
                    str(args.output)], check=True)
    print(f"wrote {args.output} ({args.columns}x{args.rows} characters)")


if __name__ == "__main__":
    main()
