#!/usr/bin/env python3
"""Package the static embedding interface from an ABIv11 release build."""
import argparse
import gzip
import hashlib
import io
import os
import pathlib
import shutil
import subprocess
import tarfile
import tempfile
import zipfile

REPO = pathlib.Path(__file__).resolve().parents[1]
NAME = 'aros-cpython-3.14.7-abiv11-0.1.0-dev'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    work = pathlib.Path(os.environ.get('WORK', REPO / 'work'))
    parser.add_argument('--build', type=pathlib.Path, default=os.environ.get('BUILD_DIR', work / 'build'))
    parser.add_argument('--install', type=pathlib.Path, default=work / 'install/Python')
    parser.add_argument('--deps', type=pathlib.Path, default=os.environ.get('DEPS', work / 'deps'))
    parser.add_argument('--output', type=pathlib.Path, default=work / 'dist')
    parser.add_argument('--strip', default='x86_64-aros-strip')
    parser.add_argument('--make', default=os.environ.get('MAKE', shutil.which('gmake') or 'make'))
    args = parser.parse_args()
    build, install, deps = (p.resolve() for p in (args.build, args.install, args.deps))
    for item in (build / 'python.exe', build / 'Makefile',
                 build / 'libpython3.14.a', build / 'pyconfig.h',
                 install / 'include/python3.14/Python.h',
                 install / 'include/python3.14/pyconfig.h',
                 install / 'lib/libpython3.14.a'):
        if not item.is_file():
            parser.exit(2, f'Missing {item}. Run scripts/build.sh first.\n')
    if (build / 'libpython3.14.a').read_bytes() != (install / 'lib/libpython3.14.a').read_bytes():
        parser.exit(2, 'Installed libpython differs from build. Run scripts/build.sh first.\n')
    if (build / 'libpython3.14.a').stat().st_mtime_ns > (build / 'python.exe').stat().st_mtime_ns:
        parser.exit(2, 'libpython is newer than python.exe. Run scripts/build.sh first.\n')
    if (build / 'pyconfig.h').read_bytes() != (install / 'include/python3.14/pyconfig.h').read_bytes():
        parser.exit(2, 'Installed pyconfig.h differs from build. Run scripts/build.sh first.\n')
    with tempfile.TemporaryDirectory() as temporary:
        temp = pathlib.Path(temporary)
        interpreter = temp / 'python'
        subprocess.run([args.strip, '--strip-debug', '-o', str(interpreter),
                        str(build / 'python.exe')], check=True)
        sha = hashlib.sha256(interpreter.read_bytes()).hexdigest()
        provenance = (REPO / 'package/interpreter-provenance.txt').read_text()
        expected = next(line.split('=', 1)[1] for line in provenance.splitlines()
                        if line.startswith('interpreter_sha256='))
        if sha != expected:
            parser.exit(2, f'Build does not match release interpreter: {sha}, expected {expected}\n')
        # Ask the real Makefile to expand its module dependencies; a copied list
        # would silently lose libraries when a builtin module changes.
        extra = temp / 'print.mk'
        extra.write_text('dev-print:\n\t@echo $(srcdir)\n\t@echo $(LOCALMODLIBS) $(LIBS) $(SYSLIBS)\n')
        expanded = subprocess.check_output(
            [args.make, '-s', '-f', 'Makefile', '-f', str(extra), 'dev-print'],
            cwd=build, text=True).splitlines()
        source_root = (build / expanded[0]).resolve()
        flags = expanded[1].split()
        root = temp / NAME
        shutil.copytree(install / 'include', root / 'include')
        lib = root / 'lib'
        lib.mkdir()
        shutil.copy2(install / 'lib/libpython3.14.a', lib)
        dependencies = []
        for flag in flags:
            if flag.endswith('.a'):
                source = pathlib.Path(flag)
                if not source.is_absolute():
                    source = build / source
                source = source.resolve()
                if source.stat().st_mtime_ns > (build / 'python.exe').stat().st_mtime_ns:
                    parser.exit(2, f'{source} is newer than python.exe. Run scripts/build.sh first.\n')
                if not source.is_relative_to(build) and not source.is_relative_to(deps):
                    parser.exit(2, f'Unexpected archive outside build/deps: {source}\n')
                if source.name not in dependencies:
                    shutil.copy2(source, lib / source.name)
                    dependencies.append(source.name)
            elif flag.startswith('-l'):
                if flag not in dependencies:
                    dependencies.append(flag)
            else:
                parser.exit(2, f'Unhandled module linker flag: {flag}\n')
        for archive in lib.glob('*.a'):
            subprocess.run([args.strip, '-D', '--strip-debug', str(archive)], check=True)
        cmake = lib / 'cmake/AROSPython'
        cmake.mkdir(parents=True)
        cmake_libs = ['${_AROSPython_ROOT}/lib/libpython3.14.a'] + [
            item if item.startswith('-l') else '${_AROSPython_ROOT}/lib/' + item
            for item in dependencies]
        (cmake / 'AROSPythonConfig.cmake').write_text(
            'get_filename_component(_AROSPython_ROOT "${CMAKE_CURRENT_LIST_DIR}/../../.." ABSOLUTE)\n'
            'if(NOT CMAKE_SYSTEM_NAME STREQUAL "AROS")\n'
            '  message(FATAL_ERROR "AROSPython requires an AROS toolchain")\nendif()\n'
            'if(NOT CMAKE_SIZEOF_VOID_P EQUAL 8)\n'
            '  message(FATAL_ERROR "AROSPython requires x86-64 ABIv11")\nendif()\n'
            'if(NOT TARGET AROSPython::Python)\n'
            '  add_library(AROSPython::Python INTERFACE IMPORTED)\n'
            '  set_target_properties(AROSPython::Python PROPERTIES\n'
            '    INTERFACE_INCLUDE_DIRECTORIES "${_AROSPython_ROOT}/include/python3.14"\n'
            '    INTERFACE_LINK_OPTIONS "-nix"\n'
            '    INTERFACE_LINK_LIBRARIES "' + ';'.join(cmake_libs) + '")\nendif()\n'
            'set(AROSPython_VERSION 3.14.7)\nset(AROSPython_ABI 11)\n')
        pc = lib / 'pkgconfig'
        pc.mkdir()
        pc_libs = ['${libdir}/libpython3.14.a'] + [
            item if item.startswith('-l') else '${libdir}/' + item for item in dependencies]
        (pc / 'aros-python-3.14-embed.pc').write_text(
            'prefix=${pcfiledir}/../..\nlibdir=${prefix}/lib\nincludedir=${prefix}/include/python3.14\n'
            'Name: AROS CPython embedding\nDescription: CPython 3.14.7 x86-64 ABIv11\n'
            'Version: 3.14.7\nCflags: -I${includedir}\nLibs: -nix ' + ' '.join(pc_libs) + '\n')
        shutil.copytree(REPO / 'package/dev', root, dirs_exist_ok=True)
        shutil.copytree(REPO / 'package/licenses', root / 'licenses')
        shutil.copy2(REPO / 'package/THIRD-PARTY-NOTICES.txt', root)
        shutil.copy2(REPO / 'LICENSE', root / 'LICENSE.port.txt')
        shutil.copy2(source_root / 'LICENSE', root / 'LICENSE.CPython.txt')
        (root / 'interpreter-provenance.txt').write_text(provenance)
        (root / 'link-dependencies.txt').write_text('\n'.join(dependencies) + '\n')
        files = sorted(p for p in root.rglob('*') if p.is_file())
        manifest = ''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' +
                           p.relative_to(root).as_posix() + '\n' for p in files)
        (root / 'MANIFEST.sha256').write_text(manifest)
        args.output.mkdir(parents=True, exist_ok=True)
        archive = args.output / (NAME + '.tar.gz')
        # Fix metadata and gzip timestamp so a repeated package is byte-identical.
        with archive.open('wb') as stream, gzip.GzipFile(fileobj=stream, mode='wb', mtime=0, filename='') as compressed:
            with tarfile.open(fileobj=compressed, mode='w') as tar:
                for p in sorted(root.rglob('*')):
                    if p.is_file():
                        data = p.read_bytes()
                        info = tarfile.TarInfo(NAME + '/' + p.relative_to(root).as_posix())
                        info.size, info.mode, info.mtime = len(data), 0o644, 1790294400
                        tar.addfile(info, io.BytesIO(data))
        checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
        (args.output / (archive.name + '.sha256')).write_text(checksum + '  ' + archive.name + '\n')
        zip_path = args.output / (NAME + '.zip')
        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipped:
            for p in sorted(root.rglob('*')):
                if p.is_file():
                    info = zipfile.ZipInfo(NAME + '/' + p.relative_to(root).as_posix(),
                                           (2026, 9, 25, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o100644 << 16
                    zipped.writestr(info, p.read_bytes())
        zip_sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()
        (args.output / (zip_path.name + '.sha256')).write_text(zip_sha + '  ' + zip_path.name + '\n')
        print(f'{archive}\n{checksum}')
        print(f'{zip_path}\n{zip_sha}')


if __name__ == '__main__':
    main()
