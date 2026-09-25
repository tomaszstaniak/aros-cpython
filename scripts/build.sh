#!/bin/zsh
# Build CPython in $BUILD_DIR (after configure.sh), then install it into
# $WORK/install for packaging.
# CFLAGS_NODIST=-std=gnu11: the ABIv11 headers declare getcwd(), readlink()
# and other POSIX functions only when __STRICT_ANSI__ is not defined, and
# configure's -std=c11 defines it. This comes after configure's flags, so it
# replaces -std=c11.
set -e
cd "$(dirname "$0")/.."
. scripts/env.sh
cd "$BUILD_DIR"
"$MAKE" -j8 CFLAGS_NODIST=-std=gnu11 "$@"
rm -rf "$WORK/install"
"$MAKE" install DESTDIR="$WORK/install" > install.log
shasum -a 256 python.exe
