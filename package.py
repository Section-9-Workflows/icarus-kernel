"""Build Poulsback for the compiled kernel and package the files for installation."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

kernel = Path('/linux')
source = Path('/source')
out = Path('/artifacts')
shutil.copytree('/recipe', out / 'recipe', dirs_exist_ok=True)

def identity(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

release = subprocess.check_output(['make', '-s', 'kernelrelease'], cwd=kernel, text=True).strip()
if release != '6.1.190-rt70-vaio-p':
    raise RuntimeError('Unexpected kernel release: ' + release)
target = json.loads((source / 'support/debian-12-bonnell/i686.json').read_text())
target['id'] = 'vaio-rt-i686'
target['inputs']['kernel_lock'] = 'kernel/integration/vaio-rt.lock.json'
target['build_metadata'].update(user='DoubleDensity', host='depot-i386', timestamp='2026-11-14 20:00:00 UTC')
directory = source / 'support/vaio-rt'
directory.mkdir()
lock = json.loads((source / 'kernel/integration/linux.lock.json').read_text())
lock['kernel_release'] = release
lock['abi_inputs'] = {name: identity(kernel / name) for name in lock['abi_inputs']}
lock['linux_source_files'] = {name: identity(kernel / name) for name in lock['linux_source_files']}
module_source = Path('/module-source')
for name in lock['linux_source_files']:
    destination = module_source / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(kernel / name, destination)
# Record the patched kernel sources and generated ABI in a separate lock.
# Keep the reference target unchanged. Its build does not validate the RT target.
(source / target['inputs']['kernel_lock']).write_text(json.dumps(lock, indent=2) + '\n')
(directory / 'i686.json').write_text(json.dumps(target, indent=2) + '\n')
subprocess.run(['python3', '-B', '/source/tools/build-kernel.py', '--build-target', target['id'],
    '--headers', str(kernel), '--kernel-source', str(module_source), '--output', '/module-build',
    '--target', 'physical', '--jobs', sys.argv[1]], check=True)
module = Path('/module-build/physical/poulsback.ko')
compat = Path('/compat-v4l2')
shutil.copytree('/recipe/v4l2loopback', compat)
capture = json.loads((compat / 'capture.json').read_text())
for name, expected in capture.items():
    if identity(compat / name) != {k: expected[k] for k in ('bytes', 'sha256')}:
        raise RuntimeError('Captured virtual-camera source changed: ' + name)
with (out / 'v4l2loopback-build.log').open('w') as stream:
    result = subprocess.run(['make', '-C', str(kernel), 'M=' + str(compat), 'ARCH=x86',
                    'CC=gcc', '-j' + sys.argv[1], 'modules'],
                   stdout=stream, stderr=subprocess.STDOUT)
if result.returncode:
    raise RuntimeError((out / 'v4l2loopback-build.log').read_text()[-8000:])
packages = list(Path('/').glob('linux-image-*.deb')) + list(Path('/').glob('linux-headers-*.deb'))
if len(packages) != 2:
    raise RuntimeError('Expected exactly image and headers packages')
for path in packages:
    shutil.copy(path, out / path.name)
module_vermagic = {}
for name, built_module in [('poulsback', module), ('v4l2loopback', compat / 'v4l2loopback.ko')]:
    vermagic = subprocess.check_output(['modinfo', '-F', 'vermagic', str(built_module)], text=True).strip()
    if not vermagic.startswith(release + ' ') or 'preempt_rt' not in vermagic:
        raise RuntimeError('Module vermagic does not match RT kernel: ' + name)
    module_vermagic[name] = vermagic
    deb = Path('/' + name + '-package')
    dest = deb / 'lib/modules' / release / 'extra'
    dest.mkdir(parents=True)
    shutil.copy(built_module, dest / built_module.name)
    notices = deb / 'usr/share/doc' / (name + '-modules-' + release)
    notices.mkdir(parents=True)
    if name == 'poulsback':
        shutil.copytree('/module-build/physical/licensing', notices / 'licensing')
    else:
        shutil.copy(compat / 'copyright', notices / 'copyright')
    subprocess.run([str(kernel / 'scripts/sign-file'), 'sha512',
        str(kernel / 'certs/signing_key.pem'), str(kernel / 'certs/signing_key.x509'),
        str(dest / built_module.name)], check=True)
    package_version = '13' if name == 'poulsback' else '2'
    control = deb / 'DEBIAN'
    control.mkdir()
    (control / 'control').write_text(f'''Package: {name}-modules-{release}
Version: {package_version}
Architecture: i386
Maintainer: DoubleDensity <doubledense@gmail.com>
Depends: linux-image-{release} (= 6.1.190-rt70-vaio1.1), kmod
Description: {name} module for the VAIO RT kernel candidate
 Compilation verified; device qualification and driver selection are separate.
''')
    (control / 'postinst').write_text(f'#!/bin/sh\nset -e\nif [ "$1" = configure ]; then depmod -a {release}; fi\n')
    (control / 'postinst').chmod(0o755)
    subprocess.run(['dpkg-deb', '--root-owner-group', '-Zgzip', '--build', str(deb),
                    str(out / f'{name}-modules-{release}_{package_version}_i386.deb')], check=True)
for name in ['vmlinux', 'System.map', 'Module.symvers']:
    shutil.copy(kernel / name, out / name)
shutil.copy(kernel / 'arch/x86/boot/bzImage', out / 'bzImage')
shutil.copy('/kernel-build.log', out / 'kernel-build.log')
shutil.copy('/module-build/report.json', out / 'poulsback-build-report.json')
shutil.copy('/reference-build/report.json', out / 'reference-build-report.json')
shutil.copytree(directory, out / 'candidate-target')
shutil.copy(source / target['inputs']['kernel_lock'], out / 'candidate-target/linux.lock.json')
subprocess.run(['tar', '-czf', str(out / 'poulsback-build-evidence.tar.gz'), '-C', '/module-build', '.'], check=True)
with (out / 'packages.tsv').open('w') as stream:
    subprocess.run(['dpkg-query', '-W'], stdout=stream, check=True)
commands = {name: (kernel / name).read_text() for name in
            ['init/.main.o.cmd', 'kernel/sched/.core.o.cmd', 'arch/x86/kernel/.process.o.cmd']}
for name, command in commands.items():
    if any(flag not in command for flag in ['-march=bonnell', '-mtune=bonnell', '-m32', '-O2']):
        raise RuntimeError('Target compiler flags missing: ' + name)
    if '-march=native' in command:
        raise RuntimeError('Build-host CPU tuning leaked into kernel')
(out / 'compiler-commands.json').write_text(json.dumps(commands, indent=2) + '\n')
(out / 'build-summary.json').write_text(json.dumps({'kernel_release': release,
    'driver_revision': 'e16941b0997966f37f0ccb9982160bc057e7218d',
    'module_vermagic': module_vermagic, 'status': 'COMPILED_NOT_BOOTED',
    'installed_on_icarus': False, 'hardware_validated': False}, indent=2) + '\n')
with (out / 'SHA256SUMS').open('w') as stream:
    for path in sorted(out.rglob('*')):
        if path.is_file() and path.name != 'SHA256SUMS':
            stream.write(identity(path)['sha256'] + '  ' + str(path.relative_to(out)) + '\n')
print('KERNEL_AND_POULSBACK_PACKAGED: ' + release, flush=True)
