# Installation and recovery

The recipe uses the `6.1.190-rt70-vaio-p` release name. Choose a distinct release
and package version when testing changes alongside an existing installation.
This keeps each kernel and its modules separate.

For a reviewed installation:

1. Save the current kernel, initramfs, configuration and GRUB entries. Verify that
   the working recovery kernel remains installed and has a usable boot entry.
2. Check the artifact hashes and inspect the packages. The kernel and external
   modules must have the same release and RT vermagic. Keep distinct module
   directories for distinct driver variants.
3. Install the reviewed image and matching modules. Generate a dedicated
   initramfs with the intended display driver. Do not globally remove the stock
   gma500 recovery path or replace an already working initramfs.
4. Inspect GRUB before rebooting. Keep a known-working kernel available and
   confirm that you can select it if the new kernel fails to boot.
5. Reboot with physical access to the machine. Verify the loaded kernel and
   driver identities, login, console switching and normal applications before
   testing sleep/wake.

The build's headers use Debian 12 tools, which may not run on older userspace.
Build additional modules in the matching container rather than upgrading the
laptop's system toolchain just for that purpose.

Installation is manual; this repository does not provide an automatic installer.
Do not unload/reset the GPU driver after an unknown hardware outcome.
