#!/bin/zsh
# Build CPython in $BUILD_DIR (after configure.sh), then install it into
# $WORK/install for packaging.
# CFLAGS_NODIST=-std=gnu11: the AROS headers declare getcwd(), readlink()
# and other POSIX functions only when __STRICT_ANSI__ is not defined, and
# configure's -std=c11 defines it. This comes after configure's flags, so it
# replaces -std=c11.
set -e
cd "$(dirname "$0")/.."
. scripts/env.sh
cd "$BUILD_DIR"
# DATE/TIME: Modules/getbuildinfo.c takes the build stamp from __DATE__ and
# __TIME__ unless these are defined, and GCC 6.5 ignores SOURCE_DATE_EPOCH
# (GCC 7 added it). They are pinned to the same instant as SOURCE_DATE_EPOCH.
"$MAKE" -j2 CFLAGS_NODIST="-std=gnu11 -DDATE='\"Sep 25 2026\"' -DTIME='\"00:00:00\"'" "$@"
rm -rf "$WORK/install"
"$MAKE" install DESTDIR="$WORK/install" > install.log
shasum -a 256 python.exe
