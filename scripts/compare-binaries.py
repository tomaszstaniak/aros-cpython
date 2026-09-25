#!/usr/bin/env python3
"""compare-binaries.py A B - compare two AROS ELF executables function by
function and data object by data object.

An AROS executable is a relocatable ELF: code and data keep their
relocations. Every function (FUNC symbol in .text) and data object (OBJECT
symbol in .data) of A is compared with the symbol of the same name in B, byte
for byte, except the bytes that relocations fill in. The linked sections as a
whole are not compared: one object of a different size shifts everything
after it.

Prints the symbols that differ or exist in only one binary, and a summary.
Exit 0 when everything outside ALLOWED is equal. ALLOWED is the build
information (version stamp), which differs by design."""
import struct, sys

ALLOWED = {'Py_GetBuildInfo', '_Py_gitversion', '_Py_gitidentifier'}

def load(path):
    d = open(path, 'rb').read()
    assert d[:4] == b'\x7fELF' and d[4] == 2 and d[5] == 1, path
    shoff, = struct.unpack_from('<Q', d, 0x28)
    se, sn, si = struct.unpack_from('<HHH', d, 0x3a)
    hs = [struct.unpack_from('<IIQQQQIIQQ', d, shoff + i * se) for i in range(sn)]
    def name(off, tab):
        o = hs[tab][4] + off
        return d[o:d.index(0, o)].decode()
    names = [name(h[0], si) for h in hs]
    masks = {}
    for h in hs:
        if h[1] == 4:                            # SHT_RELA
            m = masks.setdefault(h[7], set())
            for k in range(h[5] // 24):
                off, info, _ = struct.unpack_from('<QQq', d, h[4] + k * 24)
                width = 4 if (info & 0xffffffff) in (2, 4, 9, 10, 11) else 8
                m.update(range(off, off + width))
    sh = hs[names.index('.symtab')]
    syms = {}
    for k in range(sh[5] // 24):
        nm, info, other, shndx, value, size = struct.unpack_from('<IBBHQQ', d, sh[4] + k * 24)
        if (info & 0xf) not in (1, 2) or shndx == 0 or shndx >= 0xff00 or size == 0:
            continue
        if names[shndx] not in ('.text', '.data'):
            continue
        sec = hs[shndx]
        mask = masks.get(shndx, set())
        body = bytearray(d[sec[4] + value: sec[4] + value + size])
        for j in range(size):
            if value + j in mask:
                body[j] = 0
        syms.setdefault(name(nm, sh[6]), []).append(bytes(body))
    return syms

a, b = load(sys.argv[1]), load(sys.argv[2])
bad = []
for n in sorted(set(a) | set(b)):
    if a.get(n) != b.get(n):
        where = 'only in A' if n not in b else 'only in B' if n not in a else 'differs'
        print(f"{where:9} {n}{'  (allowed)' if n in ALLOWED else ''}")
        if n not in ALLOWED:
            bad.append(n)
same = sum(1 for n in a if a.get(n) == b.get(n))
print(f"{same} of {len(a)} symbols equal; {len(bad)} unexpected differences")
sys.exit(1 if bad else 0)
