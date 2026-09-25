# Building

The release was built on macOS 27 (arm64). Nothing in the scripts depends
on macOS except the default GNU make lookup; other Unix hosts were not tried.

## Host requirements

| Tool | Why |
|---|---|
| x86_64-aros GCC 10.5.0 (see below) | the cross compiler; set `AROS_TOOLCHAIN` to its directory |
| Python 3.14 | CPython's cross build runs a host interpreter of the same version (`BUILD_PYTHON`, default `python3.14` on `PATH`) |
| GNU make 4 | CPython and OpenSSL; set `MAKE` if it is not `gmake` or `make` |
| perl | OpenSSL's `Configure` |
| curl, shasum, unzip, patch, tar with xz | fetching and unpacking |
| LhA that can create archives (jca02266's LHa, as used by AROS) | the `.lha` package; set `LHA`. Lhasa only extracts. |

## The cross compiler

GCC 10.5.0 is the default compiler of ABIv11. The ABIv11 2026.09 release
ships an SDK but no host compiler, so build it from the release tag with the
AROS build system:

```sh
git clone https://github.com/deadwood2/AROS.git
git -C AROS checkout ABIv11_2026.09
mkdir build && cd build
../AROS/configure --target=pc-x86_64 \
    --with-aros-toolchain-install=$HOME/aros-toolchain \
    --with-portssources=$HOME/aros-portssources
make crosstools
export AROS_TOOLCHAIN=$HOME/aros-toolchain
```

On macOS the AROS build needs a case-sensitive file system and GNU tools
first on `PATH` (GNU make, gsed, bison, flex). The release binary was built
with a compiler made this way from commit 5376f09b of that repository, whose
`tools/crosstools` is identical to the one at `ABIv11_2026.09`.

The compiler is used with `--sysroot` pointing at the 2026.09 SDK
(`scripts/bin/aros-v11-gcc`), so every link archive comes from that SDK and
only `libgcc` from the compiler.

## Steps

From the repository root:

```sh
export AROS_TOOLCHAIN=...          # directory with x86_64-aros-gcc
scripts/fetch-sources.sh           # work/downloads, work/sdk
scripts/prepare-source.sh          # work/src/Python-3.14.7, patched
scripts/build-deps.sh              # work/deps: OpenSSL, jitterentropy, liblzma
scripts/configure.sh               # work/build
scripts/build.sh                   # work/build/python.exe, work/install
scripts/build-package.sh           # work/dist
```

`fetch-sources.sh` checks every download against `sources.txt` and stops on
a mismatch. `WORK` moves the whole working tree elsewhere.

## Reproducible build

The build fixes its time (`SOURCE_DATE_EPOCH` in `scripts/env.sh`) and keeps
host paths out of the binaries (`-ffile-prefix-map` in the compiler
wrappers, a relative source directory, OpenSSL installed from a staging
prefix). Two builds from fresh clones in different directories gave the same
interpreter and the same archives:

| File | SHA-256 |
|---|---|
| `Python/python` (debug information removed) | `6cdd0f6072c58dd5b63c5f977400ba60bfb820b03afc9e4daa2728b9cb1ebe48` |
| `aros-cpython-3.14.7-abiv11-0.1.0.tar.gz` | see the release page |

A different compiler build or SDK gives a different file. The code can
still be compared with the release binary function by function, which
masks the bytes that relocations fill in:

```sh
python3 scripts/compare-binaries.py release/Python/python work/build/python.exe
```

`RELEASE=1 scripts/build-package.sh` refuses to package an interpreter
whose SHA-256 differs from `package/interpreter-provenance.txt`.

## Notes on the build

- `config/config.site` answers what configure cannot find out when
  cross-compiling; every entry has its reason. The socket functions are
  declared there because the ABIv11 socket calls are inline functions in
  `<proto/socket.h>`, which configure's own tests do not include.
- `scripts/bin/aros-v11-pkg-config` answers only for the OpenSSL and liblzma
  built by `build-deps.sh`, with full paths. The SDK has its own
  `libssl.a`/`libcrypto.a` (1.1.0h) and a `liblzma.a` that links to a
  decode-only system library, and the compiler searches the SDK before any
  `-L`.
- The ABIv11 headers declare several POSIX functions only when
  `__STRICT_ANSI__` is not defined, so the build uses `-std=gnu11`.
- `_locale` is built without gettext: the SDK's `libintl.a` and `libiconv.a`
  are GNU gettext and GNU libiconv (LGPL) and would be linked statically.
