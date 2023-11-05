import requests


def translate_text(text, source_lang, target_lang):
    url = "https://translated-mymemory---translation-memory.p.rapidapi.com/get"

    querystring = {
        "langpair": f"{source_lang}|{target_lang}",
        "q": text,
        "mt": "1",
        "onlyprivate": "0",
        "de": "a@b.c"
    }

    headers = {
        "X-RapidAPI-Key": "2a9f6b760dmsh6ddc4270410ad7cp1a29f6jsn72bd39472d4f",
        "X-RapidAPI-Host": "translated-mymemory---translation-memory.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        translation_data = response.json()
        translated_text = translation_data.get('responseData', {}).get('translatedText', 'Translation not found')

        return translated_text

    else:
        return 'Translation service error'
