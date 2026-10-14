import json, subprocess, sys, time, urllib.request
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
class SmokeTest(unittest.TestCase):
    def test_status_and_hdmi(self):
        import socket
        sock=socket.socket();sock.bind(("127.0.0.1",0));port=sock.getsockname()[1];sock.close()
        import os
        env=dict(os.environ,HAMSPOT_PORT=str(port))
        proc=subprocess.Popen([sys.executable,str(ROOT/"app/server.py")],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try:
            for _ in range(30):
                try:
                    with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/status",timeout=1) as r: data=json.load(r)
                    break
                except Exception: time.sleep(.1)
            else:self.fail("server did not start")
            self.assertTrue(data["demo"])
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/hdmi.html") as r:
                self.assertIn(b"NEXTION-STYLE HDMI",r.read())
        finally:
            proc.terminate()
            proc.wait(timeout=5)
if __name__=="__main__":unittest.main()
