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

def get_RT_info(soup) -> list:
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


def get_MAL_info(RT_data_list) -> list:
    info_list = []
    for anime in RT_data_list:
        title = anime[0]

        # url here gets "full information from the API" getAnimeFullByld (https://docs.api.jikan.moe/#tag/anime/operation/getAnimeFullById)
        #url = f'https://api.jikan.moe/v4/anime/{modified_string}/full'
        url = f'https://api.jikan.moe/v4/anime?q={title}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data and len(data['data']) > 0:
                first_entry = data['data'][0]
                MAL_ID = first_entry.get('mal_id')
                
                if MAL_ID:
                    full_url = f'https://api.jikan.moe/v4/anime/{MAL_ID}/full'
                    
                    response2 = requests.get(full_url)
                    if response2.status_code == 200:
                        data2 =  response2.json()
                        fullInfo = []
                        seasonScore = data2['data'].get('score', 'null') 
                        numSeasons = -1 # 0 if movie
                        genres_list = data2['data'].get('genres', [])
                        genres = [genre.get('name', 'null') for genre in genres_list]
                        studio_list = data2['data'].get('studios', [])
                        studio = studio_list[0].get('name', 'null') if studio_list else 'null'
                        numEpisodes = data2['data'].get('episodes', 'null')
                        releaseDate = data2['data']['aired'].get('string', 'null') # string formatted as 'Mon XX, XXXX to Mon XX, XXXX'
                        numReviews = data2['data'].get('scored_by', 'null')
                        
                        fullInfo.append((title, seasonScore, genres, studio, numEpisodes, releaseDate, numReviews))
                        
                        info_list.append(fullInfo)
                        
                    else:
                        raise Exception(f"Failed to retrieve full data for MAL ID: {MAL_ID}. Response code: {response2.status_code}")
                else:
                    raise Exception(f"MAL ID not found for title: {title}")
            else:
                raise Exception(f"No data found for title: {title}")
        else:
            raise Exception(f"Failed to retrieve data: {response.status_code}")
    
    return info_list

           
            
            
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

    #d = get_RT_info(tomato_soup)

    try:
        anime_details = get_MAL_info([('Blue Exorcist', '', '') ])
        print(anime_details)
    except Exception as e:
            print(e)


if __name__ == "__main__":
    main()