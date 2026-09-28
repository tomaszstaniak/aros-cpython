#!/bin/zsh
# Build the static libraries linked into the interpreter, into $DEPS:
#   abiv0compat          C library functions ABIv0 lacks (compat/)
#   jitterentropy 3.7.0  seed source for OpenSSL (AROS has no OS entropy)
#   OpenSSL 4.0.1        _ssl, _hashlib
#   liblzma 5.8.3        lzma (the system's xz library decodes only)
set -e
cd "$(dirname "$0")/.."
. scripts/env.sh
DL="$REPO/downloads"; D="$WORK/deps-src"; O="$WORK/deps-obj"
mkdir -p "$D" "$O" "$DEPS/lib" "$DEPS/include"

# abiv0compat: see compat/abiv0compat.h.
rm -rf "$O/compat"; mkdir -p "$O/compat"
aros-v0-gcc -c -O2 -std=gnu11 -Wall -Wextra compat/abiv0compat.c -o "$O/compat/abiv0compat.o"
i386-aros-ar rcs "$DEPS/lib/libabiv0compat.a" "$O/compat/abiv0compat.o"
cp compat/abiv0compat.h "$DEPS/include/"

# jitterentropy: its Makefile's flags (the noise source must be built with
# -O0), without JENT_CONF_ENABLE_INTERNAL_TIMER, which needs C11 <threads.h>
# (not in the ABIv0 SDK either); rdtsc is the time source. The patch removes the
# FIPS mode check through /proc, which makes AROS ask for a volume "proc".
J="$D/jitterentropy-library-3.7.0"
if [ ! -d "$J" ]; then
    tar -C "$D" -xzf "$DL/jitterentropy-v3.7.0.tar.gz"
    patch -d "$J" -p1 -s < patches/jitterentropy-3.7.0-abiv11.diff
fi
rm -rf "$O/jitter"; mkdir -p "$O/jitter"
for f in "$J"/src/*.c; do
    aros-v0-gcc -c -O0 -fwrapv -std=c11 -Wall -Wextra -I"$J" -I"$J/src" "$f" \
        -o "$O/jitter/$(basename "$f" .c).o"
done
i386-aros-ar rcs "$DEPS/lib/libjitterentropy.a" "$O"/jitter/*.o
cp "$J/jitterentropy.h" "$J/jitterentropy-base-user.h" "$DEPS/include/"

# OpenSSL: a target for this SDK, no poll.h, no socketpair() and no
# getaddrinfo() in ABIv11 bsdsocket.library, socket I/O through bsdsocket's
# own calls (socket numbers clash with C library files there), and
# jitterentropy as the seed source. See the patch.
S="$D/openssl-4.0.1"
if [ ! -d "$S" ]; then
    tar -C "$D" -xzf "$DL/openssl-4.0.1.tar.gz"
    patch -d "$S" -p1 -s < patches/openssl-4.0.1-abiv11.diff
    patch -d "$S" -p1 -s < patches/openssl-4.0.1-abiv0-i386-target.diff
fi
B="$O/openssl"; rm -rf "$B"; mkdir -p "$B"
# OpenSSL compiles its directories and compiler flags into the library, so
# they must not be host paths: the prefix is /Python (the install goes to a
# staging directory and the libraries are copied to $DEPS), and the include
# path is given through CPATH rather than -I.
DEST="$WORK/openssl-dest"; rm -rf "$DEST"
# abiv0compat.h: struct sockaddr_storage, which this SDK lacks.
( cd "$B" && CPATH="$DEPS/include" AROS_CFLAGS="-O2 -include $DEPS/include/abiv0compat.h" LDFLAGS="-L$DEPS/lib" \
    "$S/Configure" aros-abiv0-i386 threads no-ssl3 no-asm no-shared no-tests \
        no-apps no-docs no-dso --with-rand-seed=getrandom \
        --prefix=/Python --libdir=lib --openssldir=/Python/ssl \
  && "$MAKE" -j2 build_libs && "$MAKE" install_dev DESTDIR="$DEST" )
rm -rf "$DEPS/include/openssl"
cp -R "$DEST/Python/include/openssl" "$DEPS/include/"
cp "$DEST/Python/lib/libssl.a" "$DEST/Python/lib/libcrypto.a" "$DEPS/lib/"

# liblzma: library only, no threads (the lzma module does not use them).
X="$D/xz-5.8.3"
[ -d "$X" ] || tar -C "$D" -xzf "$DL/xz-5.8.3.tar.gz"
B="$O/xz"; rm -rf "$B"; mkdir -p "$B"
( cd "$B" && CFLAGS="-O2" "$X/configure" --host=i386-aros \
    --build="$(sh "$X/build-aux/config.guess")" \
    --prefix="$DEPS" --disable-shared --enable-static --disable-threads \
    --disable-xz --disable-xzdec --disable-lzmadec --disable-lzmainfo \
    --disable-lzma-links --disable-scripts --disable-doc --disable-nls \
    --disable-microlzma --disable-lzip-decoder \
  && "$MAKE" -j2 -C src/liblzma && "$MAKE" -C src/liblzma install )
echo "dependencies in $DEPS"
