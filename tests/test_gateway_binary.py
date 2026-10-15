"""Optional real-binary test: HAMSPOT_GATEWAY_BINARY=/path/to/DMRGateway.

Uses only loopback UDP and synthetic identities; no radio or public reflector.
"""
import configparser
import hashlib
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app'))
from radio import render


@unittest.skipUnless(os.getenv('HAMSPOT_GATEWAY_BINARY'), 'Optional compiled gateway not provided')
class GatewayBinaryTests(unittest.TestCase):
    def test_private_reflector_login_and_module_command(self):
        binary = str(Path(os.environ['HAMSPOT_GATEWAY_BINARY']).resolve())
        with tempfile.TemporaryDirectory() as directory, socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as master, socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as modem, socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as reservation:
            master.bind(('127.0.0.1', 0))
            modem.bind(('127.0.0.1', 0))
            reservation.bind(('127.0.0.1', 0))
            gateway_port = reservation.getsockname()[1]
            reservation.close()
            master.settimeout(0.2)
            config = json.loads((ROOT / 'radio/defaults.json').read_text())
            config.update(callsign='N0TEST', dmr_id=1234567,
                          rx_frequency=433200000, tx_frequency=433200000,
                          radio_enabled=True, network_enabled=True,
                          selected_reflector='TST', module='E',
                          reflectors=[dict(id='TST', label='Loopback test',
                                           host='127.0.0.1', port=master.getsockname()[1],
                                           password='test-secret')])
            files = render(config, directory)
            ini = configparser.ConfigParser(interpolation=None)
            ini.optionxform = str
            ini.read_string(files['DMRGateway.ini'])
            ini['General']['LocalPort'] = str(gateway_port)
            ini['General']['RptPort'] = str(modem.getsockname()[1])
            buf = io.StringIO()
            ini.write(buf, space_around_delimiters=False)
            files['DMRGateway.ini'] = buf.getvalue()
            for name, text in files.items():
                (Path(directory) / name).write_text(text)
            salt = bytes.fromhex('12345678')
            seen = set()
            with (Path(directory) / 'gateway.log').open('w+') as log:
                proc = subprocess.Popen([binary, str(Path(directory) / 'DMRGateway.ini')],
                                        cwd=directory, stdout=log, stderr=log)
                try:
                    deadline = time.monotonic() + 20
                    while time.monotonic() < deadline:
                        if proc.poll() is not None:
                            log.seek(0)
                            self.fail('Gateway exited early: ' + log.read())
                        try:
                            packet, peer = master.recvfrom(2048)
                        except socket.timeout:
                            continue
                        if packet.startswith(b'RPTL'):
                            self.assertEqual(packet[4:8], (1234567).to_bytes(4, 'big'))
                            seen.add('login')
                            master.sendto(b'RPTACK' + salt, peer)
                        elif packet.startswith(b'RPTK'):
                            self.assertEqual(packet[8:], hashlib.sha256(salt + b'test-secret').digest())
                            seen.add('password')
                            master.sendto(b'RPTACK' + packet[4:8], peer)
                        elif packet.startswith(b'RPTC'):
                            self.assertIn(b'N0TEST', packet)
                            self.assertIn(b'433200000', packet)
                            seen.add('configuration')
                            master.sendto(b'RPTACK' + packet[4:8], peer)
                        elif packet.startswith(b'DMRD'):
                            destination = int.from_bytes(packet[8:11], 'big')
                            if destination == 4005:
                                self.assertTrue(packet[15] & 0x40, 'Module command must be a private call')
                                seen.add('module E')
                                break
                    self.assertEqual(seen, {'login', 'password', 'configuration', 'module E'})
                finally:
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait()


if __name__ == '__main__':
    unittest.main()
