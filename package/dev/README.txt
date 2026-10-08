CPython 3.14.7 development package - x86-64 AROS ABIv11
=====================================================

Companion to aros-cpython-3.14.7-abiv11-0.1.1. Requires the ABIv11
2026.09 SDK and a matching x86_64-aros toolchain (tested: GCC 10.5.0).
Do not mix with mainline ABIv1, i386 or other ABI builds.

This archive contains the public headers including the generated pyconfig.h,
libpython3.14.a, CPython's private static helper archives and the custom
OpenSSL 4.0.1, jitterentropy 3.7.0 and liblzma 5.8.3 archives. Debug information
is removed; link symbols and relocations are retained.

The remaining -l dependencies in link-dependencies.txt come from the matching
AROS SDK. Some SDK archives are stubs for AROS shared libraries; use the runtime
release's requirements and THIRD-PARTY-NOTICES.txt. The package does not replace
the AROS SDK. Licenses for bundled components are in licenses/.

Install the runtime package separately and assign Python: to its Python drawer.
An embedded interpreter needs the runtime's lib/python3.14 directory. The example
explicitly sets PyConfig.home to /Python; an application may instead use its own
installation path. The interpreter executable itself is not invoked by embedding.
Embedding also bypasses the executable's AROS startup hook: suppress DOS volume
requesters with pr_WindowPtr = (APTR)-1 while running Python, and restore the
previous value afterwards. See the example. Otherwise startup can wait forever
on a requester for a missing path such as pyvenv.cfg.

Cross-build the example (replace SDK, package and toolchain paths):

  cmake -S /path/to/dev/examples -B build-embed \
    -DCMAKE_SYSTEM_NAME=AROS \
    -DCMAKE_C_COMPILER=/path/to/toolchain/x86_64-aros-gcc \
    -DCMAKE_SYSROOT=/path/to/SDK-202609/Development \
    -DCMAKE_PREFIX_PATH=/path/to/dev
  cmake --build build-embed

AROSPython::Python includes all static module dependencies and -nix. Custom
archives are passed by full path: -lssl/-lcrypto/-llzma can select older SDK
libraries before the package's -L path. For direct compiler use:

  PKG_CONFIG_PATH=/path/to/dev/lib/pkgconfig \
    pkg-config --cflags --libs aros-python-3.14-embed

Use those flags after the application's objects/source in the linker command.
For upstream GemRB's FindPython, set Python_INCLUDE_DIR to include/python3.14
and Python_LIBRARY to lib/libpython3.14.a, enable STATIC_LINK, and also link the
AROSPython::Python target (or append the complete pkg-config linker flags).
Finding libpython alone does not supply the static module dependencies.
GemRB compilation and runtime compatibility are not verified by this package.

Run on AROS from a Shell with sufficient stack:

  Stack 1048576
  embed /Python >RAM:embed.log

Expected: EMBED PASS and FINALIZE PASS, exit code 0. The example registers a
builtin host module and checks JSON, Decimal, SHA-256, compression and SQLite.
It imports SSL and checks its version; it does not test TLS networking.
Dynamic extension loading is unchanged from the runtime release.

This companion matches runtime 0.1.1 (patches 0001-0023), including the
thread-ident correction used by faulthandler and pthread API calls.
