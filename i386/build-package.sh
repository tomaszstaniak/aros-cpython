#!/bin/bash
# build-package.sh - assemble the i386 ABIv0 package on a Linux host:
#   aros-cpython-3.14.7-abiv0-0.1.0.tar.gz and .lha (same content),
#   a .sha256 for each, CHECKSUMS.txt and MANIFEST.txt, in $OUT.
#
# Inputs (environment):
#   INTERP   the interpreter, already stripped with
#            i386-aros-strip --strip-debug (the build container has it)
#   INSTALL  the `make install` tree (the directory that holds Python/)
#   DL       downloads: pyfiglet wheel and cacert-2026-08-13.pem
#            (checked against sources-abiv11.txt)
#   LHA      jca02266's LHa for UNIX (Lhasa cannot create archives)
#   OUT      output directory (default ./dist)
#   RELEASE=1  refuse an interpreter whose SHA-256 differs from
#            interpreter_sha256 in package/interpreter-provenance.txt
# The package files that differ from x86_64 live in i386/package/; the
# self-tests, demos, notices and licenses are shared with package/.
set -euo pipefail
cd "$(dirname "$0")/.."
REPO=$PWD
NAME=aros-cpython-3.14.7-abiv0-0.1.0
: "${INTERP:?}" "${INSTALL:?}" "${DL:?}" "${LHA:?}"
OUT=$(realpath -m "${OUT:-dist}")
STDLIB="$INSTALL/Python/lib/python3.14"
PIPWHL=$(ls "$STDLIB"/ensurepip/_bundled/pip-26.2.1-py3-none-any.whl)
SOURCE_DATE_EPOCH=1790294400
for f in "$INTERP" "$STDLIB" "$PIPWHL" "$DL/pyfiglet-1.0.4-py3-none-any.whl" \
         "$DL/cacert-2026-08-13.pem"; do
  [ -e "$f" ] || { echo "missing: $f" >&2; exit 2; }
done
"$LHA" --version 2>&1 | grep -q "LHa for UNIX" || { echo "LHA must be jca02266's LHa" >&2; exit 2; }
for f in pyfiglet-1.0.4-py3-none-any.whl cacert-2026-08-13.pem; do
  want=$(awk -v f="$f" '$1 == f {print $2}' i386/sources-abiv11.txt)
  echo "$want  $DL/$f" | sha256sum -c --quiet -
done

REC=$(grep '^interpreter_sha256=' i386/package/interpreter-provenance.txt | cut -d= -f2)
STAGE="$OUT/.stage"; rm -rf "$STAGE"; mkdir -p "$STAGE"
T="$STAGE/$NAME"; P="$T/Python"
mkdir -p "$P/lib" "$P/S" "$P/demo" "$P/tests" "$P/wheels" "$P/ssl"
cp "$INTERP" "$P/python"
PYSHA=$(sha256sum "$P/python" | awk '{print $1}')
if [ "${RELEASE:-0}" = 1 ] && [ "$PYSHA" != "$REC" ]; then
  echo "RELEASE=1 but the interpreter is $PYSHA, not $REC" >&2; exit 2
fi
cp -R "$STDLIB" "$P/lib/python3.14"
# sysconfig records the build's directories; the container's are /work/py
# (sources and builds) and /i386 (this tree). Name them as the x86_64
# package does.
for f in "$P"/lib/python3.14/_sysconfigdata__*.py "$P"/lib/python3.14/_sysconfig_vars__*.json; do
  sed -i -e "s|/work/py|/work|g" -e "s|/i386|/src|g" "$f"
done
# Left out, as in the x86_64 package: the test suite, IDLE, turtle demos,
# bytecode caches, and config-3.14-* (headers and the static library for
# building C extensions, which AROS cannot load).
find "$P/lib/python3.14" -depth -type d \
     \( -name test -o -name tests -o -name idlelib -o -name turtledemo -o -name __pycache__ \) \
     -exec rm -rf {} +
rm -rf "$P/lib/python3.14"/config-3.14-*
mkdir -p "$P/lib/python3.14/site-packages"
( cd "$P/lib/python3.14/site-packages" && unzip -q "$PIPWHL" \
  && patch -p0 -s < "$REPO/patches/pip-26.2.1-without-mmap.diff" )
cp i386/package/S/python i386/package/S/python-startup "$P/S/"
cp "$DL/cacert-2026-08-13.pem" "$P/ssl/ca-bundle.crt"
cp package/tests/*.py "$P/tests/"
cp package/demo/*.py "$P/demo/"
cp "$DL/pyfiglet-1.0.4-py3-none-any.whl" "$P/wheels/"
cp "$STDLIB/LICENSE.txt" "$P/LICENSE"
# Notices and license texts: the shared ones, minus SQLite (not in the i386
# build), plus zlib and bzip2 (linked in statically on ABIv0), with the i386
# versions of the two summary files.
cp i386/package/THIRD-PARTY-NOTICES.txt "$P/"
cp -R package/licenses "$P/licenses"
rm "$P/licenses/LICENSE.sqlite-3.48.0.txt"
cp i386/package/licenses/* "$P/licenses/"
cp i386/package/README.txt "$T/"
[ -f i386/package/ACCEPTANCE.txt ] && cp i386/package/ACCEPTANCE.txt "$T/"
cp patches/pip-26.2.1-without-mmap.diff "$T/"
sed "s/^interpreter_sha256=.*/interpreter_sha256=$PYSHA/" i386/package/interpreter-provenance.txt \
    > "$T/interpreter-provenance.txt"
[ "$PYSHA" = "$REC" ] || echo "local_build=yes; this interpreter is not the tested binary $REC" >> "$T/interpreter-provenance.txt"

[ -z "$(find "$STAGE" -type l)" ] || { echo "symbolic links in staging" >&2; exit 3; }
( cd "$T" && find . -type f ! -name MANIFEST.txt | LC_ALL=C sort | while read -r f; do
    sha256sum "$f"; done ) > "$T/MANIFEST.txt"

# Reproducible archives: every file dated SOURCE_DATE_EPOCH, members in
# sorted order, no owner names, gzip without its own time stamp.
find "$STAGE" -exec touch -h -d "@$SOURCE_DATE_EPOCH" {} +
cd "$STAGE"
rm -f "$OUT/$NAME.lha" "$OUT/$NAME.tar.gz"
find "$NAME" -type f | LC_ALL=C sort > "$OUT/.files"
xargs "$LHA" a "$OUT/$NAME.lha" < "$OUT/.files" >/dev/null
find "$NAME" | LC_ALL=C sort > "$OUT/.members"
tar --no-xattrs --owner 0 --group 0 --numeric-owner --no-recursion \
    -cf - -T "$OUT/.members" | gzip -n -9 > "$OUT/$NAME.tar.gz"
rm -f "$OUT/.files" "$OUT/.members"
cp "$T/MANIFEST.txt" "$OUT/MANIFEST.txt"
cd "$OUT"
: > CHECKSUMS.txt
for a in "$NAME.tar.gz" "$NAME.lha" MANIFEST.txt; do
  sha256sum "$a" | tee "$a.sha256" >> CHECKSUMS.txt
done
rm -rf "$STAGE"
echo "interpreter $PYSHA"; cat CHECKSUMS.txt
