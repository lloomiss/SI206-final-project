import json
import re
import requests
from bs4 import BeautifulSoup
#headers = {'X-MAL-Client-ID': '6114d00ca681b7701d1e15fe11a4987e'}
#resp = requests.get('https://api.myanimelist.net/v2/anime/search?status=not_yet_aired&limit=1&offset=0&fields=alternative_titles', headers=headers)
#print(resp.json())

def tomato_extract(tag):
    # get the tags for anime titles, tomatometers, and popcornmeters
    title_tag = tag.find('span', {'data-qa': 'discovery-media-list-item-title'})
    tomatometer_tag = tag.find('rt-text', {'slot': 'criticsScore'})
    popcornmeter_tag = tag.find('rt-text', {'slot': 'audienceScore'})

    # get the text or return a NULL value if no text
    title = title_tag.get_text(strip=True) if title_tag else "NULL"
    tomatometer = tomatometer_tag.get_text(strip=True) if tomatometer_tag else "NULL"
    popcornmeter = popcornmeter_tag.get_text(strip=True) if popcornmeter_tag else "NULL"
    
    return (title, tomatometer, popcornmeter)

def get_RT_Info(soup) -> list:
    # initialize list of tuples to return
    RT_data_list = []

    # get the a and div tags
    a_data_tags = soup.find_all('a', {'data-track': 'scores'}, {'data-qa': 'discovery-media-list-item-caption'})
    div_data_tags = soup.find_all('div', {'data-track': 'scores'}, {'data-qa': 'discovery-media-list-item-caption'})

    # combine the a and div tags into one list
    data_tags = a_data_tags + div_data_tags

    # iterate through all the tags, extract the data, and append each tuple to RT_data_list
    if data_tags:
        for tag in data_tags:
            RT_data_list.append(tomato_extract(tag))
    else:
        print("No data found")
    
    print(RT_data_list)
    return RT_data_list


'''def get_MAL_ID(url): ## Picturing a string of a url or multiple as input
    patternID = r'myanimelist.net/anime/(d+)/w*'
    patternTitle = r'myanimelist.net/anime/d+/(w*)'
    MAL_ID =  re.findall(patternID, url)
    MAL_Titles = re.findall(patternTitle, url)
    

    

    ## Want to get specific id from animelist
    return '''


'''def get_anime_details(id):
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
    #evie testing'''

def main():
    # get soup
    url = 'https://www.rottentomatoes.com/browse/tv_series_browse/genres:anime~sort:popular?page=5'
    r = requests.get(url)
    
    if r.status_code == 200:
        html = r.text
        tomato_soup = BeautifulSoup(html, 'html.parser')
    else:
        print('Invalid URL')
        return

    d = get_RT_Info(tomato_soup)

if __name__ == "__main__":
    main()