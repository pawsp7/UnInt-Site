#!/usr/bin/env bash
# Print AI Agents tabloid posters to PDF, then rasterize PNG previews.
#   ./Events/AI-Agents/capture_posters.sh
#   ./Events/AI-Agents/capture_posters.sh v4-toolkit.html v5-lime.html v6-nodes.html
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
UD="/tmp/chrome-ai-agents-posters"
mkdir -p "$UD"

print_pdf() {
  local html="$1"
  local out="$2"
  local file="file://${ROOT// /%20}/${html}"
  # Chrome often hangs after writing the PDF; timeout and keep the file.
  timeout 50 google-chrome \
    --headless \
    --disable-gpu \
    --disable-dev-shm-usage \
    --hide-scrollbars \
    --no-sandbox \
    --user-data-dir="$UD" \
    --no-pdf-header-footer \
    --print-to-pdf="$out" \
    "$file" || true
  python3 - "$out" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
if not p.exists() or p.stat().st_size < 10000:
    raise SystemExit(f"PDF missing or too small: {p}")
print(f"Wrote {p} ({p.stat().st_size} bytes)")
PY
}

pdf_for() {
  case "$1" in
    v1-ink.html) echo "${ROOT}/AI Agents Poster v1 Ink (11×17).pdf" ;;
    v2-paper.html) echo "${ROOT}/AI Agents Poster v2 Paper (11×17).pdf" ;;
    v3-arcade.html) echo "${ROOT}/AI Agents Poster v3 Arcade (11×17).pdf" ;;
    v4-toolkit.html) echo "${ROOT}/AI Agents Poster v4 Toolkit (11×17).pdf" ;;
    v5-lime.html) echo "${ROOT}/AI Agents Poster v5 Lime (11×17).pdf" ;;
    v6-nodes.html) echo "${ROOT}/AI Agents Poster v6 Nodes (11×17).pdf" ;;
    v7-split.html) echo "${ROOT}/AI Agents Poster v7 Split (11×17).pdf" ;;
    v8-bands.html) echo "${ROOT}/AI Agents Poster v8 Bands (11×17).pdf" ;;
    v9-billboard.html) echo "${ROOT}/AI Agents Poster v9 Billboard (11×17).pdf" ;;
    v10-monument.html) echo "${ROOT}/AI Agents Poster v10 Monument (11×17).pdf" ;;
    v11-listings.html) echo "${ROOT}/AI Agents Poster v11 Listings (11×17).pdf" ;;
    v12-versus.html) echo "${ROOT}/AI Agents Poster v12 Versus (11×17).pdf" ;;
    *) echo "Unknown poster: $1" >&2; return 1 ;;
  esac
}

if [ "$#" -eq 0 ]; then
  set -- v1-ink.html v2-paper.html v3-arcade.html v4-toolkit.html v5-lime.html v6-nodes.html v7-split.html v8-bands.html v9-billboard.html v10-monument.html v11-listings.html v12-versus.html
fi

PDFS=()
for html in "$@"; do
  pdf="$(pdf_for "$html")"
  print_pdf "$html" "$pdf"
  PDFS+=("$pdf")
done

python3 - "${PDFS[@]}" <<'PY'
from pathlib import Path
import sys
import pypdfium2 as pdfium
for pdf in map(Path, sys.argv[1:]):
    doc = pdfium.PdfDocument(str(pdf))
    page = doc[0]
    w, h = page.get_size()
    assert abs(w / 72 - 11) < 0.05 and abs(h / 72 - 17) < 0.05, (w, h)
    pil = page.render(scale=150 / 72).to_pil()
    out = pdf.with_suffix(".png")
    pil.save(out, optimize=True)
    print(f"{pdf.name}: {w/72:.2f}x{h/72:.2f} in -> {out.name} {pil.size}")
PY

ls -lh "$ROOT"/*.pdf "$ROOT"/*.png
