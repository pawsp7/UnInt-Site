#!/usr/bin/env bash
# Rasterize index.html at 150 DPI (10800×5400) from the live SVG mascot.
# Uses the 1920×960 CSS layout with a 5.625 device scale so the HTML layout
# matches banner_6x3ft_html_layout.png rather than changing CSS-pixel sizes.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT="$ROOT/banner_6x3ft_html_layout.png"
TMP="/tmp/banner-html-150dpi.png"
URL="file://${ROOT// /%20}/index.html?capture=1"
SCALE="5.625"

timeout 90 google-chrome \
  --headless \
  --disable-gpu \
  --disable-dev-shm-usage \
  --hide-scrollbars \
  --no-sandbox \
  --user-data-dir="/tmp/chrome-banner-150" \
  --window-size=1920,960 \
  --force-device-scale-factor="$SCALE" \
  --virtual-time-budget=20000 \
  --screenshot="$TMP" \
  "$URL" || true

python3 - "$TMP" "$OUT" <<'PY'
import sys
from pathlib import Path
from PIL import Image

src, dest = Path(sys.argv[1]), Path(sys.argv[2])
if not src.exists():
    raise SystemExit(f"Chrome did not write {src}")
im = Image.open(src)
if im.size != (10800, 5400):
    raise SystemExit(f"Unexpected size {im.size}, expected 10800×5400")
im.save(dest, format="PNG", compress_level=9, dpi=(150, 150))
print(f"Wrote {dest} {im.size[0]}×{im.size[1]} @ 150 DPI")
PY
