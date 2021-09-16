import requests, os, json


def lnapi(path, method='GET', **kw):
    if os.environ.get('MOCK_LND') == 'true':
        return lnd_mock(path, method, **kw)

    base = os.environ['LND_URL']
    url = '/'.join([base, 'v1', path])
    cert_path = os.environ['LND_CERT_PATH']
    headers = {'Grpc-Metadata-macaroon': os.environ['LND_MACAROON']}
    res = requests.request(method, url, headers=headers, verify=cert_path, **kw)

    try:
        return res.json()
    except json.decoder.JSONDecodeError:
        raise ValueError(res.text)


def lnd_mock(path, method, **kw):
    k = f"{method} {path}"

    if k == 'POST invoices':
        return {"r_hash": 'fake', "payment_request": "fake"}

    if k.startswith('GET invoice/'):
        return {'state': 'SETTLED'}

    raise NotImplementedError(k)
