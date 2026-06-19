"""Tymczasowy endpoint diagnostyczny — USUŃ po naprawieniu płatności."""
from http.server import BaseHTTPRequestHandler
import json, os, base64, urllib.request, urllib.error

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        pos_id  = os.environ.get('P24_POS_ID', '')
        api_key = os.environ.get('P24_API_KEY', '')
        sandbox = os.environ.get('P24_SANDBOX', 'true').lower() != 'false'
        base    = 'https://sandbox.przelewy24.pl' if sandbox else 'https://secure.przelewy24.pl'

        # Test połączenia z P24 /api/v1/testAccess
        creds = base64.b64encode(f'{pos_id}:{api_key}'.encode()).decode()
        req = urllib.request.Request(
            base + '/api/v1/testAccess',
            headers={'Authorization': f'Basic {creds}', 'Content-Type': 'application/json'},
            method='GET',
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                p24_response = json.loads(r.read())
                p24_status = r.status
        except urllib.error.HTTPError as e:
            p24_response = e.read().decode('utf-8', errors='replace')
            p24_status = e.code
        except Exception as e:
            p24_response = str(e)
            p24_status = 0

        result = {
            'env_vars_set': {
                'P24_MERCHANT_ID': bool(os.environ.get('P24_MERCHANT_ID')),
                'P24_POS_ID':      bool(pos_id),
                'P24_CRC':         bool(os.environ.get('P24_CRC')),
                'P24_API_KEY':     bool(api_key),
                'P24_SANDBOX':     os.environ.get('P24_SANDBOX', 'NOT SET'),
            },
            'connecting_to': base,
            'p24_test_status': p24_status,
            'p24_test_response': p24_response,
        }

        out = json.dumps(result, indent=2).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, *_):
        pass
