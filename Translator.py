import requests

url = "https://translated-mymemory---translation-memory.p.rapidapi.com/get"

querystring = {"langpair":"en|it","q":"Hello World!","mt":"1","onlyprivate":"0","de":"a@b.c"}

headers = {
	"X-RapidAPI-Key": "2a9f6b760dmsh6ddc4270410ad7cp1a29f6jsn72bd39472d4f",
	"X-RapidAPI-Host": "translated-mymemory---translation-memory.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())