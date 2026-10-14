import json, os
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
ROOT=Path(__file__).resolve().parent
CONFIG=json.loads((ROOT.parent/"config.example.json").read_text())
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT),**kwargs)
    def do_GET(self):
        if self.path=="/api/status":
            data=json.dumps({"demo":True,"callsign":"DEMO","mode":CONFIG["radio"]["mode"],"reflector":CONFIG["radio"]["reflector"],"talkgroup":CONFIG["radio"]["talkgroup"],"bridge":"not installed","nextion":"not connected"}).encode()
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.send_header("Cache-Control","no-store")
            self.send_header("Content-Length",str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else: super().do_GET()
if __name__=="__main__":
    host=os.getenv("HAMSPOT_HOST","127.0.0.1")
    port=int(os.getenv("HAMSPOT_PORT","8080"))
    print(f"HamSpot prototype http://{host}:{port}")
    ThreadingHTTPServer((host,port),Handler).serve_forever()
