# Identifiers as the running guest reports them, and the interpreter's identity.
import sys, os, sysconfig, hashlib, platform
print("sys.platform      ", sys.platform)
print("os.uname          ", tuple(os.uname()))
print("get_platform      ", sysconfig.get_platform())
for k in ("AROS_ABI", "MULTIARCH", "SOABI", "EXT_SUFFIX", "HOST_GNU_TYPE", "LIBPL"):
    print(f"{k:18}", sysconfig.get_config_var(k))
print("sysconfigdata     ", sysconfig._get_sysconfigdata_name())
from pip._vendor.packaging import tags
t = list(tags.sys_tags())
print("pip tags          ", len(t), [str(x) for x in t[:3]])
print("pip platform tags ", sorted({x.platform for x in t}))
try:
    print("ENV:ABI           ", open("/ENV/ABI").read().strip())
except OSError as e:
    print("ENV:ABI           ", "unreadable:", e)
h = hashlib.sha256(open(sys.executable, "rb").read()).hexdigest()
print("executable        ", sys.executable, os.path.getsize(sys.executable))
print("sha256            ", h)
print("IDPROBE-END")
