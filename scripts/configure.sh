#!/bin/zsh
# Cross-configure CPython for AROS x86_64 ABIv11 in $BUILD_DIR.
# PKG_CONFIG: scripts/bin/aros-v11-pkg-config knows only the OpenSSL and
#   liblzma built by build-deps.sh, so no host library reaches the link.
# MODULE_BUILDTYPE=static: AROS cannot load C extension modules.
# LDFLAGS=-nix: Unix-style path translation in the C library (/Python/lib).
# LIBS=-lnet: SocketBase for bsdsocket.library.
# OPENSSL_NO_*_METHOD: OpenSSL 4.0 has no per-version SSLv3/TLSv1.x method
#   functions, and _ssl.c leaves them out only under these macros.
set -e
cd "$(dirname "$0")/.."
. scripts/env.sh
[ -x "$BUILD_PYTHON" ] || { echo "BUILD_PYTHON: a host Python 3.14 is needed" >&2; exit 1; }
mkdir -p "$BUILD_DIR" && cd "$BUILD_DIR"
# configure is run by a relative path: the source directory (VPATH) is
# compiled into the interpreter, and an absolute one would be a host path.
SRCREL=$("$BUILD_PYTHON" -c 'import os, sys; print(os.path.relpath(sys.argv[1]))' "$SRC")
CONFIG_SITE="$REPO/config/config.site" \
CFLAGS="-O2 -DOPENSSL_NO_SSL3 -DOPENSSL_NO_SSL3_METHOD -DOPENSSL_NO_TLS1_METHOD -DOPENSSL_NO_TLS1_1_METHOD -DOPENSSL_NO_TLS1_2_METHOD" \
CPPFLAGS="-I$DEPS/include" LDFLAGS="-nix -L$DEPS/lib" LIBS="-lnet" \
MODULE_BUILDTYPE=static PKG_CONFIG=aros-v11-pkg-config \
"$SRCREL/configure" \
    --host=x86_64-aros --build="$(sh "$SRCREL/config.guess")" \
    --with-build-python="$BUILD_PYTHON" \
    --disable-shared --disable-ipv6 --without-ensurepip \
    --disable-test-modules --without-pymalloc --without-mimalloc \
    --with-suffix=.exe \
    AROS_ABI="$AROS_ABI" AROS_ABI_MAJOR="$AROS_ABI_MAJOR" \
    --prefix=/Python 2>&1 | tee configure.log
