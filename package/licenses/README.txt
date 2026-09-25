License texts for components in this release (ABIv11)
=====================================================

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
SQLite 3.48.0       (sqlite3)                      blessing        LICENSE.sqlite-3.48.0.txt
Expat 2.8.2         (pyexpat, xml.parsers)         MIT             LICENSE.expat-2.8.2.txt
mpdecimal           (_decimal)                     BSD-2-Clause    LICENSE.mpdecimal.txt
HACL*               (hashlib primitives)           MIT             LICENSE.HACL.txt
CA bundle           (Python/ssl/ca-bundle.crt)     MPL-2.0         LICENSE.ca-bundle.txt

The OpenSSL, jitterentropy and xz texts are copied verbatim from the source
archives that were compiled for this build; Expat's from CPython 3.14.7's
Modules/expat/COPYING; mpdecimal's and HACL*'s from the header blocks in the
CPython 3.14.7 source; SQLite's from the header of the SDK's sqlite3.h.

Not in this folder (licensed elsewhere):
  - Python 3.14.7 itself        -> ../LICENSE (PSF License Agreement)
  - pip 26.2.1                  -> lib/python3.14/site-packages/pip-26.2.1.dist-info/licenses/
  - pyfiglet 1.0.4              -> inside wheels/pyfiglet-1.0.4-py3-none-any.whl
  - zlib, bzip2, the C runtime  -> AROS system libraries, not bundled here
