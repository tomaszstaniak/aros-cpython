# instchk.py MANIFEST OUT - compare the installed /Python with the release's
# MANIFEST.txt (SHA-256 of every file in the package), so that a test report
# can say which files it ran against. Files not in the MANIFEST (the test
# suite added for these runs, __pycache__, pip-installed packages) are listed
# as extra.
import os, sys, hashlib

manifest, out = sys.argv[1], sys.argv[2]
want = {}
for line in open(manifest, encoding="utf-8"):
    h, p = line.rstrip("\n").split("  ", 1)
    if p.startswith("./Python/"):
        want["/Python/" + p[len("./Python/"):]] = h
ok = bad = 0
missing, badlist, extra = [], [], 0
seen = set()
for root, dirs, files in os.walk("/Python"):
    for f in files:
        p = os.path.join(root, f)
        seen.add(p)
        if p not in want:
            extra += 1
            continue
        h = hashlib.sha256()
        with open(p, "rb") as fh:
            for b in iter(lambda: fh.read(1 << 20), b""):
                h.update(b)
        if h.hexdigest() == want[p]:
            ok += 1
        else:
            bad += 1
            badlist.append(p)
missing = sorted(set(want) - seen)
with open(out, "w") as o:
    o.write("INSTCHK manifest=%d ok=%d bad=%d missing=%d extra=%d\n"
            % (len(want), ok, bad, len(missing), extra))
    for p in badlist:
        o.write("BAD %s\n" % p)
    for p in missing:
        o.write("MISSING %s\n" % p)
    o.write("INSTCHK-END\n")
