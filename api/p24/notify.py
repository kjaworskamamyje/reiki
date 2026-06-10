"""
Vercel Serverless Function — POST /api/p24/notify
Webhook wywoływany przez Przelewy24 po płatności — weryfikuje transakcję.
"""
from http.server import BaseHTTPRequestHandler
import json, hashlib, os, urllib.request, urllib.error, base64


def _env_int(key):
    return int(os.environ.get(key, 0))

P24_MERCHANT_ID = _env_int('P24_MERCHANT_ID')
P24_POS_ID      = _env_int('P24_POS_ID')
P24_CRC         = os.environ.get('P24_CRC', '')
P24_API_KEY     = os.environ.get('P24_API_KEY', '')
P24_SANDBOX     = os.environ.get('P24_SANDBOX', 'true').lower() != 'false'
P24_BASE        = ('https://sandbox.przelewy24.pl'
                   if P24_SANDBOX else
                   'https://secure.przelewy24.pl')


def _sha384(ordered: dict) -> str:
    raw = json.dumps(ordered, separators=(',', ':'))
    return hashlib.sha384(raw.encode('utf-8')).hexdigest()


def _p24_put(path: str, payload: dict) -> dict:
    creds = base64.b64encode(f'{P24_POS_ID}:{P24_API_KEY}'.encode()).decode()
    req = urllib.request.Request(
        P24_BASE + path,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type':  'application/json',
            'Authorization': f'Basic {creds}',
        },
        method='PUT',
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        raise RuntimeError(f'P24 HTTP {e.code}: {body}')


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            n    = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(n))

            session_id = data.get('sessionId')
            order_id   = data.get('orderId')
            amount     = data.get('amount')

            if not all([session_id, order_id, amount]):
                return self._json(400, {'status': 'error', 'msg': 'missing fields'})

            sign = _sha384({
                'sessionId':  session_id,
                'orderId':    order_id,
                'amount':     amount,
                'currency':   'PLN',
                'crc':        P24_CRC,
            })

            verify_payload = {
                'merchantId': P24_MERCHANT_ID,
                'posId':      P24_POS_ID,
                'sessionId':  session_id,
                'amount':     amount,
                'currency':   'PLN',
                'orderId':    order_id,
                'sign':       sign,
            }

            _p24_put('/api/v1/transaction/verify', verify_payload)
            # Tutaj możesz dodać zapis do bazy lub wysłanie e-maila

            self._json(200, {'status': 'ok'})

        except Exception as exc:
            self._json(500, {'status': 'error', 'msg': str(exc)})

    def _json(self, code: int, body: dict):
        out = json.dumps(body).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type',   'application/json')
        self.send_header('Content-Length', str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, *_):
        pass
