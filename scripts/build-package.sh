#!/bin/zsh
# build-package.sh [INTERPRETER] - assemble the package into $WORK/dist:
#   aros-cpython-$PY_VER-abiv11-$PORT_VER.tar.gz, .zip and .lha,
#   a .sha256 for each, CHECKSUMS.txt and MANIFEST.txt.
#
# INTERPRETER defaults to $BUILD_DIR/python.exe; the package gets it with
# the debug information removed. With RELEASE=1 the SHA-256 of that packaged
# file must equal interpreter_sha256 in package/interpreter-provenance.txt;
# without it, the SHA-256 of the packaged binary is written into the
# package's copy of that file, so a local build is never labelled as the
# release. The standard library comes from `make install` ($WORK/install).
# Needs an LhA that can create archives (jca02266's LHa); set LHA.
set -e
cd "$(dirname "$0")/.."
. scripts/env.sh
NAME=aros-cpython-$PY_VER-abiv11-$PORT_VER
INTERP="${1:-$BUILD_DIR/python.exe}"
STDLIB="$WORK/install/Python/lib/python3.14"
DL="$WORK/downloads"
PIPWHL="$SRC/Lib/ensurepip/_bundled/pip-26.2.1-py3-none-any.whl"
LHA="${LHA:-$(command -v lha || true)}"
for f in "$INTERP" "$STDLIB" "$PIPWHL" "$DL/pyfiglet-1.0.4-py3-none-any.whl" \
         "$DL/cacert-2026-08-13.pem" "$SRC/LICENSE"; do
  [ -e "$f" ] || { echo "missing: $f" >&2; exit 2; }
done
if [ "$LHA" != none ]; then
  "$LHA" --version 2>&1 | grep -q "LHa for UNIX" || { echo "set LHA to jca02266's LHa, or LHA=none for ZIP/tar.gz" >&2; exit 2; }
fi

REC=$(grep '^interpreter_sha256=' package/interpreter-provenance.txt | cut -d= -f2)

OUT="$WORK/dist"; STAGE="$OUT/.stage"
rm -rf "$STAGE"; mkdir -p "$STAGE"
T="$STAGE/$NAME"; P="$T/Python"
mkdir -p "$P/lib" "$P/S" "$P/demo" "$P/tests" "$P/wheels" "$P/ssl"
# --strip-debug only: a full strip makes AROS load the program without
# applying its relocations. Stripping twice changes nothing, so the release
# binary (already stripped) passes through unchanged.
x86_64-aros-strip --strip-debug -o "$P/python" "$INTERP"
PYSHA=$(shasum -a 256 "$P/python" | awk '{print $1}')
cp -R "$STDLIB" "$P/lib/python3.14"
# sysconfig records configure's flags and directories, and the JSON file
# (a build-time snapshot for tools) also the build user's home directory;
# replace the host paths with the names the compiler wrappers use, and ~.
for f in "$P"/lib/python3.14/_sysconfigdata__*.py "$P"/lib/python3.14/_sysconfig_vars__*.json; do
  sed -i.bak -e "s|$WORK|/work|g" -e "s|$REPO|/src|g" -e "s|$HOME|~|g" "$f" && rm "$f.bak"
done
# Not needed or not usable here: the test suite, IDLE, turtle demos,
# bytecode caches, and config-3.14-* (headers and the static library for
# building C extensions, which AROS cannot load).
find "$P/lib/python3.14" -depth -type d \
     \( -name test -o -name tests -o -name idlelib -o -name turtledemo -o -name __pycache__ \) \
     -exec rm -rf {} +
rm -rf "$P/lib/python3.14"/config-3.14-*
mkdir -p "$P/lib/python3.14/site-packages"
( cd "$P/lib/python3.14/site-packages" && unzip -q "$PIPWHL" \
  && patch -p0 -s < "$REPO/patches/pip-26.2.1-without-mmap.diff" )
cp package/S/python package/S/python-startup "$P/S/"
cp "$DL/cacert-2026-08-13.pem" "$P/ssl/ca-bundle.crt"
cp package/tests/*.py "$P/tests/"
cp tests/guest/thread_ident11.py "$P/tests/"
cp package/demo/*.py "$P/demo/"
cp "$DL/pyfiglet-1.0.4-py3-none-any.whl" "$P/wheels/"
cp "$SRC/LICENSE" "$P/LICENSE"
cp package/THIRD-PARTY-NOTICES.txt "$P/"
cp -R package/licenses "$P/licenses"
cp package/README.txt package/ACCEPTANCE.txt patches/pip-26.2.1-without-mmap.diff "$T/"
if [ "$RELEASE" = 1 ] && [ "$PYSHA" != "$REC" ]; then
  echo "RELEASE=1 but the interpreter is $PYSHA, not $REC" >&2; exit 2
fi
sed "s/^interpreter_sha256=.*/interpreter_sha256=$PYSHA/" package/interpreter-provenance.txt \
    > "$T/interpreter-provenance.txt"
[ "$PYSHA" = "$REC" ] || echo "local_build=yes; this interpreter is not the release binary $REC" >> "$T/interpreter-provenance.txt"

xattr -rc "$STAGE" 2>/dev/null || true
find "$STAGE" \( -name '._*' -o -name '.DS_Store' \) -delete
[ -z "$(find "$STAGE" -type l)" ] || { echo "symbolic links in staging" >&2; exit 3; }
( cd "$T" && find . -type f ! -name MANIFEST.txt | LC_ALL=C sort | while read -r f; do
    shasum -a 256 "$f"; done ) > "$T/MANIFEST.txt"

# Reproducible archives: every file dated SOURCE_DATE_EPOCH, members in
# sorted order, no owner names, and gzip without its own time stamp.
"$BUILD_PYTHON" - "$STAGE" "$SOURCE_DATE_EPOCH" "$OUT/$NAME.zip" <<'EOF'
import os, sys, zipfile, time
root, t = sys.argv[1], int(sys.argv[2])
for d, dirs, files in os.walk(root):
    for n in dirs + files:
        os.utime(os.path.join(d, n), (t, t), follow_symlinks=False)
os.utime(root, (t, t))
with zipfile.ZipFile(sys.argv[3], 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for d, dirs, files in os.walk(root):
        dirs.sort()
        for n in sorted(files):
            path = os.path.join(d, n)
            info = zipfile.ZipInfo(os.path.relpath(path, root), time.gmtime(t)[:6])
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = os.stat(path).st_mode << 16
            with open(path, 'rb') as f:
                z.writestr(info, f.read())
EOF
cd "$STAGE"
rm -f "$OUT/$NAME.lha" "$OUT/$NAME.lha.sha256" "$OUT/$NAME.tar.gz"
find "$NAME" -type f | LC_ALL=C sort > "$OUT/.files"
if [ "$LHA" != none ]; then
  xargs "$LHA" a "$OUT/$NAME.lha" < "$OUT/.files" >/dev/null
fi
find "$NAME" | LC_ALL=C sort > "$OUT/.members"
COPYFILE_DISABLE=1 tar --no-xattrs --uid 0 --gid 0 --uname "" --gname "" \
    -n -cf - -T "$OUT/.members" | gzip -n -9 > "$OUT/$NAME.tar.gz"
rm -f "$OUT/.files" "$OUT/.members"
cp "$T/MANIFEST.txt" "$OUT/MANIFEST.txt"
cd "$OUT"
: > CHECKSUMS.txt
ARCHIVES=("$NAME.tar.gz" "$NAME.zip" MANIFEST.txt)
[ "$LHA" = none ] || ARCHIVES+=("$NAME.lha")
for a in "${ARCHIVES[@]}"; do
  shasum -a 256 "$a" | tee "$a.sha256" >> CHECKSUMS.txt
done
rm -rf "$STAGE"
echo "interpreter $PYSHA"; cat CHECKSUMS.txt
