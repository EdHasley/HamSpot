# HamSpot image

See the root README for flashing, credentials and supported functions. The image produced by this branch is a **DMR integration test**, not a finished multi-mode release.

Both `build-image.sh` and GitHub Actions use `prepare-stage.sh` to package the same application, radio templates and services. Upstream commits are pinned in `radio/sources.json`. The image retains those source trees and their licenses.

Credentials and TLS keys are generated on first boot, never embedded in the published image. Initial Ethernet DHCP is required. Radio/network remain off until configured in the HTTPS control center at port 8443. The host-file editor identifies D-Star files as inactive until their gateways are installed.
