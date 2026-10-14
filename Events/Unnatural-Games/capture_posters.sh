#!/usr/bin/env bash
# Print Unnatural Games tabloid posters to PDF, then rasterize PNG previews.
#   ./Events/Unnatural-Games/capture_posters.sh
#   ./Events/Unnatural-Games/capture_posters.sh v1-presents.html
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
UD="/tmp/chrome-unnatural-games-posters"
mkdir -p "$UD"

print_pdf() {
  local html="$1"
  local out="$2"
  local file="file://${ROOT// /%20}/${html}"
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
if not p.exists() or p.stat().st_size < 8000:
    raise SystemExit(f"PDF missing or too small: {p}")
print(f"Wrote {p} ({p.stat().st_size} bytes)")
PY
}

pdf_for() {
  case "$1" in
    v1-presents.html) echo "${ROOT}/Unnatural Games Poster v1 Presents (11×17).pdf" ;;
    v2-scoreboard.html) echo "${ROOT}/Unnatural Games Poster v2 Scoreboard (11×17).pdf" ;;
    v3-ticket.html) echo "${ROOT}/Unnatural Games Poster v3 Ticket (11×17).pdf" ;;
    templates.html) echo "${ROOT}/Fact Bar Templates (11×17).pdf" ;;
    *) echo "Unknown poster: $1" >&2; return 1 ;;
  esac
}

if [ "$#" -eq 0 ]; then
  set -- v1-presents.html v2-scoreboard.html v3-ticket.html templates.html
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
    print(f"{pdf.name}: pages={len(doc)} size={w/72:.2f}x{h/72:.2f} in")
    assert abs(w / 72 - 11) < 0.08 and abs(h / 72 - 17) < 0.08, (w, h)
    assert len(doc) == 1, f"{pdf.name} spilled to {len(doc)} pages"
    pil = page.render(scale=110 / 72).to_pil()
    out = pdf.with_suffix(".png")
    pil.save(out, optimize=True)
    print(f"  -> {out.name} {pil.size}")
PY
