# Single-image strategy for Pi 4 and Pi 5

Use Raspberry Pi OS Lite 64-bit with a supported current kernel and firmware covering both Raspberry Pi 4 and 5. Use the official pi-gen tooling to build an SD image; the files here are a packaging scaffold, **not a completed pi-gen stage or flashable image**.

1. Pin a supported Raspberry Pi OS/pi-gen release and base package versions.
2. Build a custom pi-gen stage that installs Python, MMDVM services and the HamSpot application.
3. Create the dedicated hamspot system user and enable the service.
4. Configure a minimal Wayland kiosk session for Nextion-style HDMI 0, with HDMI 1 configurable.
5. Implement and test physical Nextion serial display adapter and model-specific .HMI/.tft.
6. Implement authenticated settings and transactional nftables port changes.
7. Integrate D-Star/DMR routing and a verified codec backend.
8. Build .img.xz and checksum; boot-test Pi 4 and Pi 5 separately before release.

Do not flash this repository as an image: it is source code only.
