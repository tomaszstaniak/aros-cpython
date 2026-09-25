#!/bin/sh
# Download every input listed in sources.txt into $WORK/downloads, check
# its SHA-256, and unpack the SDK into $WORK/sdk.
set -e
cd "$(dirname "$0")/.."
WORK="${WORK:-$PWD/work}"
mkdir -p "$WORK/downloads"
grep -v '^#' sources.txt | while read -r file sum url; do
    [ -n "$file" ] || continue
    out="$WORK/downloads/$file"
    [ -f "$out" ] || curl -fL --retry 3 -o "$out" "$url"
    echo "$sum  $out" | shasum -a 256 -c -
done
if [ ! -d "$WORK/sdk/SDK-202609/Development" ]; then
    mkdir -p "$WORK/sdk"
    unzip -q "$WORK/downloads/SDK-202609-any-x86_64.zip" -d "$WORK/sdk"
fi
