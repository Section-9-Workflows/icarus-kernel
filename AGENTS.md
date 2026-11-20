# Icarus kernel maintenance

Keep the machine configuration and build recipes separate from Poulsback driver
contributions. Never copy private upstream source, firmware blobs, signing keys,
credentials or machine logs into this repository.

Use DoubleDensity <doubledense@gmail.com> for owner-authored commits. Keep
third-party notices and describe the origin of patches. Validate with real
compilation and owner workflows; do not add or run unit tests or synthetic probes
without explicit owner authorization. A build is not device qualification.

Prefer Depot for builds; install host tools through Nix. Apt belongs only inside
the build container. Never use -march=native for VAIO artifacts. Preserve
reference compiler flags separately from machine-specific optimization choices.

Do not install, reboot or replace a kernel merely because a build passed.
Maintain separate kernel releases and module directories for driver variants.
Preserve working kernels and GRUB recovery entries. Follow README.md for scope
and docs/installation.md for the installation procedure.

Public documentation describes the project, its build inputs and how others can
use it. Keep personal deployment state, boot-menu order, private paths and
operational handover notes outside the repository. Keep the VAIO P model and hardware details prominent: this configuration
specifically targets that platform. Exact revisions belong in validation records
when they support a specific claim.
