# HamSpot bootable SD image build

Target: Raspberry Pi OS Lite 64-bit, Raspberry Pi 4/5 initially. This is a **prototype image recipe**, not yet a verified bootable release.

Use the official Raspberry Pi `pi-gen` image builder on an appropriate Linux build host. Place `stage-hamspot` into pi-gen as a custom stage after the base OS stages, or use an equivalent image customization process. Install Python 3 and the HamSpot source in `/opt/hamspot`, install `hamspot.service`, and enable it at boot.

The existing web dashboard runs locally at port 8080. A production image still requires user provisioning, secure authentication, MMDVMHost hardware integration, Nextion serial support, HDMI kiosk setup, firewall management and actual codec bridging.

**Do not distribute the prototype as a functional radio hotspot image.** Test with spare SD media; do not overwrite your existing WPSD/Pi-Star card.
