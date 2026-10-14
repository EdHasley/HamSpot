# HamSpot pi-gen custom stage

Run `image/build-image.sh` on a Linux Docker build host to generate a Raspberry Pi OS 64-bit prototype image. The script downloads official pi-gen, adds this stage and invokes its Docker builder.

This is a **developer image prototype**, not a completed no-terminal hotspot appliance. It serves the dashboard on loopback only until authentication and first-boot provisioning are implemented. No MMDVMHost or Nextion driver is installed yet. There is no guarantee that the build completes successfully on every build host. Do not flash over a working card.

The build is intended to create an `.img.xz` under `image/work/pi-gen/deploy/`. This path is an expected output, not a published artifact.
