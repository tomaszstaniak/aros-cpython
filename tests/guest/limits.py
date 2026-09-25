# Indirect users of subprocess and process creation on AROS: what each one
# does, and how readable its failure is. One line per case:
#   L <case> OK <detail>  |  L <case> ERR <exception type>: <first line>
# Every case runs in its own try block, so one failure does not hide the rest.
import sys, os, traceback, tempfile

def case(name, fn):
    try:
        r = fn()
        print(f"L {name:14} OK  {str(r)[:90]}", flush=True)
    except BaseException as e:
        msg = str(e).splitlines()[0] if str(e) else ""
        print(f"L {name:14} ERR {type(e).__name__}: {msg[:90]}", flush=True)

def t_subprocess():
    import subprocess
    return subprocess.run(["C:Echo", "hi"], capture_output=True).returncode

def t_popen():
    with os.popen("Echo hi") as p:
        return p.read().strip()

def t_system():
    return os.system("Echo hi >NIL:")

def t_ensurepip():
    import ensurepip
    return ensurepip.version()

def t_venv():
    import venv
    d = tempfile.mkdtemp(dir="/RAM")
    venv.create(d + "/v", with_pip=False)
    return sorted(os.listdir(d + "/v"))

def t_pip_sdist():
    # pip builds an sdist in a subprocess (PEP 517 build backend).
    from pip._internal.cli.main import main as pip_main
    d = tempfile.mkdtemp(dir="/RAM")
    src = d + "/pkg"
    os.makedirs(src + "/lim_demo")
    open(src + "/lim_demo/__init__.py", "w").write("X = 1\n")
    open(src + "/pyproject.toml", "w").write(
        '[build-system]\nrequires = []\nbuild-backend = "setuptools.build_meta"\n'
        '[project]\nname = "lim-demo"\nversion = "0.1"\n')
    try:
        return pip_main(["install", "--no-index", "--no-build-isolation", "--target", d + "/t", src])
    except SystemExit as e:
        return f"SystemExit {e.code}"

def t_pydoc():
    import pydoc
    return len(pydoc.render_doc("json", renderer=pydoc.plaintext))

def t_webbrowser():
    import webbrowser
    return webbrowser.get().name

def t_compileall():
    import compileall
    d = tempfile.mkdtemp(dir="/RAM")
    for i in range(4):
        open(f"{d}/m{i}.py", "w").write(f"V = {i}\n")
    return compileall.compile_dir(d, quiet=1, workers=2)

def t_find_library():
    import ctypes.util
    return ctypes.util.find_library("z1")

def t_multiprocessing():
    import multiprocessing
    return multiprocessing.cpu_count()

for n, f in [("subprocess", t_subprocess), ("os.popen", t_popen), ("os.system", t_system),
             ("ensurepip", t_ensurepip), ("venv", t_venv), ("pip-sdist", t_pip_sdist),
             ("pydoc", t_pydoc), ("webbrowser", t_webbrowser), ("compileall-w2", t_compileall),
             ("find_library", t_find_library), ("multiprocessing", t_multiprocessing)]:
    case(n, f)
print("LIMITS-END", flush=True)
