import requests

headers = {
    'Content-Type': 'application/xml',
    'Accept': 'application/xml',
}
params = (('apiKey', 'ca2f08c5-8b33-454a-adc4-8215cfb3e088'),)

data = """
<?xml version="1.0"?>
<researchOutputsQuery>
	<size>
		1
	</size>
</researchOutputsQuery>
"""

data = data.encode('utf-8')

url = f'https://pure01.tugraz.at/ws/api/514/research-outputs'

response = requests.post(url, headers=headers, params=params, data=data)
print(response.content)
