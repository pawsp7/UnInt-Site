#!/usr/bin/env bash
# Rasterize hero tags at 300 DPI and write print PDFs (Letter kit + A4 fill-in).
# Run from anywhere:
#   ./Branding/Design\ Templates/Name-Tags/capture_nametags.sh
#   ./Branding/Design\ Templates/Name-Tags/capture_nametags.sh --pdf-only
#   ./Branding/Design\ Templates/Name-Tags/capture_nametags.sh --exec-stickers
#   ./Branding/Design\ Templates/Name-Tags/capture_nametags.sh --a4-human
#   ./Branding/Design\ Templates/Name-Tags/capture_nametags.sh --a4-human-ticket
#   ./Branding/Design\ Templates/Name-Tags/capture_nametags.sh --a4-clanker-ticket
#   ./Branding/Design\ Templates/Name-Tags/capture_nametags.sh --a4-human-ticket-pen
#   ./Branding/Design\ Templates/Name-Tags/capture_nametags.sh --a4-human-ticket-pen-variants
#   ./Branding/Design\ Templates/Name-Tags/capture_nametags.sh --luiz
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
FILE="file://${ROOT// /%20}/index.html"
UD="/tmp/chrome-nametags"
mkdir -p "$UD"

chrome() {
  local seconds="${TIMEOUT_SECS:-8}"
  timeout "$seconds" google-chrome \
    --headless \
    --disable-gpu \
    --disable-dev-shm-usage \
    --hide-scrollbars \
    --no-sandbox \
    --user-data-dir="$UD" \
    --virtual-time-budget=3000 \
    --run-all-compositor-stages-before-draw \
    "$@" || true
}

# CSS px at 96 dpi. Device scale 3.125 → 300 DPI.
capture_tag() {
  local spec="$1"
  local out="$2"
  local w="$3"
  local h="$4"
  local tmp="/tmp/nametag-${spec}-$$.png"
  rm -f "/tmp/nametag-${spec}.png" "$tmp"
  chrome \
    --window-size="$w,$h" \
    --force-device-scale-factor=3.125 \
    --screenshot="$tmp" \
    "${FILE}?capture=${spec}"
  python3 - "$tmp" "$out" <<'PY'
import sys
from pathlib import Path
src, dest = Path(sys.argv[1]), Path(sys.argv[2])
if not src.exists():
    raise SystemExit(f"Chrome did not write {src}")
data = src.read_bytes()
if len(data) < 1000:
    raise SystemExit(f"Screenshot too small: {src} ({len(data)} bytes)")
dest.write_bytes(data)
print(f"Wrote {dest} ({len(data)} bytes)")
PY
}

# 4 in × 3 in → 384×288 CSS px
capture_lanyard() { capture_tag "$1" "$2" 384 288; }
# 3.5 in × 2 in → 336×192 CSS px
capture_sticker() { capture_tag "$1" "$2" 336 192; }

write_pdf() {
  local query="$1"
  local out="$2"
  TIMEOUT_SECS=60 chrome \
    --no-pdf-header-footer \
    --print-to-pdf="$out" \
    "${FILE}?${query}"
  python3 - "$out" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
if not p.exists() or p.stat().st_size < 10000:
    raise SystemExit(f"PDF missing or too small: {p}")
print(f"Wrote {p} ({p.stat().st_size} bytes)")
PY
}

write_pen_variant_pdfs() {
  write_pdf "print=a4-human-ticket-pen-lime" "$ROOT/Human-Ticket-Pen-Lime-A4.pdf"
  write_pdf "print=a4-human-ticket-pen-olive" "$ROOT/Human-Ticket-Pen-Olive-A4.pdf"
  write_pdf "print=a4-human-ticket-pen-ink" "$ROOT/Human-Ticket-Pen-Ink-A4.pdf"
  write_pdf "print=a4-human-ticket-pen-sampler" "$ROOT/Human-Ticket-Pen-Sampler-A4.pdf"
}

MODE="${1:-}"
SKIP_PNG=0
case "$MODE" in
  --pdf-only|--exec-stickers|--a4-human|--a4-human-ticket|--a4-clanker-ticket|--a4-human-ticket-pen|--a4-human-ticket-pen-lime|--a4-human-ticket-pen-olive|--a4-human-ticket-pen-ink|--a4-human-ticket-pen-sampler|--a4-human-ticket-pen-variants|--luiz)
    SKIP_PNG=1
    ;;
esac
if [[ "$SKIP_PNG" != "1" ]]; then
  capture_lanyard ticket-exec "$ROOT/nametag-exec-ticket.png"
  capture_lanyard ticket-member "$ROOT/nametag-member-ticket.png"
  capture_lanyard ticket-clanker "$ROOT/nametag-clanker-ticket.png"
  capture_lanyard lockup-exec "$ROOT/nametag-exec-lockup.png"
  capture_lanyard lockup-member "$ROOT/nametag-member-lockup.png"
  capture_lanyard lockup-clanker "$ROOT/nametag-clanker-lockup.png"
  capture_lanyard ticket-exec-blank "$ROOT/nametag-exec-ticket-blank.png"
  capture_lanyard ticket-member-blank "$ROOT/nametag-member-ticket-blank.png"
  capture_lanyard ticket-clanker-blank "$ROOT/nametag-clanker-ticket-blank.png"
  capture_lanyard lockup-member-blank "$ROOT/nametag-member-lockup-blank.png"

  capture_sticker sticker-exec "$ROOT/nametag-exec-sticker.png"
  capture_sticker sticker-member "$ROOT/nametag-member-sticker.png"
  capture_sticker sticker-clanker "$ROOT/nametag-clanker-sticker.png"
  capture_sticker spec-exec "$ROOT/nametag-exec-spec.png"
  capture_sticker spec-member "$ROOT/nametag-member-spec.png"
  capture_sticker spec-clanker "$ROOT/nametag-clanker-spec.png"
  capture_sticker sticker-exec-blank "$ROOT/nametag-exec-sticker-blank.png"
  capture_sticker spec-clanker-blank "$ROOT/nametag-clanker-spec-blank.png"
  capture_lanyard ticket-clanker-luiz "$ROOT/nametag-luiz-ticket.png"
fi

if [[ "$MODE" == "--exec-stickers" ]]; then
  write_pdf "print=exec-stickers" "$ROOT/Exec-Stickers.pdf"
elif [[ "$MODE" == "--a4-human" ]]; then
  write_pdf "print=a4-human-fillin" "$ROOT/Human-Fill-In-A4.pdf"
elif [[ "$MODE" == "--a4-human-ticket" ]]; then
  write_pdf "print=a4-human-ticket" "$ROOT/Human-Ticket-Fill-In-A4.pdf"
elif [[ "$MODE" == "--a4-clanker-ticket" ]]; then
  write_pdf "print=a4-clanker-ticket" "$ROOT/Clanker-Ticket-Fill-In-A4.pdf"
elif [[ "$MODE" == "--a4-human-ticket-pen" ]]; then
  write_pdf "print=a4-human-ticket-pen" "$ROOT/Human-Ticket-Pen-A4.pdf"
elif [[ "$MODE" == "--a4-human-ticket-pen-lime" ]]; then
  write_pdf "print=a4-human-ticket-pen-lime" "$ROOT/Human-Ticket-Pen-Lime-A4.pdf"
elif [[ "$MODE" == "--a4-human-ticket-pen-olive" ]]; then
  write_pdf "print=a4-human-ticket-pen-olive" "$ROOT/Human-Ticket-Pen-Olive-A4.pdf"
elif [[ "$MODE" == "--a4-human-ticket-pen-ink" ]]; then
  write_pdf "print=a4-human-ticket-pen-ink" "$ROOT/Human-Ticket-Pen-Ink-A4.pdf"
elif [[ "$MODE" == "--a4-human-ticket-pen-sampler" ]]; then
  write_pdf "print=a4-human-ticket-pen-sampler" "$ROOT/Human-Ticket-Pen-Sampler-A4.pdf"
elif [[ "$MODE" == "--a4-human-ticket-pen-variants" ]]; then
  write_pen_variant_pdfs
elif [[ "$MODE" == "--luiz" ]]; then
  capture_lanyard ticket-clanker-luiz "$ROOT/nametag-luiz-ticket.png"
  write_pdf "print=luiz-ticket" "$ROOT/Luiz-Clanker-Ticket.pdf"
else
  write_pdf "print=1" "$ROOT/Name-Tags.pdf"
  write_pdf "print=exec-stickers" "$ROOT/Exec-Stickers.pdf"
  write_pdf "print=a4-human-fillin" "$ROOT/Human-Fill-In-A4.pdf"
  write_pdf "print=a4-human-ticket" "$ROOT/Human-Ticket-Fill-In-A4.pdf"
  write_pdf "print=a4-clanker-ticket" "$ROOT/Clanker-Ticket-Fill-In-A4.pdf"
  write_pdf "print=a4-human-ticket-pen" "$ROOT/Human-Ticket-Pen-A4.pdf"
  write_pen_variant_pdfs
  write_pdf "print=luiz-ticket" "$ROOT/Luiz-Clanker-Ticket.pdf"
fi
ls -lh "$ROOT"/nametag-*.png "$ROOT"/Name-Tags.pdf "$ROOT"/Exec-Stickers.pdf "$ROOT"/Human-Fill-In-A4.pdf "$ROOT"/Human-Ticket-Fill-In-A4.pdf "$ROOT"/Clanker-Ticket-Fill-In-A4.pdf "$ROOT"/Human-Ticket-Pen-A4.pdf "$ROOT"/Human-Ticket-Pen-Lime-A4.pdf "$ROOT"/Human-Ticket-Pen-Olive-A4.pdf "$ROOT"/Human-Ticket-Pen-Ink-A4.pdf "$ROOT"/Human-Ticket-Pen-Sampler-A4.pdf "$ROOT"/Luiz-Clanker-Ticket.pdf
# Drop the old human-only PDF name if it is still around.
rm -f "$ROOT/Name-Tags-human.pdf"
