#!/usr/bin/env bash
# Print podcast posters and the letter card pack to PDF, then rasterize previews.
#   ./Events/Podcast/capture.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
UD="/tmp/chrome-podcast-posters"
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

print_pdf "ep01-hate.html" "$ROOT/Podcast Poster E01 I Hate It (11x17).pdf"
print_pdf "ep02-useful.html" "$ROOT/Podcast Poster E02 So Useful (11x17).pdf"
print_pdf "ep03-finish.html" "$ROOT/Podcast Poster E03 Human Finish (11x17).pdf"
print_pdf "cards.html" "$ROOT/Podcast Cards Letter.pdf"

python3 - "$ROOT" <<'PY'
from pathlib import Path
import sys
root = Path(sys.argv[1])
import pypdfium2 as pdfium
jobs = [
    ("Podcast Poster E01 I Hate It (11x17).pdf", 11, 17),
    ("Podcast Poster E02 So Useful (11x17).pdf", 11, 17),
    ("Podcast Poster E03 Human Finish (11x17).pdf", 11, 17),
    ("Podcast Cards Letter.pdf", 8.5, 11),
]
for name, ew, eh in jobs:
    pdf = root / name
    doc = pdfium.PdfDocument(str(pdf))
    for i, page in enumerate(doc):
        w, h = page.get_size()
        print(f"{name} p{i+1}: {w/72:.2f}x{h/72:.2f} in")
        if abs(w/72 - ew) > 0.08 or abs(h/72 - eh) > 0.08:
            raise SystemExit(f"unexpected page size {w/72:.2f}x{h/72:.2f}")
        pil = page.render(scale=110/72).to_pil()
        suffix = "" if len(doc) == 1 else f"-p{i+1}"
        out = pdf.with_name(pdf.stem + suffix + ".png")
        pil.save(out, optimize=True)
        print(f"  -> {out.name} {pil.size}")
PY

python3 "$ROOT/export_png.py"
