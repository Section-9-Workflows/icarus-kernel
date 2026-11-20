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

The recipe builds `6.1.190-rt70-vaio-p`, a matching Poulsback module, and
v4l2loopback. Kernel inputs and driver revisions are pinned in the Dockerfile.
Private driver source and decoder firmware are not included.

See [building](docs/building.md), [installation and recovery](docs/installation.md),
and [source provenance](docs/provenance.md).

## Device validation

I booted and used this kernel configuration on a Sony VAIO P VPCP118KX. With
a separately built development driver, I tested battery-idle sleep and
lid-triggered sleep, wake, console switching, and the
[Poulygon](https://github.com/Section-9-Workflows/poulygon) cube after wake.
Poulygon is a compact flat-shaded 3D engine that uses Poulsback directly from a
Linux console. Its repository may require access.

Those results apply to the driver revisions recorded in the
[suspend/resume PR](https://github.com/poulsback/poulsback-dev/pull/3), which
currently requires access to upstream's private development repository. They do
not qualify every driver pin or a newly built image. The original kernel's
[public test notes](https://github.com/ishad0w/poulsback/pull/11#validation)
also identify the hardware and earlier revisions.

I used an AI coding agent to migrate the configuration, prepare the recipes,
and run build checks. I performed the reported hands-on device testing.
Licensing and third-party attribution are in [NOTICE.md](NOTICE.md).
