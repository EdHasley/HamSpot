# HamSpot test hardware: AURSINC B089JYBXHQ

User-provided Amazon ASIN B089JYBXHQ identifies AURSINC MMDVM Duplex Hotspot Module Dual Hat V1.5.2.

Manufacturer manual: https://manuals.plus/asin/B089JYBXHQ.pdf

Pi-Star/WPSD modem menu reference: `STM32-DVM/MMDVM_HS-Raspberry pi Hat (GPIO)`.

Target hardware: Raspberry Pi 5, duplex MMDVM HAT, Nextion display. Secondary target: Raspberry Pi 4.

## Required validation before claiming compatibility
1. Confirm GPIO HAT seating, 40-pin pinout and Pi 5 UART configuration; do not assume Pi 4 UART names work unchanged.
2. Identify Nextion model, UART path, baud rate and power connection. Never confuse HDMI graphics with physical Nextion serial output.
3. Detect modem firmware/version, then configure MMDVMHost with appropriate serial port and duplex settings.
4. Provide a guided, browser-based setup wizard and diagnostics; no terminal required by the end user.
5. Validate both RX and TX using legal amateur frequencies and dummy load/antenna; do not invent frequency defaults.
6. Test image on Pi 5 first and Pi 4 second.

Status: documented hardware target only; no boot-tested image, no proven Pi 5 modem compatibility.
