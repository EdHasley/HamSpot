# HDMI prototype smoke test (not an SD image)

On a Raspberry Pi OS Desktop installation with Chromium, clone HamSpot and run:

```bash
cd HamSpot
python3 app/server.py
```

In another terminal in an active graphical session:

```bash
chromium --kiosk http://127.0.0.1:8080/hdmi.html
```

This tests only the Nextion-style HDMI **visual layout**. It does not control the physical Nextion screen, MMDVM, firewall or bridge. The first milestone is a read-only screen; touchscreen interaction will follow. On a Lite OS, install/configure a graphical compositor and browser before using kiosk mode.
