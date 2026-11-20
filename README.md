# Icarus kernel

A real-time Linux kernel configuration for the Sony VAIO P VPCP118KX, with an
Atom Z550 and a 1600×768 panel. It targets console applications, audio work,
and graphics through [Poulsback](https://github.com/ishad0w/poulsback).

“VAIO RT” refers to this **32-bit Linux 6.1.190 kernel with PREEMPT_RT patch
RT70**. It is a VAIO-specific platform configuration, separate from Poulsback.

## Configuration

[original.config](original.config) preserves the configuration from the earlier
5.4.82-rt45-xanmod1-vaio-p kernel. [prepare.py](prepare.py) migrates it through the
new kernel's Kconfig and verifies the required settings. Each build exports the
result as `kernel.config` and records changed symbols in `config-migration.json`.

The configuration keeps real-time and lazy preemption, a periodic 500 Hz tick,
high-resolution timers, PAE, and the VAIO's storage, Wi-Fi, console and audio
support. The kernel uses O2 and explicit Bonnell compiler targeting. Building
on a different CPU does not change that target. Those flags are a local choice;
we have not measured a performance gain over upstream's compiler settings.

[vaio-policy.patch](vaio-policy.patch) carries the timer, CPU target, scheduler,
cache-pressure, ondemand governor and I/O-affinity defaults retained from the earlier
configuration. This is not a complete port of XanMod. The old global short-sleep changes
and unrelated hardware patches were not carried forward.

## What is published

The recipe builds `6.1.190-rt70-vaio-p`, a matching Poulsback module, and
v4l2loopback. Kernel inputs and driver revisions are pinned in the Dockerfile.
Private driver source and decoder firmware are not included.

See [building](docs/building.md), [installation and recovery](docs/installation.md),
and [source provenance](docs/provenance.md).

## Hardware scope

Developed and used on a Sony VAIO P VPCP118KX. Other hardware has not been
validated. Build validation is documented in [building](docs/building.md).

## License

See [NOTICE.md](NOTICE.md) for licensing and third-party attribution.
