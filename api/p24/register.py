"""
Vercel Serverless Function — POST /api/p24/register
Rejestruje transakcję Przelewy24 i zwraca URL do płatności.

Zmienne środowiskowe (ustaw w Vercel Dashboard → Settings → Environment Variables):
  P24_MERCHANT_ID  np. 12345
  P24_POS_ID       np. 12345
  P24_CRC          klucz CRC z panelu P24
  P24_API_KEY      klucz REST API z panelu P24
  P24_SANDBOX      true / false  (domyślnie true)
"""
from http.server import BaseHTTPRequestHandler
import json, hashlib, uuid, os, urllib.request, urllib.error, base64


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


def _p24_post(path: str, payload: dict) -> dict:
    creds = base64.b64encode(f'{P24_POS_ID}:{P24_API_KEY}'.encode()).decode()
    req = urllib.request.Request(
        P24_BASE + path,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type':  'application/json',
            'Authorization': f'Basic {creds}',
        },
        method='POST',
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

            required = {'price', 'svcName', 'date', 'time', 'clientName', 'clientEmail'}
            missing  = required - data.keys()
            if missing:
                return self._json(400, {'error': f'Brak pól: {missing}'})

            # Ustal bazowy URL (działa zarówno lokalnie jak i na produkcji)
            host = (self.headers.get('X-Forwarded-Host')
                    or self.headers.get('Host')
                    or 'reikihealing.pl')
            proto     = 'https' if 'localhost' not in host else 'http'
            site_url  = f'{proto}://{host}'

            session_id    = 'reiki-' + uuid.uuid4().hex
            amount_grosze = int(data['price']) * 100   # PLN → grosze

            sign = _sha384({
                'sessionId':  session_id,
                'merchantId': P24_MERCHANT_ID,
                'amount':     amount_grosze,
                'currency':   'PLN',
                'crc':        P24_CRC,
            })

            payload = {
                'merchantId':  P24_MERCHANT_ID,
                'posId':       P24_POS_ID,
                'sessionId':   session_id,
                'amount':      amount_grosze,
                'currency':    'PLN',
                'description': (f"Sesja Reiki — {data['svcName']} "
                                f"· {data['date']}, {data['time']}"),
                'email':       data['clientEmail'],
                'client':      data['clientName'],
                'phone':       data.get('clientPhone', ''),
                'country':     'PL',
                'language':    'pl',
                'urlReturn':   f'{site_url}/?p24_return=1&sessionId={session_id}',
                'urlStatus':   f'{site_url}/api/p24/notify',
                'sign':        sign,
            }

            result      = _p24_post('/api/v1/transaction/register', payload)
            token       = result['data']['token']
            payment_url = f'{P24_BASE}/trnRequest/{token}'

            self._json(201, {
                'status':     'ok',
                'paymentUrl': payment_url,
                'sessionId':  session_id,
            })

        except Exception as exc:
            self._json(500, {'error': str(exc)})

    def do_OPTIONS(self):
        self._json(200, {})

    def _json(self, code: int, body: dict):
        out = json.dumps(body).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type',  'application/json')
        self.send_header('Content-Length', str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, *_):
        pass
