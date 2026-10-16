"""
Terminal visualisation helpers: bar charts, histograms and Bloch spheres.

Kept dependency-free so the labs render identically in a terminal, in a
Jupyter notebook and inside the browser-based Python runner.
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Sequence, Tuple

__all__ = [
    "bar_chart",
    "histogram",
    "bloch_sphere_ascii",
    "qubit_bloch",
    "table",
    "boxed",
    "kv_table",
]


def bar_chart(
    data: Dict[str, float],
    width: int = 40,
    max_value: float | None = None,
    title: str = "",
) -> str:
    """
    Render a horizontal bar chart with Unicode block characters.

    >>> print(bar_chart({"00": 0.5, "11": 0.5}, width=20))
    """
    if not data:
        return "(no data)"
    top = max_value if max_value is not None else max(data.values())
    if top <= 0:
        top = 1.0
    lines = []
    if title:
        lines.append(title)
    for key, value in data.items():
        filled = int(round((value / top) * width))
        bar = "█" * filled + "·" * (width - filled)
        lines.append(f"{key:>10} |{bar}| {value:>8.4f}")
    return "\n".join(lines)


def histogram(counts: Dict[str, int], width: int = 40, title: str = "Counts") -> str:
    """Render a bar chart of measurement counts, normalised to the largest."""
    if not counts:
        return "(no counts)"
    total = sum(counts.values())
    norm = {k: v / total for k, v in counts.items()}
    lines = [f"{title}  (total {total} shots)"]
    lines.append(bar_chart(norm, width=width))
    lines.append("raw: " + ", ".join(f"{k}:{v}" for k, v in sorted(counts.items())))
    return "\n".join(lines)


def qubit_bloch(alpha: float, beta: float) -> Tuple[float, float, float]:
    """
    Convert the amplitudes ``alpha`` (for |0>) and ``beta`` (for |1>) into
    Bloch-sphere coordinates ``(x, y, z)``.

    ``x = 2*Re(alpha* conj(beta))``, ``y = 2*Im(alpha* conj(beta))``,
    ``z = |alpha|^2 - |beta|^2``
    """
    a = complex(alpha)
    b = complex(beta)
    prod = a * b.conjugate()
    x = 2 * prod.real
    y = 2 * prod.imag
    z = abs(a) ** 2 - abs(b) ** 2
    return (x, y, z)


def bloch_sphere_ascii(x: float, y: float, z: float, size: int = 13) -> str:
    """
    Render a Bloch sphere with the state as a marker, using ASCII art.

    The projection used is the simple orthographic one onto the (x, z)
    plane with the y component shown by a depth marker.
    """
    lines = []
    radius = size / 2.0
    cx = cy = radius
    for row in range(size):
        line = []
        for col in range(size):
            dx = (col - cx) / radius
            dz = -(row - cy) / radius
            r2 = dx * dx + dz * dz
            if r2 <= 1.0:
                shade = r2
                chars = " .:-=+*#%@"
                idx = int(shade * (len(chars) - 1))
                line.append(chars[idx])
            else:
                line.append(" ")
        lines.append("".join(line))

    # Place the state marker.
    mx = int(round(cx + x * radius))
    my = int(round(cy - z * radius))
    if 0 <= my < size and 0 <= mx < size:
        row = list(lines[my])
        row[mx] = "@"
        lines[my] = "".join(row)

    header = f"x={x:+.3f}  y={y:+.3f}  z={z:+.3f}"
    return header + "\n" + "\n".join(lines)


def table(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> str:
    """Render a simple aligned text table."""
    rows = [list(map(str, r)) for r in rows]
    widths = [len(h) for h in headers]
    for r in rows:
        for i, cell in enumerate(r):
            if i < len(widths):
                widths[i] = max(widths[i], len(cell))
    out = [" | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))]
    out.append("-+-".join("-" * w for w in widths))
    for r in rows:
        out.append(" | ".join(cell.ljust(widths[i]) for i, cell in enumerate(r)))
    return "\n".join(out)


def kv_table(data: Dict[str, object], key_width: int = 28) -> str:
    """Render a dictionary as an aligned ``key : value`` block."""
    width = max([key_width] + [len(k) for k in data]) if data else key_width
    return "\n".join(f"{k.ljust(width)} : {v}" for k, v in data.items())


def boxed(title: str, body: str = "", width: int = 68) -> str:
    """Draw a titled box around ``body``."""
    inner = width - 2
    lines = ["┌" + "─" * inner + "┐"]
    if title:
        t = f" {title} "
        lines.append("│" + t.ljust(inner) + "│")
        lines.append("├" + "─" * inner + "┤")
    for line in body.splitlines() or [""]:
        lines.append("│" + line.ljust(inner)[:inner] + "│")
    lines.append("└" + "─" * inner + "┘")
    return "\n".join(lines)
