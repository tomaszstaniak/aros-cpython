# compress11.py - zlib, gzip, bz2, lzma, zipfile, tarfile round trips.
import zlib, gzip, bz2, lzma, zipfile, tarfile, io, os
data = (b"AROS ABIv11 " * 5000) + os.urandom(3000)
def rt(name, fn):
    try:
        print("Z %-8s %s" % (name, "PASS" if fn() else "FAIL"), flush=True)
    except BaseException as e:
        print("Z %-8s FAIL %s: %s" % (name, type(e).__name__, e), flush=True)
rt("zlib", lambda: zlib.decompress(zlib.compress(data, 9)) == data)
rt("gzip", lambda: gzip.decompress(gzip.compress(data)) == data)
rt("bz2", lambda: bz2.decompress(bz2.compress(data)) == data)
rt("lzma", lambda: lzma.decompress(lzma.compress(data)) == data)
rt("lzma-alone", lambda: lzma.decompress(lzma.compress(data, format=lzma.FORMAT_ALONE)) == data)
def z():
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w", zipfile.ZIP_DEFLATED) as f:
        f.writestr("a.bin", data)
        f.writestr("b.txt", "zażółć")
    with zipfile.ZipFile(io.BytesIO(b.getvalue())) as f:
        return f.read("a.bin") == data and f.read("b.txt").decode() == "zażółć" and f.testzip() is None
rt("zipfile", z)
def t(mode):
    b = io.BytesIO()
    with tarfile.open(fileobj=b, mode="w:" + mode) as f:
        ti = tarfile.TarInfo("a.bin"); ti.size = len(data)
        f.addfile(ti, io.BytesIO(data))
    with tarfile.open(fileobj=io.BytesIO(b.getvalue()), mode="r:" + mode) as f:
        return f.extractfile("a.bin").read() == data
for m in ("gz", "bz2", "xz"):
    rt("tar." + m, lambda m=m: t(m))
print("Z-END", flush=True)
