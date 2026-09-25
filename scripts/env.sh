# Build environment for CPython on AROS x86_64 ABIv11. Source it from the
# repository root:  . scripts/env.sh
#
# Required:
#   AROS_TOOLCHAIN  directory with x86_64-aros-gcc (GCC 10.5.0, see
#                   docs/building.md)
# Optional:
#   WORK            where sources, builds and packages go (default ./work)
#   BUILD_PYTHON    a host Python 3.14 (default: python3.14 on PATH)
#   AROS_SDK        the SDK's Development directory (default: extracted by
#                   scripts/fetch-sources.sh into $WORK/sdk)
[ -n "$AROS_TOOLCHAIN" ] || { echo "set AROS_TOOLCHAIN (see docs/building.md)" >&2; return 1 2>/dev/null || exit 1; }
export REPO="$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%x}}")/.." && pwd)"
export WORK="${WORK:-$REPO/work}"
export AROS_SDK="${AROS_SDK:-$WORK/sdk/SDK-202609/Development}"
export PATH="$REPO/scripts/bin:$AROS_TOOLCHAIN:$PATH"
export CC=aros-v11-gcc CXX=aros-v11-g++
export AR=x86_64-aros-ar RANLIB=x86_64-aros-ranlib READELF=x86_64-aros-readelf
export AROS_ABI=abiv11
export AROS_ABI_MAJOR=11          # ENV:ABI on ABIv11 systems
export DEPS="$WORK/deps"          # static OpenSSL, jitterentropy, liblzma
export BUILD_PYTHON="${BUILD_PYTHON:-$(command -v python3.14)}"
export PY_VER=3.14.7
export SRC="$WORK/src/Python-$PY_VER"
export BUILD_DIR="$WORK/build"
# GNU make 4 (CPython and OpenSSL); macOS's /usr/bin/make is 3.81.
export MAKE="${MAKE:-$(command -v gmake || command -v make)}"
# A fixed build time (2026-09-25 00:00 UTC), used by GCC for __DATE__ and
# __TIME__ and by OpenSSL for its build date, so that two builds from this
# repository with the same compiler give the same binary.
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-1790294400}"
