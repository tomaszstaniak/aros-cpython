"""HTTPS with certificate verification, using only the standard library."""
import ssl, urllib.request
ctx = ssl.create_default_context()        # verifies the server certificate
r = urllib.request.urlopen("https://example.com", timeout=30, context=ctx)
# The TLS version has to be read BEFORE the body: at end of file the response
# closes its fp, and r.fp is then None.
raw = getattr(getattr(r, "fp", None), "raw", None)
sock = getattr(raw, "_sock", None)
tls = sock.version() if sock is not None else "ok"
print("status:", r.status)
print("bytes :", len(r.read()))
print("TLS   :", tls)
