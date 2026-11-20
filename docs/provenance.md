# Sources and provenance

- Linux: Debian source package 6.1.190-1, obtained through the pinned public
  Poulsback fetcher and its source lock. Linux license notices remain in the
  fetched source and generated packages.
- RT70: [kernel.org patch](https://cdn.kernel.org/pub/linux/kernel/projects/rt/6.1/older/patch-6.1.190-rt70.patch.xz).
  The exact hash and the signature verification recorded during the original
  import are in [rt-provenance.json](../rt-provenance.json). The build checks the
  hash; it does not repeat the historical signature verification.
- Original configuration: captured from a working
  `5.4.82-rt45-xanmod1-vaio-p` kernel and source tree. It is configuration data,
  not a copy of the XanMod tree. Its SHA-256 is
  `dd9267005495feb16c64af99b8f6fb6dbf6815c2f2c1f7617c520fa236c05515`.
- VAIO policy: Linux-source patch hunks preserving selected settings from that
  earlier kernel. These retain Linux's licensing. No independent claim of
  novelty or measured speed improvement is made.
- Poulsback dependencies: a local Kconfig entry selecting the helpers needed by
  the separately built module. It does not select the display driver at boot.
- v4l2loopback 0.12.5: retained source and Debian copyright notice under
  [v4l2loopback/](../v4l2loopback/). The source hashes in `capture.json` are checked
  before compilation. [Upstream](https://github.com/umlaeute/v4l2loopback) retains
  its authorship and licensing.

No closed vendor code, firmware payload, private Poulsback dev source, private
mail, host-access credential or module signing key is included. This snapshot
starts a new repository history; private recipe history was not imported.
