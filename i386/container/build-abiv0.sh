#!/bin/bash
# Build the AROS ABIv0 i386 cross toolchain (GCC 6.5.0) and the pc-i386
# system from the ABIv0_20250313-1 tags, inside aros-abiv0-build.
# /work is a Docker volume; /ports holds pre-fetched ports sources.
set -euo pipefail
W=/work; TAG=ABIv0_20250313-1; J=${J:-2}
cd $W
if [ ! -d AROS ]; then
  git clone -q --depth 1 -b $TAG https://github.com/deadwood2/AROS.git AROS
  git clone -q --depth 1 -b $TAG https://github.com/deadwood2/contrib.git AROS/contrib
fi
echo "AROS $(git -C AROS rev-parse HEAD) contrib $(git -C AROS/contrib rev-parse HEAD)"
mkdir -p portssources && cp -n /ports/*.tar.* portssources/ 2>/dev/null || true
# GCC 6.5 is C++98 code; GCC 12 defaults to C++17.
export CXX="g++ -std=gnu++98"
if [ ! -x toolchain/i386-aros-gcc ]; then
  rm -rf toolchain-build; mkdir -p toolchain-build toolchain; cd toolchain-build
  ../AROS/configure --target=pc-i386 --with-aros-toolchain-install=$W/toolchain --with-portssources=$W/portssources
  make -s crosstools -j$J
  cd $W
fi
unset CXX
mkdir -p pc-i386; cd pc-i386
[ -f config.status ] || ../AROS/configure --target=pc-i386 --with-aros-toolchain=yes --with-aros-toolchain-install=$W/toolchain --with-portssources=$W/portssources
make -j$J
echo BUILD-OK
