#!/bin/sh
# Build the i386 ABIv0 toolchain (GCC 6.5.0 from deadwood2 ABIv0_20250313-1)
# and CPython 3.14.7 for it, in containers. Needs podman (docker works the
# same) and ./fetch-inputs.sh run first. Run from any directory:
#   i386/fetch-inputs.sh && i386/build-i386.sh
#   i386/out/python.exe   the interpreter; i386-aros-strip --strip-debug of
#                         it is what the package ships (see package/
#                         interpreter-provenance.txt)
# --security-opt label=disable: on hosts with SELinux enforcing (Fedora) the
# bind-mounted scripts cannot be executed otherwise; it changes nothing in
# the build.
set -e
cd "$(dirname "$0")"
I=$(pwd)
E=${ENGINE:-podman}
[ "$E" = podman ] && SEC="--security-opt label=disable" || SEC=
$E build -t aros-abiv0-build:bookworm -f container/Dockerfile container
sed 's/^FROM aros-abiv0-build:bookworm/FROM localhost\/aros-abiv0-build:bookworm/' container/Dockerfile.py > container/Dockerfile.py.local
[ "$E" = podman ] || cp container/Dockerfile.py container/Dockerfile.py.local
$E build -t aros-abiv0-build:py314 -f container/Dockerfile.py.local .
$E volume create aros-abiv0-work >/dev/null 2>&1 || true
# 1. toolchain (and, as a cross-check, the whole pc-i386 system)
$E run --rm $SEC -v aros-abiv0-work:/work -v "$I/ports:/ports:ro" \
    -v "$I/container:/scripts:ro" -e J="$(nproc)" aros-abiv0-build:bookworm \
    bash -c '/scripts/build-abiv0.sh > /work/build.log 2>&1; echo rc=$? >> /work/build.log; tail -3 /work/build.log'
# 2. dependencies and interpreter
$E run --rm $SEC -v aros-abiv0-work:/work -v "$I:/i386" -v "$I/sdk:/sdk:ro" \
    aros-abiv0-build:py314 bash -c '/i386/container/build-python.sh && cp /work/py/build/python.exe /i386/python.exe'
mkdir -p out && mv python.exe out/python.exe
sha256sum out/python.exe
