"""Verify that development archives remain usable after relocation."""
import pathlib
import hashlib
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile
import shlex

REPO = pathlib.Path(__file__).resolve().parents[1]


class DevelopmentPackageTests(unittest.TestCase):
    def test_newer_library_is_rejected_before_packaging(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            build, install = root / 'build', root / 'install'
            paths = {'build/python.exe': b'executable', 'build/Makefile': b'',
                     'build/libpython3.14.a': b'archive', 'build/pyconfig.h': b'config',
                     'install/include/python3.14/Python.h': b'header',
                     'install/include/python3.14/pyconfig.h': b'config',
                     'install/lib/libpython3.14.a': b'archive'}
            for name, data in paths.items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                os.utime(target, (100, 100))
            os.utime(build / 'libpython3.14.a', (101, 101))
            result = subprocess.run([sys.executable, str(REPO / 'scripts/build-dev-package.py'),
                                     '--build', str(build), '--install', str(install),
                                     '--deps', str(root), '--output', str(root / 'out')],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('libpython is newer than python.exe', result.stderr)
            self.assertFalse((root / 'out').exists())

    def test_work_environment_selects_build_location(self):
        with tempfile.TemporaryDirectory() as directory:
            env = dict(os.environ, WORK=directory)
            for key in ('BUILD_DIR', 'DEPS'):
                env.pop(key, None)
            result = subprocess.run([sys.executable, str(REPO / 'scripts/build-dev-package.py')],
                                    env=env, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(directory + '/build/python.exe', result.stderr)

    def test_missing_build_is_reported_without_creating_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = pathlib.Path(directory) / 'out'
            result = subprocess.run(
                [sys.executable, str(REPO / 'scripts/build-dev-package.py'),
                 '--build', directory + '/missing', '--install', directory,
                 '--deps', directory, '--output', str(output)],
                capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Run scripts/build.sh first', result.stderr)
            self.assertFalse(output.exists())

    @unittest.skipUnless(os.environ.get('DEV_ARCHIVE'), 'set DEV_ARCHIVE for artifact checks')
    def test_unpacked_manifest_and_relocated_cmake_consumer(self):
        with tempfile.TemporaryDirectory(prefix='python-dev-') as directory:
            location = pathlib.Path(directory)
            with tarfile.open(os.environ['DEV_ARCHIVE']) as archive:
                archive.extractall(location, filter='data')
            root = next(location.iterdir())
            with zipfile.ZipFile(os.environ['DEV_ARCHIVE'].replace('.tar.gz', '.zip')) as zipped:
                for item in zipped.infolist():
                    self.assertEqual(zipped.read(item), (location / item.filename).read_bytes())
            for line in (root / 'MANIFEST.sha256').read_text().splitlines():
                digest, filename = line.split('  ', 1)
                self.assertEqual(hashlib.sha256((root / filename).read_bytes()).hexdigest(), digest)
            self.assertTrue((root / 'include/python3.14/pyconfig.h').is_file())
            for config in (root / 'lib').rglob('*'):
                if config.suffix in ('.pc', '.cmake'):
                    self.assertNotIn('/Users/', config.read_text())
            compiler = os.environ['AROS_TOOLCHAIN'] + '/x86_64-aros-gcc'
            subprocess.run(['cmake', '-S', str(root / 'examples'), '-B', str(location / 'build'),
                            '-DCMAKE_SYSTEM_NAME=AROS', '-DCMAKE_C_COMPILER=' + compiler,
                            '-DCMAKE_SYSROOT=' + os.environ['AROS_SDK'],
                            '-DCMAKE_PREFIX_PATH=' + str(root)], check=True)
            subprocess.run(['cmake', '--build', str(location / 'build')], check=True)
            undefined = subprocess.check_output(
                [os.environ['AROS_TOOLCHAIN'] + '/x86_64-aros-nm', '-u',
                 str(location / 'build/embed')], text=True)
            self.assertEqual(undefined.strip(), '')
            env = dict(os.environ, PKG_CONFIG_PATH=str(root / 'lib/pkgconfig'))
            flags = shlex.split(subprocess.check_output(
                ['pkg-config', '--cflags', '--libs', 'aros-python-3.14-embed'], env=env, text=True))
            target = location / 'pkgconfig-embed'
            subprocess.run([compiler, '--sysroot=' + os.environ['AROS_SDK'],
                            str(root / 'examples/embed.c'), '-o', str(target), *flags], check=True)
            self.assertEqual(subprocess.check_output(
                [os.environ['AROS_TOOLCHAIN'] + '/x86_64-aros-nm', '-u', str(target)], text=True).strip(), '')


if __name__ == '__main__':
    unittest.main()
