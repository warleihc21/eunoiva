import requests

refresh_token = 'TG-681ab084604092000120b939-153067470'  # Seu refresh token aqui

url = "https://api.mercadolibre.com/oauth/token"

payload = {
    'grant_type': 'refresh_token',
    'client_id': '4839064475156085',  # Seu client_id
    'client_secret': 'qINYYlydQTai7G0f8waDGVStj7CMK9PI',  # Seu client_secret
    'refresh_token': refresh_token
}

headers = {
    'accept': 'application/json',
    'content-type': 'application/x-www-form-urlencoded'
}

response = requests.post(url, headers=headers, data=payload)

print(response.status_code)
print(response.text)