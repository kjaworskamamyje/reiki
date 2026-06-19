"""Tymczasowy endpoint diagnostyczny — USUŃ po naprawieniu płatności."""
from http.server import BaseHTTPRequestHandler
import json, os, hashlib, base64

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        merchant_id = os.environ.get('P24_MERCHANT_ID', 'BRAK')
        pos_id      = os.environ.get('P24_POS_ID', 'BRAK')
        crc         = os.environ.get('P24_CRC', 'BRAK')
        api_key     = os.environ.get('P24_API_KEY', 'BRAK')
        sandbox     = os.environ.get('P24_SANDBOX', 'BRAK')

        def mask(v):
            if v in ('BRAK', ''):
                return v
            s = str(v)
            return s[:3] + '***' + s[-3:] if len(s) > 6 else '***'

        # Sprawdź co idzie do Basic Auth
        try:
            pos_int = int(pos_id)
        except:
            pos_int = None

        creds_raw = f'{pos_id}:{api_key}'
        creds_b64 = base64.b64encode(creds_raw.encode()).decode() if pos_id != 'BRAK' else 'BRAK'

        info = {
            'P24_MERCHANT_ID': mask(merchant_id),
            'P24_POS_ID':      mask(pos_id),
            'P24_CRC':         mask(crc),
            'P24_API_KEY':     mask(api_key),
            'P24_SANDBOX':     sandbox,
            'pos_id_as_int':   pos_int,
            'basic_auth_prefix': creds_b64[:20] + '...' if len(creds_b64) > 20 else creds_b64,
            'sandbox_url': 'https://sandbox.przelewy24.pl' if sandbox != 'false' else 'https://secure.przelewy24.pl',
        }

        out = json.dumps(info, indent=2).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, *_):
        pass
