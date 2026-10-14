# HamSpot roadmap

## Phase 1 — prototype
Original browser dashboard, status API, config schema and tests.

## Phase 2 — MMDVM integration
Hardware discovery, MMDVMHost service management, event parsing, DMRGateway and D-Star gateway configuration. Respect upstream licenses and network policies.

## Phase 3 — displays
Nextion-style HDMI kiosk via a display server; independent HDMI 0/1 layouts where supported. Physical Nextion serial adapter, Nextion Editor .HMI source and compiled .tft after confirming the exact 3.5-inch model. The HDMI output is software-rendered, not a conversion of Nextion serial bytes.

## Phase 4 — secure settings
Authenticated admin API, port collision checks, validated privileged agent, nftables rule transactions with automatic rollback and remote-access recovery.

## Phase 5 — D-Star/DMR bridge
Bidirectional call state machines, callsign/DMR-ID mapping, talkgroup/module mapping, jitter buffers, codec backend and hardware transcoder support. D-Star and DMR AMBE formats are not guaranteed directly interchangeable. Verify audio conversion on real equipment.

## Phase 6 — packaging
Systemd units, automated tests, reproducible Raspberry Pi OS image, Pi 4/5 HDMI and Nextion hardware validation.

No claim is made that unfinished subsystems currently function.
