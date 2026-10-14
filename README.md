# HamSpot

Independent Raspberry Pi digital-radio hotspot platform. **Work in progress, not a finished Pi-Star/WPSD replacement.**

## Project goals
- Original responsive web dashboard, live MMDVM radio events
- Nextion-style HDMI kiosk views, including dual HDMI on supported Pi hardware
- Separate physical Nextion HMI/TFT project and serial adapter
- DMR, D-Star and additional supported MMDVM modes
- Editable protocol ports and a secure nftables firewall manager
- D-Star <-> DMR bridge with explicit vocoder backend selection
- Reproducible Raspberry Pi OS installation and eventual flashable image

## First prototype
Run `python3 app/server.py` on Python 3.10+, then open http://127.0.0.1:8080.
To listen on your trusted LAN set `HAMSPOT_HOST=0.0.0.0`. **The prototype has no authentication. Do not expose it to the Internet.**

This first milestone is a demonstration dashboard with mock radio values, not a hardware-ready hotspot.
See docs/ROADMAP.md for implementation boundaries and test plan.
