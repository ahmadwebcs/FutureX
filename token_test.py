import urllib.request
import urllib.parse

data = urllib.parse.urlencode({'username': 'admin@example.com', 'password': 'adminpass'}).encode()
req = urllib.request.Request('http://127.0.0.1:8000/api/token-auth/', data=data, method='POST')
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = resp.read().decode('utf-8')
        print('STATUS:', resp.getcode())
        print('CONTENT-TYPE:', resp.getheader('Content-Type'))
        print('\nRESPONSE BODY:\n')
        print(body)
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8') if e.fp is not None else ''
    print('HTTP ERROR:', e.code)
    print('RESPONSE BODY:\n', body)
except Exception as e:
    print('REQUEST ERROR:', e)
