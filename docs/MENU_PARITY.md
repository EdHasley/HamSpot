# Configuration menu parity target

HamSpot will offer the capabilities of Pi-Star and WPSD through original, separate web menus rather than copying their interfaces.

Initial prototype settings page: `/settings.html`. Its fields are client-side preview ONLY; no configuration is saved or applied.

## Feature groups
- General: callsign, DMR ID, hostname, location, timezone.
- Radio: MMDVMHost, hardware/modem, simplex/duplex, RX/TX frequencies, mode toggles.
- DMR: masters, DMRGateway, XLX reflectors, talkgroups, module and ports.
- D-Star: gateway, reflector, module, reconnect.
- Other digital modes: YSF, P25, NXDN, M17 and future per-mode managers.
- Cross-mode: D-Star/DMR bridge and codec backend.
- Firewall: protocol ports, automatic allow rules, validation and rollback.
- Displays: HDMI 0/1, Nextion serial, screen firmware and layout selection.
- Network: Wi-Fi, Ethernet, hostname, DNS.
- Advanced: MMDVMHost parameters, gateway rewrite rules, service settings.
- Maintenance: update, backup/restore, restart, diagnostics, factory reset.

## Implementation requirement
No terminal use for ordinary administration. Initial provisioning must work via first-boot setup UI, Wi-Fi access point or supported Raspberry Pi Imager customization. Authenticated settings API must validate and atomically apply changes, handle port conflicts, preserve connectivity and roll back on failure.

The current menus do not implement backend changes. Hardware-specific options may differ and not every upstream feature can be supported until dependencies are integrated and tested.
