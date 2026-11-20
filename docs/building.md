# Building the published baseline

Use a Linux AMD64 builder that can execute i386 programs. The Dockerfile uses a
digest-pinned Debian i386 image and runs the kernel tools with `setarch i686`.
No GPU, host device mounts or private GitHub credentials are needed.

```sh
git clone https://github.com/Section-9-Workflows/icarus-kernel.git
cd icarus-kernel
docker buildx build --platform linux/386 --target artifacts \
  --build-arg JOBS=16 --build-arg RECIPE_REVISION="$(git rev-parse HEAD)" \
  --output type=local,dest=artifacts .
```

Choose JOBS to fit the builder. A Depot project can run the same Dockerfile:

```sh
depot build --project YOUR_PROJECT --build-platform linux/amd64 \
  --platform linux/386 --target artifacts --save \
  --build-arg JOBS=16 --build-arg RECIPE_REVISION="$(git rev-parse HEAD)" \
  --output type=local,dest=artifacts .
```

Authenticate using Depot's normal CLI/environment mechanism. Never copy a token
into this tree or pass it as a Docker build argument. GitHub Actions and project
provisioning are not configured by this snapshot.

The recipe fetches public Poulsback commit
`958a0b3c35afba66420adeb2a63194a157e61b5d` for its pinned Linux input tooling.
It later fetches `e16941b0997966f37f0ccb9982160bc057e7218d` for the historical
module build. Both pins are intentional. The reference module and RT module
compile separately; one does not validate the other's ABI.

Linux comes from Debian's verified 6.1.190-1 source archive. The supplied RT70
patch is hash-checked before use. Two MANA statistics hunks already present in
Debian are omitted after checking their expected source form. Other patches
apply without fuzz. Kconfig migration refuses missing required settings.

The artifacts include Debian packages, kernel image/configuration, ABI and
module reports, compiler commands, package versions and SHA-256 checksums:

```sh
cd artifacts
sha256sum -c SHA256SUMS
```

Retain the recipe commit and build receipt with the artifacts. The base image,
Linux and RT inputs are pinned; build-tool packages still resolve from Debian's
package indexes. This is not a guarantee of byte-identical future rebuilds.
Module signing keys are generated inside the build, used there, and excluded
from exported recipe files. Do not publish kernel headers or artifacts without
reviewing their contents separately. Packaging does not install or boot anything.

## Published recipe validation

Recipe commit `10d515c3a1359381ca42adb61eeddfcba71820c9` completed on Depot. The unchanged kernel compilation layer was reused from
cache; the reference and VAIO RT module builds and packaging ran successfully.
Both module reports passed compilation and stack checks. All 40 exported file
checksums passed local verification. Build artifacts are not stored in Git history.

This validates the published recipe and package production. These newly exported
packages have not been installed or booted. The live device results in the
README apply to their recorded kernel and driver revisions.
