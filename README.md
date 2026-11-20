# Icarus kernel

My custom real-time Linux kernel for Icarus, a Sony VAIO P VPCP118KX with an
Atom Z550 and a 1600×768 panel. I use it for console applications, audio work,
and graphics through [Poulsback](https://github.com/ishad0w/poulsback).

“VAIO RT” in my Poulsback reports means this machine's **32-bit Linux 6.1.190
kernel with PREEMPT_RT patch RT70**. It is a custom platform configuration, not a
Poulsback release or a claim that other VAIO models have been tested.

## Configuration

[original.config](original.config) preserves the configuration from my earlier
5.4.82-rt45-xanmod1-vaio-p kernel. [prepare.py](prepare.py) migrates it through the
new kernel's Kconfig and verifies the required settings. Each build exports the
result as `kernel.config` and records changed symbols in `config-migration.json`.

The configuration keeps real-time and lazy preemption, a periodic 500 Hz tick,
high-resolution timers, PAE, and the VAIO's storage, Wi-Fi, console and audio
support. The kernel uses O2 and explicit Bonnell compiler targeting. Building
on a different CPU does not change that target. Those flags are a local choice;
we have not measured a performance gain over upstream's compiler settings.

[vaio-policy.patch](vaio-policy.patch) carries the timer, CPU target, scheduler,
cache-pressure, ondemand governor and I/O-affinity defaults retained from my old
setup. This is not a complete port of XanMod. The old global short-sleep changes
and unrelated hardware patches were not carried forward.

## What is published

This first snapshot preserves the earlier build recipe and its public driver
pins. It builds `6.1.190-rt70-vaio-p`, the matching Poulsback module, and the
v4l2loopback module used by the original setup. It is a reproducible starting
point for the platform work, **not an update to install over the newer kernels**.

The laptop now has two separately packaged variants of this platform:

- `6.1.190-rt70-icarus1`: the personal integration, first in GRUB.
- `6.1.190-rt70-pbdev1`: the upstream-dev candidate, second in GRUB.

The older Gold Master kernel remains third, with further recovery entries kept.
The dual-variant build/deployment recipe is still local. Private driver source
and legacy decoder firmware are not included here. This repository does not
reproduce those two complete installed variants yet.

See [building](docs/building.md), [installation and recovery](docs/installation.md),
and [source provenance](docs/provenance.md).

## Device validation

The platform was booted and used on my VAIO P. On the dev variant, I tested
battery-idle sleep and lid-triggered sleep, wake, console switching, and the
[Poulygon](https://github.com/Section-9-Workflows/poulygon) cube after wake.
Poulygon is a compact flat-shaded 3D engine that uses Poulsback directly from a
Linux console. Its repository may require access.

Those results belong to the installed driver revisions recorded in the
[suspend/resume PR](https://github.com/poulsback/poulsback-dev/pull/3), which
currently requires access to upstream's private development repository. They do
not qualify every driver pin or a newly built image. The original kernel's
[public test notes](https://github.com/ishad0w/poulsback/pull/11#validation)
also identify the hardware and earlier revisions.

I used an AI coding agent to migrate the configuration, prepare the recipes,
and run build checks. I performed the reported hands-on device testing.
Licensing and third-party attribution are in [NOTICE.md](NOTICE.md).
