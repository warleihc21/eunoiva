import requests

url = "https://api.mercadolibre.com/oauth/token"

data = {
    "grant_type": "authorization_code",
    "client_id": "6974408972842302",
    "client_secret": "pswqBQJcclOD6vBa0QLGGelbOzLWQcTi",
    "code": "TG-67fa756db22b4000019997be-153067470",
    "redirect_uri": "https://www.inoivos.site/noivos"
}

response = requests.post(url, data=data)

if response.status_code == 200:
    token_info = response.json()
    print("Access Token:", token_info["access_token"])
    print("Refresh Token:", token_info["refresh_token"])
else:
    print("Erro:", response.status_code, response.json())