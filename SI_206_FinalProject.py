import json

import requests

'''headers = {'X-MAL-Client-ID': '6114d00ca681b7701d1e15fe11a4987e'}
resp = requests.get('https://api.myanimelist.net/v2/anime/search?status=not_yet_aired&limit=1&offset=0&fields=alternative_titles', headers=headers)
print(resp.json())
'''



def MAL_get_anime_details(id):
    url = f'https://api.jikan.moe/v4/anime/{id}'
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Exception(f"Failed to retrieve data: {response.status_code}")

try:
    MALanime_details = MAL_get_anime_details(6)
    print(MALanime_details)
except Exception as e:
    print(e)

'''
def MAL_get_anime_reviews(id):
    url = f'https://api.jikan.moe/v4/reviews/anime/{id}'
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Exception(f"Failed to retrieve data: {response.status_code}")

try:
    MALanime_reviews = MAL_get_anime_reviews(25)
    print(MALanime_reviews)
except Exception as e:
    print(e)
'''
