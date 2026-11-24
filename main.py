#!/usr/bin/env python3
"""
main.py -- write the front-page entry to /output/entry.png.

Outside the grader, set MAKEFUN_OUTPUT_DIR to a local directory:

    MAKEFUN_OUTPUT_DIR=out python3 main.py

The image is always a 1024 x 1024 PNG of at most 1 MiB.
"""

from __future__ import annotations

import os
import struct
from pathlib import Path

import make_image


MAX_BYTES = 1024 * 1024
SIZE = 1024


def verify(path: Path) -> tuple[int, int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"{path} is not a PNG file")
    if len(data) > MAX_BYTES:
        raise RuntimeError(f"{path} is {len(data)} bytes, over the 1 MiB limit")
    width, height = struct.unpack(">II", data[16:24])
    if width > SIZE or height > SIZE:
        raise RuntimeError(f"{path} is {width}x{height}, over {SIZE}x{SIZE}")
    return width, height, len(data)


def main() -> None:
    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / "entry.png"

    make_image.render(str(target))
    width, height, size = verify(target)
    print(f"wrote {target} ({width}x{height}, {size} bytes)")


if __name__ == "__main__":
    main()
