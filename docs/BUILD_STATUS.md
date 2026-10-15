# Build status and remaining work

## Implemented in DMR integration branch

- Pinned G4KLX MMDVM-Host and DMRGateway source compilation during image build, including Mosquitto dependency.
- Validated callsign/ID, UART, frequencies, duplex, DMR color code, slot, talkgroup and level/offset settings.
- First boot RF/network off; FM/POCSAG off. UART defaults to ttyAMA0, not the different serial0 mapping observed on the test Pi.
- Original full-width light/dark dashboard backed by actual configuration and service operations.
- Saved custom XLX reflectors, per-reflector remote UDP ports and passwords; quick connection changes from dashboard.
- DMR/XLX host editor, and stored DCS/XRF/REF text editors on a separate submenu, with per-file downloads. D-Star files are not consumed until gateways are implemented.
- Basic authentication over unique self-signed TLS, per-card random password, fixed privileged helper, request validation, journal diagnostics and configuration backup/restore.
- Config writes are serialized; start command failures restore previous files. Delayed modem/network failures are visible in diagnostics, not automatically rolled back. Start success is not proof of connection.

## Evidence from prior physical Pi testing

The manually installed MMDVM-Host communicated on ttyAMA0, read MMDVM_HS_Dual_Hat v1.6.1 firmware, and decoded a user DMR RF transmission after FM was disabled. This is evidence for the modem path on that existing card, not validation of this new image. TX, network return audio and first boot remain unverified.

## Required before a complete release

- Build image successfully; inspect manifest/artifact; boot on spare card on Pi 5.
- Verify generated credentials, DHCP/mDNS, TLS, modem UART, save/apply, persistence after reboot, RF receive/transmit, reflector login, module selection and bidirectional audio.
- Integrate and test D-Star gateway/REF/DCS/XRF connections and remaining mode gateways.
- Implement physical Nextion NX4832K035 UI, serial events and flashing support.
- Implement dual HDMI kiosk configuration, network/Wi-Fi management, safe updates and remaining menu groups.
- Test all supported hardware profiles; audit privilege boundary, service stop/start behavior, recovery and backup restoration.

No file from the user's SD card has been uploaded. Personal settings are intentionally not reconstructed or committed.
