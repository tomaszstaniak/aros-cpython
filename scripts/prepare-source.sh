#!/bin/sh
# Unpack CPython 3.14.7 into $WORK/src and apply patches/cpython in order.
set -e
cd "$(dirname "$0")/.."
REPO=$PWD
WORK="${WORK:-$REPO/work}"
S="$WORK/src/Python-3.14.7"
[ ! -e "$S" ] || { echo "$S exists; remove it to prepare again" >&2; exit 1; }
mkdir -p "$WORK/src"
tar -C "$WORK/src" -xJf "$WORK/downloads/Python-3.14.7.tar.xz"
for p in "$REPO"/patches/cpython/*.patch; do
    patch -d "$S" -p1 -s < "$p"
done
echo "prepared $S"
