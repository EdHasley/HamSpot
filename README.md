# HamSpot

Independent Raspberry Pi radio platform. **In development; not a complete Pi-Star/WPSD replacement.**

## DMR integration image

The `image/dmr-integration` branch builds a Raspberry Pi OS Lite arm64 image for testing on spare SD media. It installs pinned upstream MMDVM-Host and DMRGateway sources, Mosquitto, authenticated HTTPS administration, saved settings, custom XLX hosts/ports, and systemd startup. No callsign, private reflector or RF frequency is published in this repository.

Working application paths: radio configuration, saved reflectors, quick connect/disconnect, start/stop, live journal diagnostics, JSON configuration backup/restore, and a separate host-file editor for DMR/XLX, DCS, XRF and REF. DMR host edits feed DMRGateway; D-Star lists are stored only until their gateways are integrated. Themes apply throughout the control center.

Radio and network are disabled on first boot. First use requires callsign, DMR ID and licensed RX/TX frequencies. Modem profile defaults to `/dev/ttyAMA0`, 115200 baud; Pi 5 GPIO UART overlay is included. FM and POCSAG are explicitly disabled. RX/TX and reflector login must be tested on actual hardware.

### Using a generated image

1. Download the successful **Build HamSpot SD Image** Actions artifact and extract its `.img.xz` from the artifact ZIP. Flash the `.img.xz` to a **spare** card with Raspberry Pi Imager. Keep the existing card intact.
2. Connect Ethernet for initial setup and boot the Pi. Allow time for the unique TLS certificate and login to be generated.
3. Credentials are printed to the attached console and written to `HAMSPOT-LOGIN.txt` on the FAT boot partition after first boot. If using another computer to read that partition, shut down the Pi before removing the card.
4. Open `https://hamspot.local:8443` (or the Pi IP at port 8443). The certificate is generated on the Pi, so a certificate warning is expected. Sign in as `admin` using the generated password.
5. Enter radio settings and enable the radio. Add reflector entries, including any custom remote UDP port, then use Quick Connect. Review Diagnostics for modem initialization and gateway login; an active service alone is not a successful link.

SSH is disabled. Do not forward the administration port to the Internet. Keep credential files and backups private. The operating-system account is not the web admin account.

### What is not finished

D-Star/other mode gateways, cross-mode audio, physical Nextion HMI/TFT and serial driver, automatic Wi-Fi provisioning, dual HDMI kiosk startup, firewall editing, and full Pi-Star/WPSD menu parity remain unfinished. Unimplemented features are identified rather than exposed as working controls. This image is a DMR integration test, **not the requested complete multi-mode release**.

## Development

`python3 -m unittest discover -s tests -v` tests validation, rendering, authentication, host editing and failed-operation rollback. Run `bash image/build-image.sh` on a Linux host with Docker to build locally, or use the repository Actions workflow. Build success does not certify Pi boot, RF transmit, network audio or displays. See `docs/BUILD_STATUS.md` for exact scope.

Radio source revisions are recorded in `radio/sources.json`. Upstream source and license files remain under `/usr/local/src/hamspot` in the image. HamSpot does not claim authorship of those programs.

## Dashboard integration prototype

Branch `prototype/dashboard-integration` adds a full-width layout, charcoal/slate dark theme, radio/network sidebar, live CPU temperature/memory/disk metrics and journal event table. Dashboard start/stop and XLX controls use the existing privileged service helper; settings are saved to the same configuration used by MMDVM-Host and DMRGateway. Cross mode reports unavailable until D-Star gateway and codec integration exists.

This branch triggers the SD image workflow automatically. Download only a successful image artifact from that branch's latest build. Test on a spare card: save callsign/DMR ID/frequencies/modem settings, enable radio, check modem initialization in Diagnostics, save an XLX host/port, connect to a module and check gateway login. Then test RF receive and transmit audio in both directions. Neither successful unit tests nor an image build proves hardware operation.

Browser passwords can be changed under **Backup & Maintenance → Change browser password**. Enter the current password and the new password twice. Simple nonempty passwords are accepted without complexity rules (1–128 characters). Reload afterward and sign in as `admin` with the new password. This changes the web login only; configuration backups do not include or restore it. The first-boot login file continues to show the original generated password after a change.
