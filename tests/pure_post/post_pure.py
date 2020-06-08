import requests
from pprint import pprint

def _process_response(response, dirpath, type):
    open(f'{dirpath}/response_{type}.xml', "wb").write(response.content)

    print(f"""
    request:            {response.request}
    status_code:        {response.status_code}
    reason:             {response.reason}
    content_consumed:   {response._content_consumed}
    url:                {response.url}
    headers:            {response.headers}
    """)
    return response.status_code
    

headers = {
    'Content-Type': 'application/xml',
    'Accept': 'application/xml',
}
params = (('apiKey', 'ca2f08c5-8b33-454a-adc4-8215cfb3e088'),)

dirpath = '/home/bootcamp/src/pure_sync_rdm/synchronizer/tests/pure_post'
data = open(f'{dirpath}/data.xml', 'r').read().encode('utf-8')

record_uuid = '6c551848-4c93-4b5e-a512-5861cc028b85'

url = f'https://pure01.tugraz.at/ws/api/514/research-outputs/{record_uuid}'

response = requests.put(url, headers=headers, params=params, data=data)
r1 = _process_response(response, dirpath, '1')

response = requests.post(url, headers=headers, params=params, data=data)
r2 = _process_response(response, dirpath, '2')


url = f'https://pure01.tugraz.at/ws/api/514/research-outputs'

response = requests.put(url, headers=headers, params=params, data=data)
r3 = _process_response(response, dirpath, '3')

response = requests.post(url, headers=headers, params=params, data=data)
r4 = _process_response(response, dirpath, '4')

print(f"""
uuid put:   {r1}
uuid post:  {r2}
put:        {r3}
post:       {r4}
""")

# 405 Method Not Allowed
# 400 Bad Request