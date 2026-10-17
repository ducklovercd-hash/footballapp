import requests
url = "https://v3.football.api-sports.io/leagues"

payload={}
headers = {
  'x-apisports-key': '5a7afef744082c26f28777d2d1462b4b',
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)