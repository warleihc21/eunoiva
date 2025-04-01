import requests

CLIENT_ID = "3067363791536171"
CLIENT_SECRET = "7DHF45r97SjuLEovjqtxPfO1sNC0ENWF"

url = "https://api.mercadolibre.com/oauth/token"
data = {
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "scope": "read"
}

response = requests.post(url, data=data)

if response.status_code == 200:
    token_info = response.json()
    access_token = token_info.get("access_token")
    print(f"Access Token: {access_token}")
else:
    print(f"Erro ao obter token: {response.json()}")
    print(f"Código de status: {response.status_code}")