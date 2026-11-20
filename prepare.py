"""Migrate the captured configuration onto pinned Linux and RT sources."""
import hashlib
import json
import lzma
from pathlib import Path
import shutil
import subprocess

recipe = Path('/recipe')
source = Path('/source')
kernel = Path('/linux')
artifacts = Path('/artifacts')
artifacts.mkdir()
lock = json.loads((source / 'kernel/integration/linux.lock.json').read_text())
archive = Path('/kernel-inputs/package/usr/src') / lock['source_archive']['filename']
if hashlib.sha256(archive.read_bytes()).hexdigest() != lock['source_archive']['sha256']:
    raise RuntimeError('Linux archive identity changed')
kernel.mkdir()
subprocess.run(['tar', '-xJf', str(archive), '--strip-components=1', '-C', str(kernel)], check=True)
rt = recipe / 'rt.patch.xz'
provenance = json.loads((recipe / 'rt-provenance.json').read_text())
if hashlib.sha256(rt.read_bytes()).hexdigest() != provenance['sha256']:
    raise RuntimeError('RT patch identity changed')
# Debian already carries these two MANA statistics fixes, including newer fields.
omitted = {'drivers/net/ethernet/microsoft/mana/mana_en.c',
           'drivers/net/ethernet/microsoft/mana/mana_ethtool.c'}
chunks = lzma.decompress(rt.read_bytes()).decode().split('diff --git ')
selected = [chunks[0]]
for chunk in chunks[1:]:
    name = chunk.splitlines()[0].split()[0][2:]
    if name in omitted:
        text = (kernel / name).read_text()
        if ('u64_stats_fetch_begin_irq(' in text or 'u64_stats_fetch_retry_irq(' in text
                or 'u64_stats_fetch_begin(' not in text or 'u64_stats_fetch_retry(' not in text):
            raise RuntimeError('Debian MANA fix no longer matches reviewed source')
    else:
        selected.append('diff --git ' + chunk)
adapted = artifacts / 'rt-debian.patch'
adapted.write_text(''.join(selected))
for patch in [adapted, recipe / 'vaio-policy.patch', recipe / 'poulsback-dependencies.patch']:
    subprocess.run(['patch', '--batch', '--forward', '--fuzz=0', '-p1', '-i', str(patch)],
                   cwd=kernel, check=True)
shutil.copy(recipe / 'original.config', kernel / '.config')
config = [str(kernel / 'scripts/config')]
subprocess.run(config + ['--set-str', 'LOCALVERSION', '-vaio-p',
    '--disable', 'LOCALVERSION_AUTO', '--enable', 'PREEMPT_RT',
    '--disable', 'PREEMPT_DYNAMIC', '--enable', 'PREEMPT_LAZY',
    '--enable', 'HZ_500', '--enable', 'HZ_PERIODIC', '--enable', 'MATOM',
    '--module', 'DRM_POULSBACK_EXTERNAL', '--enable', 'DEBUG_INFO_NONE',
    '--set-str', 'SYSTEM_TRUSTED_KEYS', '', '--set-str', 'SYSTEM_REVOCATION_KEYS', ''],
    cwd=kernel, check=True)
subprocess.run(['make', 'olddefconfig'], cwd=kernel, check=True)

def read_config(path):
    result = {}
    for line in path.read_text().splitlines():
        if line.startswith('CONFIG_') and '=' in line:
            key, value = line.split('=', 1)
            result[key[7:]] = value
        elif line.startswith('# CONFIG_') and line.endswith(' is not set'):
            result[line[9:-11]] = 'n'
    return result

old = read_config(recipe / 'original.config')
new = read_config(kernel / '.config')
required = {'X86_32': 'y', 'X86_PAE': 'y', 'MATOM': 'y',
    'PREEMPT_RT': 'y', 'PREEMPT_LAZY': 'y', 'HZ': '500', 'HZ_PERIODIC': 'y',
    'HIGH_RES_TIMERS': 'y', 'SCHED_HRTICK': 'y', 'RCU_BOOST': 'y', 'RCU_BOOST_DELAY': '0',
    'CPU_FREQ_DEFAULT_GOV_USERSPACE': 'y', 'X86_ACPI_CPUFREQ': old['X86_ACPI_CPUFREQ'],
    'DRM_GMA500': old['DRM_GMA500'], 'DRM_FBDEV_EMULATION': 'y',
    'FRAMEBUFFER_CONSOLE': old['FRAMEBUFFER_CONSOLE'], 'FRAMEBUFFER_CONSOLE_ROTATION': 'y',
    'DRM_POULSBACK_EXTERNAL': 'm', 'DRM_GEM_SHMEM_HELPER': 'm', 'DRM_SCHED': 'm',
    'PATA_SCH': old['PATA_SCH'], 'ATH9K': old['ATH9K'], 'SKY2': old['SKY2'],
    'SONY_LAPTOP': old['SONY_LAPTOP'], 'SND_HDA_INTEL': old['SND_HDA_INTEL'],
    'SND_HDA_CODEC_REALTEK': old['SND_HDA_CODEC_REALTEK'], 'SND_USB_AUDIO': old['SND_USB_AUDIO'],
    'SND_HRTIMER': old['SND_HRTIMER'], 'SND_SEQUENCER': old['SND_SEQUENCER'], 'FRAME_WARN': '1024',
    'DYNAMIC_FTRACE': 'y', 'CC_OPTIMIZE_FOR_PERFORMANCE': 'y'}
missing = {k: {'wanted': v, 'actual': new.get(k)} for k, v in required.items() if new.get(k) != v}
if missing:
    raise RuntimeError('Required configuration did not survive migration: ' + json.dumps(missing))
changes = {k: {'old': old.get(k), 'new': new.get(k)} for k in sorted(old.keys() | new.keys())
           if old.get(k) != new.get(k)}
(artifacts / 'config-migration.json').write_text(json.dumps(changes, indent=2) + '\n')
(artifacts / 'required-config.json').write_text(json.dumps(required, indent=2) + '\n')
shutil.copy(kernel / '.config', artifacts / 'kernel.config')
shutil.copytree(recipe, artifacts / 'recipe', ignore=shutil.ignore_patterns('.git'))
print('CONFIGURATION_READY: RT, lazy preemption, 500 Hz, Bonnell and VAIO devices verified', flush=True)
