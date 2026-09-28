# Build environment for CPython on AROS i386 ABIv0 (deadwood2 ABIv0_20250313-1).
# Source it from the i386 directory:  . scripts/env.sh
# Runs inside the aros-abiv0-build container (container/), where the
# i386-aros cross compiler (GCC 6.5.0) was built from the same tag.
#   AROS_TOOLCHAIN  directory with i386-aros-gcc (default /work/toolchain)
#   AROS_SDK        the release ISO's Development directory
#   WORK            sources, builds and packages (default /work/py)
#   BUILD_PYTHON    host Python 3.14.7 (default /opt/py314/bin/python3.14)
export AROS_TOOLCHAIN="${AROS_TOOLCHAIN:-/work/toolchain}"
export REPO="$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%x}}")/.." && pwd)"
export WORK="${WORK:-/work/py}"
export AROS_SDK="${AROS_SDK:-/sdk/Development}"
export PATH="$REPO/scripts/bin:$AROS_TOOLCHAIN:$PATH"
export CC=aros-v0-gcc CXX=aros-v0-g++
export AR=i386-aros-ar RANLIB=i386-aros-ranlib READELF=i386-aros-readelf
export AROS_ABI=abiv0
export AROS_ABI_MAJOR=0           # rom/aros/arosinquirea.c at ABIv0_20250313-1
export DEPS="$WORK/deps"
export BUILD_PYTHON="${BUILD_PYTHON:-/opt/py314/bin/python3.14}"
export PY_VER=3.14.7
export SRC="$WORK/src/Python-$PY_VER"
export BUILD_DIR="$WORK/build"
export MAKE="${MAKE:-make}"
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-1790294400}"
