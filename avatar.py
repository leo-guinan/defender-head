"""avatar.py — deterministic identicon from a stable seed (e.g. accountId).

Twitter's pbs.twimg.com avatar URLs are CDN-rotated and not fetchable, so we
generate a stable, unique SVG avatar from the identity instead. Same seed ->
same avatar, so Defender's headshot is consistent across rebuilds and ties
visually to his real archive accountId.
"""
from __future__ import annotations

import hashlib
from pathlib import Path


def identicon_svg(seed: str, size: int = 256) -> str:
    h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    # 5x5 symmetric grid, foreground color from hash
    fg = f"#{h[:6]}"
    bg = f"#{h[6:8]}{h[8:10]}{h[10:12]}"
    cells = []
    bits = [int(b, 16) for b in h[:15]]  # 15 half-bytes -> 15 cells (left 3 cols)
    idx = 0
    cell = size // 5
    for row in range(5):
        for col in range(3):  # mirror across
            on = (bits[idx % len(bits)] >> (col % 4)) & 1
            idx += 1
            if on:
                x = col * cell
                y = row * cell
                cells.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}"/>')
                # mirror
                mx = (4 - col) * cell
                cells.append(f'<rect x="{mx}" y="{y}" width="{cell}" height="{cell}"/>')
    rects = "\n".join(f'    {c}' for c in cells)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 {size} {size}">\n'
        f'  <rect width="{size}" height="{size}" fill="{bg}"/>\n'
        f'{rects}\n'
        f'  <rect width="{size}" height="{size}" fill="{fg}" fill-opacity="0" '
        f'style="mix-blend-mode:multiply"/>\n'
        f'</svg>\n'
    )


def write_headshot(seed: str, dest: Path) -> Path:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(identicon_svg(seed), encoding="utf-8")
    return dest
