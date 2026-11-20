# Installation and recovery

The published recipe uses the historical `6.1.190-rt70-vaio-p` release name.
Do not install its packages over an existing kernel of that name or treat it as
an upgrade to Icarus's current dual-variant setup. Allocate a new release and
package version before preparing another installation.

For a reviewed installation:

1. Save the current kernel, initramfs, configuration and GRUB entries. Verify that
   the working recovery kernel remains installed and has a usable boot entry.
2. Check the artifact hashes and inspect the packages. The kernel and external
   modules must have the same release and RT vermagic. Keep distinct module
   directories for distinct driver variants.
3. Install the reviewed image and matching modules. Generate a dedicated
   initramfs with the intended display driver. Do not globally remove the stock
   gma500 recovery path or replace an already working initramfs.
4. Inspect GRUB before rebooting. Icarus's agreed order is personal integration,
   upstream-dev candidate, then Gold Master. Keep other working entries too.
5. Reboot with the owner present. Verify the loaded kernel and driver identities,
   login, console switching and normal applications before testing sleep/wake.

The build's headers use Debian 12 tools, which may not run on Icarus's older
userspace. Build additional modules in the matching container rather than
upgrading the laptop's system toolchain just for that purpose.

This repository deliberately contains no automatic installer. The existing
installation scripts depend on private machine snapshots and remain local.
Do not unload/reset the GPU driver after an unknown hardware outcome.
