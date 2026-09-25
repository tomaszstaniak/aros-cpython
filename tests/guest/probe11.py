# probe11.py TAG - one pass over the things the ABIv11 port has to do.
# One line per step, PASS/FAIL/INFO, then "P11-END TAG <passes>/<steps>".
# A missing END line means the run did not finish.
import sys, os, time, json, traceback

TAG = sys.argv[1] if len(sys.argv) > 1 else "?"
steps, passes = 0, 0
print("P11-START", TAG, flush=True)

def step(name, fn):
    global steps, passes
    steps += 1
    t0 = time.time()
    try:
        r = fn()
        passes += 1
        print("P %-10s PASS %s (%.1fs)" % (name, r, time.time() - t0), flush=True)
    except BaseException as e:
        print("P %-10s FAIL %s: %s" % (name, type(e).__name__, str(e).splitlines()[0][:70] if str(e) else ""), flush=True)

def files():
    p = "/RAM/p11.json"
    json.dump({"a": list(range(100)), "s": "zazółć"}, open(p, "w"))
    d = json.load(open(p)); os.remove(p)
    assert d["a"][99] == 99 and d["s"] == "zazółć"
    return "json round trip"

def stat():
    st = os.stat("/Python/python")
    return "size %d" % st.st_size

def pwd_():
    import pwd
    try:
        return "entry %s" % pwd.getpwuid(os.getuid()).pw_name
    except KeyError:
        return "KeyError (no user db)"

def urandom():
    t0 = time.time(); a = os.urandom(32); t1 = time.time(); b = os.urandom(32); t2 = time.time()
    import secrets
    assert a != b and len(set(a)) > 8
    return "first %.2fs, next %.3fs, token %s" % (t1 - t0, t2 - t1, secrets.token_hex(4))

def zlib_():
    import zlib, gzip
    d = bytes(range(256)) + bytes(1000)
    assert zlib.decompress(zlib.compress(d)) == d and gzip.decompress(gzip.compress(d)) == d
    return "zlib %s" % zlib.ZLIB_VERSION

def bz2_():
    import bz2
    d = b"abc" + bytes(5000)
    assert bz2.decompress(bz2.compress(d)) == d
    return "round trip"

def lzma_():
    import lzma
    d = b"abc" + bytes(5000)
    assert lzma.decompress(lzma.compress(d)) == d
    return "round trip"

def https():
    import ssl, urllib.request
    ctx = ssl.create_default_context(cafile="/Python/ssl/ca-bundle.crt")
    with urllib.request.urlopen("https://pypi.org/simple/pip/", timeout=60, context=ctx) as u:
        body = u.read()
    return "status %d, %d bytes, %s" % (u.status, len(body), ssl.OPENSSL_VERSION)

def pip_():
    from pip._internal.cli.main import main as pip_main
    try:
        rc = pip_main(["--version"])
    except SystemExit as e:
        rc = e.code
    assert rc in (0, None)
    return "pip --version rc %s" % rc

def worker_socket():
    import threading, socket
    out = {}
    def w():
        try:
            s = socket.create_connection(("pypi.org", 80), timeout=30)
            s.sendall(b"HEAD / HTTP/1.0\r\nHost: pypi.org\r\n\r\n")
            out["r"] = s.recv(64).split(b"\r\n")[0].decode()
            s.close()
        except BaseException as e:
            out["r"] = "%s: %s" % (type(e).__name__, e)
    t = threading.Thread(target=w); t.start(); t.join(60)
    assert not t.is_alive() and out.get("r", "").startswith("HTTP/"), out.get("r")
    return out["r"]

for n, f in [("files", files), ("stat", stat), ("pwd", pwd_), ("urandom", urandom),
             ("zlib", zlib_), ("bz2", bz2_), ("lzma", lzma_), ("https", https),
             ("pip", pip_), ("worker-sock", worker_socket)]:
    step(n, f)
print("P11-END %s %d/%d" % (TAG, passes, steps), flush=True)
