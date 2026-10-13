#!/usr/bin/env bash
# Build a self-contained static site for the Clubs Expo table page.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/Events/Clubs-Expo"
OUT="${1:-$ROOT/docs}"

if [ ! -f "$SRC/table-concepts.html" ]; then
  echo "Missing $SRC/table-concepts.html" >&2
  exit 1
fi

rm -rf "$OUT"
mkdir -p "$OUT/fonts" "$OUT/assets"

cp -R "$SRC/assets/." "$OUT/assets/"
cp -R "$SRC/git-walk-seed" "$OUT/git-walk-seed"
cp "$SRC/README.md" "$OUT/README.md"

for font in \
  Inter-Regular.ttf \
  Inter-Medium.ttf \
  Inter-SemiBold.ttf \
  Inter-Bold.ttf \
  InterDisplay-Bold.ttf \
  JetBrainsMono-Regular.ttf \
  JetBrainsMono-Bold.ttf \
  LICENSE.txt
do
  cp "$ROOT/charter/fonts/$font" "$OUT/fonts/"
done

rewrite() {
  sed 's|url("../../charter/fonts/|url("fonts/|g'
}

rewrite < "$SRC/table-concepts.html" > "$OUT/index.html"
rewrite < "$SRC/git-walk.html" > "$OUT/git-walk.html"
sed -i 's|href="table-concepts.html#git-walk"|href="./#git-walk"|g' "$OUT/git-walk.html"
sed -i 's|href="table-concepts.html"|href="./"|g' "$OUT/git-walk.html"

touch "$OUT/.nojekyll"

echo "Wrote static site to $OUT"
