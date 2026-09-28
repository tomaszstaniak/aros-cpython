License texts for components in this release (i386 ABIv0)
=========================================================

This folder holds the full license texts for the third-party components that
are statically linked into the interpreter binary, and for the CA bundle. See
../THIRD-PARTY-NOTICES.txt for the summary and for components licensed
elsewhere (Python itself, system libraries, bundled Python packages).

Component                                          SPDX            Text file
----------------------------------------------------------------------------
OpenSSL 4.0.1       (_ssl, _hashlib)               Apache-2.0      LICENSE.OpenSSL-4.0.1.txt
jitterentropy 3.7.0 (random seed source)           BSD-3-Clause    LICENSE.jitterentropy-3.7.0.txt
                                                   or GPL-2.0
xz / liblzma 5.8.3  (lzma)                         0BSD            LICENSE.xz-liblzma-5.8.3.txt
Expat 2.8.2         (pyexpat, xml.parsers)         MIT             LICENSE.expat-2.8.2.txt
mpdecimal           (_decimal)                     BSD-2-Clause    LICENSE.mpdecimal.txt
HACL*               (hashlib primitives)           MIT             LICENSE.HACL.txt
zlib 1.2.13         (zlib, gzip)                   Zlib            LICENSE.zlib-1.2.13.txt
bzip2 1.0.6         (bz2)                          bzip2-1.0.6     LICENSE.bzip2-1.0.6.txt
CA bundle           (Python/ssl/ca-bundle.crt)     MPL-2.0         LICENSE.ca-bundle.txt

The OpenSSL, jitterentropy and xz texts are copied verbatim from the source
archives that were compiled for this build; Expat's from CPython 3.14.7's
Modules/expat/COPYING; mpdecimal's and HACL*'s from the header blocks in the
CPython 3.14.7 source; zlib's from the header of the ABIv0 SDK's zlib.h;
bzip2's is the LICENSE file of bzip2 1.0.6 (sourceware.org bzip2.git, tag
bzip2-1.0.6), the version the SDK's bzlib.h names.

Not in this folder (licensed elsewhere):
  - Python 3.14.7 itself        -> ../LICENSE (PSF License Agreement)
  - pip 26.2.1                  -> lib/python3.14/site-packages/pip-26.2.1.dist-info/licenses/
  - pyfiglet 1.0.4              -> inside wheels/pyfiglet-1.0.4-py3-none-any.whl
  - the C runtime, bsdsocket    -> AROS system libraries, not bundled here
