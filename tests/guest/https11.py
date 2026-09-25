# https11.py - HTTPS with certificate verification, and the refusals that
# verification must produce.
import ssl, socket, urllib.request, urllib.error
ctx = ssl.create_default_context()
print("H openssl  ", ssl.OPENSSL_VERSION, "cafile", ssl.get_default_verify_paths().cafile, flush=True)
def get(url):
    with urllib.request.urlopen(url, timeout=60, context=ctx) as u:
        return u.status, len(u.read())
def ok(name, url):
    try:
        print("H %-10s PASS %s" % (name, get(url)), flush=True)
    except BaseException as e:
        print("H %-10s FAIL %s: %s" % (name, type(e).__name__, e), flush=True)
def refused(name, url):
    try:
        r = get(url)
        print("H %-10s FAIL accepted %s" % (name, r), flush=True)
    except BaseException as e:
        cause = getattr(e, "reason", e)
        good = isinstance(cause, ssl.SSLCertVerificationError)
        print("H %-10s %s %s: %s" % (name, "PASS refused" if good else "FAIL other", type(cause).__name__, str(cause)[:80]), flush=True)
ok("pypi", "https://pypi.org/simple/pip/")
ok("python", "https://www.python.org/")
refused("expired", "https://expired.badssl.com/")
refused("wronghost", "https://wrong.host.badssl.com/")
refused("selfsigned", "https://self-signed.badssl.com/")
print("H-END", flush=True)
