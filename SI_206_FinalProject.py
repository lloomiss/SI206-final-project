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

#something to note -- specific anime pages must have id nubmer to access information, titles get search results! 
'''def get_MAL_info2(RT_data_list) -> list:
    info_list = []
    for anime in RT_data_list:
        title = anime[0]
        # url here gets "full information from the API" getAnimeFullByld (https://docs.api.jikan.moe/#tag/anime/operation/getAnimeFullById"
        #url = f'https://api.jikan.moe/v4/anime/{modified_string}/full'
        url = f'https://api.jikan.moe/v4/anime?q={title}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            

            EnglishTitle = data['data']['titles'][3].get('title', 'null') 
            JpnTitle =  data['data']['titles'][2].get('title', 'null') 
            #checking if title grabbed from Rotten Tomatoes is the same as MAL search results
            if EnglishTitle == title or JpnTitle  == modified_string:
                MAL_ID = data['data']['titles'][3].get('title', 'null') 
                full_url = 'https://api.jikan.moe/v4/anime/{MAL_ID}/full'
                
                response2 = requests.get(full_url)
                if response2.status_code == 200:
                    data2 =  response2.json()
                    fullInfo = []
                    seasonScore = data2['data'].get('score', 'null') 
                    numSeasons = -1 #0 if movie
                    genres = []
                    studio = ''
                    numEpisodes = data2['data'].get('episodes', 'null')
                    releaseDate = data2['data']['aired'].get('string', 'null') # string formatted as 'Mon XX, XXXX to Mon XX, XXXX'
                    numReviews = data2['data'].get('scored_by', 'null')
                    studio = data2['data']['studios'].get('name', 'null')
                    for item in genres:
                       genre = data2['data']['genres'][item].get('name', 'null')
                       genres.append(genre)
                    
                    fullInfo.append((modified_string, seasonScore, genres, studio, numEpisodes, releaseDate, numReviews))
                    
                    
'''

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
            
            '''titles = data['data']['titles'] if 'titles' in data['data'] else []
            
            EnglishTitle = None
            JpnTitle = None
            for i in range(len(titles)):
                if titles[i]['type'] == 'English':
                    EnglishTitle = titles[i]['title']
                elif titles[i]['type'] == 'Japanese':
                    JpnTitle = titles[i]['title']
            '''

            # Checking if title grabbed from Rotten Tomatoes is the same as MAL search results
            #if EnglishTitle == modified_string or JpnTitle == modified_string:
            MAL_ID = data['data']['mal_id']
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
                raise Exception(f"Failed to match titles: {title}")
            
        else:
            raise Exception(f"Failed to retrieve data: {response.status_code}")
    
    return info_list



## CHAT HELPED WITH THIS 

'''def get_english_title(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and len(data['data']) > 0:
            # Get the first entry in the data
            first_entry = data['data'][0]
            titles = first_entry.get('titles', [])
            english_title = None
            for title in titles:
                if title['type'] == 'English':
                    english_title = title['title']
                    break
            return english_title
        else:
            raise Exception("No data found in the API response.")
    else:
        raise Exception(f"Failed to retrieve data: {response.status_code}")

api_url = "https://api.jikan.moe/v4/anime?q=blue%20exorcist"
english_title = get_english_title(api_url)
if english_title:
    print(f"English Title: {english_title}")
else:
    print("English title not found.")
'''
           
# original code, not sure if we want to continue with the method of grabbing titles and then inputing -- if we do, we can
# then go into the specific entries, grab their mal_id, and then 
'''def get_MAL_info(RT_data_list): 
    for anime in RT_data_list:
        title = anime[0]
        print(title)
        if re.search(title, r' '):
             modified_string = title.replace(" ", "-")
        else: 
            modified_string = title
        
        url = f'https://api.jikan.moe/v4/anime?q={modified_string}'
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            raise Exception(f"Failed to retrieve data: {response.status_code}")
'''
            
            
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