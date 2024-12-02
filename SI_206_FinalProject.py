import json
import re
import requests

headers = {'X-MAL-Client-ID': '6114d00ca681b7701d1e15fe11a4987e'}
resp = requests.get('https://api.myanimelist.net/v2/anime/search?status=not_yet_aired&limit=1&offset=0&fields=alternative_titles', headers=headers)
print(resp.json())

def get_MAL_ID(url): ## Picturing a string of a url or multiple as input
    patternID = r'myanimelist.net/anime/(d+)/w*'
    patternTitle = r'myanimelist.net/anime/d+/(w*)'
    MAL_ID =  re.findall(patternID, url)
    MAL_Titles = re.findall(patternTitle, url)
    

    

    ## Want to get specific id from animelist
    return 


def get_anime_details(id):
    url = f'https://api.jikan.moe/v4/anime/{id}'
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Exception(f"Failed to retrieve data: {response.status_code}")

try:
    anime_details = get_anime_details(20)
    print(anime_details)
except Exception as e:
    print(e)