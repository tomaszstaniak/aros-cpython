# Build host for the AROS ABIv0 (i386) cross toolchain and system.
# Debian 12 gives GCC 12 as the host compiler; GCC 6.5.0 (the ABIv0
# default) is built with it as C++98, while Apple clang produces a cc1 that crashes
# at random (measured: 1 in 60 compiles of the same file).
FROM debian@sha256:f37a335e82bca302e955fa39f9dfe28f1be618f016f8a2b56318e5a5111afc26
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential git bison flex gawk python3 python3-mako bzip2 xz-utils \
      netpbm libpng-dev zlib1g-dev autoconf automake libtool wget curl ca-certificates \
      cmake gperf texinfo patch unzip zip file cpio genisoimage \
 && rm -rf /var/lib/apt/lists/*
