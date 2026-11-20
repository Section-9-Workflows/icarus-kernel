FROM docker.io/library/debian@sha256:139eacf457e4a322903c5ac9d5ac33da2b12bd1340e830124694a467a415a0d9 AS build
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates build-essential git python3 patch pkg-config libdrm-dev \
    libelf-dev util-linux bc bison flex libssl-dev kmod rsync cpio xz-utils lz4 \
    && rm -rf /var/lib/apt/lists/*
RUN git init /source && cd /source \
    && git remote add origin https://github.com/Section-9-Workflows/poulsback.git \
    && git fetch --depth=1 origin 958a0b3c35afba66420adeb2a63194a157e61b5d \
    && git checkout --detach FETCH_HEAD \
    && test "$(git rev-parse HEAD)" = 958a0b3c35afba66420adeb2a63194a157e61b5d
WORKDIR /source
RUN setarch i686 python3 -B tools/fetch-kernel.py \
    --build-target debian-12-bonnell-i686 --output /kernel-inputs
COPY original.config rt.patch.xz rt-provenance.json vaio-policy.patch poulsback-dependencies.patch prepare.py /recipe/
ENV ARCH=x86 KBUILD_BUILD_USER=DoubleDensity KBUILD_BUILD_HOST=depot-i386 \
    KBUILD_BUILD_TIMESTAMP="2026-11-14 20:00:00 UTC" KDEB_COMPRESS=gzip \
    KBUILD_DEBARCH=i386 KDEB_PKGVERSION=6.1.190-rt70-vaio1.1
RUN --network=none setarch i686 python3 /recipe/prepare.py
WORKDIR /linux
ARG JOBS=16
RUN --network=none bash -o pipefail -c 'setarch i686 make -j"$JOBS" bindeb-pkg 2>&1 | tee /kernel-build.log'
# Keep the proven kernel layer cached when only the external driver changes.
RUN cd /source && git fetch --depth=1 origin e16941b0997966f37f0ccb9982160bc057e7218d \
    && git checkout --detach FETCH_HEAD \
    && test "$(git rev-parse HEAD)" = e16941b0997966f37f0ccb9982160bc057e7218d
RUN apt-get update && apt-get install -y --no-install-recommends \
    linux-headers-6.1.0-54-686-pae=6.1.190-1 \
    linux-headers-6.1.0-54-common=6.1.190-1 linux-kbuild-6.1 linux-compiler-gcc-12-x86 \
    && rm -rf /var/lib/apt/lists/*
RUN --network=none setarch i686 python3 -B /source/tools/build-kernel.py \
    --build-target debian-12-i686 --headers /usr/src/linux-headers-6.1.0-54-686-pae \
    --kernel-source /kernel-inputs/linux --output /reference-build --target physical --jobs "$JOBS"
COPY package.py README.md Dockerfile .dockerignore .gitattributes AGENTS.md /recipe/
COPY v4l2loopback /recipe/v4l2loopback/
RUN --network=none setarch i686 python3 /recipe/package.py "$JOBS"
FROM scratch AS artifacts
ARG RECIPE_REVISION
LABEL org.opencontainers.image.revision=$RECIPE_REVISION
COPY --from=build /artifacts/ /
