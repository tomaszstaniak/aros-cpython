#!/bin/bash
# Inside aros-abiv0-build:py314: prepare, configure and build CPython for
# AROS i386 ABIv0 from /i386 (the i386 tree) into /work/py.
set -euo pipefail
cd /i386
export AROS_SDK=/sdk/Development
[ -d /work/py/src/Python-3.14.7 ] || WORK=/work/py scripts/prepare-source.sh
[ -f /work/py/deps/lib/libssl.a ] || zsh scripts/build-deps.sh > /work/py/deps.out 2>&1 || { grep -n "error" /work/py/deps.out | head -30; tail -20 /work/py/deps.out; exit 1; }
rm -rf /work/py/build
zsh scripts/configure.sh > /work/py/configure.out 2>&1
grep -q "^config.status: creating Makefile" /work/py/configure.out || { tail -30 /work/py/configure.out; exit 1; }
zsh scripts/build.sh > /work/py/build.out 2>&1 || { grep -n "error" /work/py/build.out | head -40; tail -30 /work/py/build.out; exit 1; }
tail -3 /work/py/build.out
