import requests

def get_latest_news( country='us', category=None):
    base_url = 'https://newsapi.org/v2/top-headlines'

    params = {
        'apiKey': 'f10ac73c073845ca97a86e9a8c77edcb',
        'country': country,
        'category': category
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        news_data = response.json()
        articles = news_data.get('articles', [])
        return articles
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None



# Вам потрібно вставити свій API-ключ замість 'YOUR_API_KEY'
api_key = 'f10ac73c073845ca97a86e9a8c77edcb'
category_to_fetch = 'science'
latest_news = get_latest_news("ua",category_to_fetch)

# if latest_news:
#     print(f"Останні новини у категорії '{category_to_fetch}':")
#     for i, article in enumerate(latest_news, start=1):
#         print(f"{i}. {article['title']} - {article['url']}")
