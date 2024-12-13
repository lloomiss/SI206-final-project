import json
import re
import requests
from bs4 import BeautifulSoup
import unittest
import sqlite3
import json
import os
import time


def tomato_extract(tag):
    # get the tags for anime titles, tomatometers, and popcornmeters
    title_tag = tag.find('span', {'data-qa': 'discovery-media-list-item-title'})
    tomatometer_tag = tag.find('rt-text', {'slot': 'criticsScore'})
    popcornmeter_tag = tag.find('rt-text', {'slot': 'audienceScore'})

    # get the text or return a NULL value if no text
    title = title_tag.get_text(strip=True) if title_tag else "NULL"
    lower_title = title.lower()
    
    if tomatometer_tag:
        tomatometer_text = tomatometer_tag.get_text(strip=True)
        if tomatometer_text.endswith('%'):
            tomatometer = float(tomatometer_text[:-1]) / 10
        else:
            tomatometer = "NULL"
    else:
        tomatometer = "NULL"
        
    if popcornmeter_tag:
        popcornmeter_text = popcornmeter_tag.get_text(strip=True)
        if popcornmeter_text.endswith('%'):
            popcornmeter = float(popcornmeter_text[:-1]) / 10
        else:
            popcornmeter = "NULL"
    else:
        popcornmeter = "NULL"
    
    return (lower_title, tomatometer, popcornmeter)

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
    
    return RT_data_list

def get_MAL_info(RT_data_list, start, stop) -> list:
    info_list = []
    for anime in RT_data_list[start:stop]:
        RT_title = anime[0].lower()
        # Getting the search results of our title from RT_data_list
        url = f'https://api.jikan.moe/v4/anime?q={RT_title}'
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                fullInfo = []
                titleMatch = False
                for entry in data['data']:
                    MAL_titles = entry.get('titles')
                    for MAL_title in MAL_titles:
                        lowerMAL = MAL_title['title'].lower()
                        if lowerMAL == RT_title:
                            titleMatch = True
                            break
                    if titleMatch:
                        MAL_ID = entry.get('mal_id')
                        full_url = f'https://api.jikan.moe/v4/anime/{MAL_ID}/full'
                        
                        # Delay in requests
                        time.sleep(2)
                        
                        response2 = requests.get(full_url)
                        if response2.status_code == 200:
                            data2 = response2.json()
                            seasonScore = data2['data'].get('score', 'null')
                            genres_list = data2['data'].get('genres', [])
                            genre1 = genres_list[0].get('name', 'null') if genres_list else 'null' #[genre.get('name', 'null') for genre in genres_list]
                            studio_list = data2['data'].get('studios', [])
                            studio = studio_list[0].get('name', 'null') if studio_list else 'null'
                            numEpisodes = data2['data'].get('episodes', 'null')
                            releaseDate = data2['data']['aired'].get('string', 'null')
                            numReviews = data2['data'].get('scored_by', 'null')
                            
                            fullInfo.append((RT_title, seasonScore, genre1, studio, numEpisodes, releaseDate, numReviews))
                            info_list.append(fullInfo)
                        else:
                            raise Exception(f"Failed to retrieve full data for MAL ID: {MAL_ID}. Response code: {response2.status_code}")
                        break
                if not titleMatch:
                    seasonScore = 'null'
                    genres = []
                    studio = 'null'
                    numEpisodes = 'null'
                    releaseDate = 'null'
                    numReviews = 'null'
                    fullInfo.append((RT_title, seasonScore, genres, studio, numEpisodes, releaseDate, numReviews))
                    info_list.append(fullInfo)
            else:
                raise Exception(f"No data found for title: {RT_title}")
        else:
            raise Exception(f"Failed to retrieve data: {response.status_code}")

    print(info_list)
    return info_list

def set_up_database(db_name):
    """
    Sets up a SQLite database connection and cursor.

    Parameters
    -----------------------
    db_name: str
        The name of the SQLite database.

    Returns
    -----------------------
    Tuple (Cursor, Connection):
        A tuple containing the database cursor and connection objects.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    cur = conn.cursor()
    return cur, conn

def create_MAL_table(cur, conn):
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS Anime (
            anime_id INTEGER PRIMARY KEY,
            title TEXT,
            score TEXT,
            genre TEXT,
            studio TEXT,
            numEpi INTEGER,
            releaseDate TEXT,
            numReviews INTEGER
        )
        '''
    )

    conn.commit()
    
def chunk_data(data, chunk_size):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

def insert_data(data, cur, conn):
    chunk_size = 25
    for chunk in chunk_data(data, chunk_size):
        for anime in chunk:
            title = anime[0]
            score = anime[1]
            genre = anime[2]
            studio = anime[3]
            numEpisodes = anime[4]
            releaseDate = anime[5]
            numReviews = anime[6]

            cur.execute(
                '''
                INSERT OR IGNORE INTO Anime (
                    title, score, genre, studio, numEpi, releaseDate, numReviews
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (title, score, genre, studio, numEpisodes, releaseDate, numReviews)
            )


    conn.commit()
            
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

    RT_info = get_RT_info(tomato_soup)

    try:
        anime_details = get_MAL_info(RT_info, 0, 50)
        cur, conn = set_up_database("anime.db")
        create_MAL_table(cur, conn)
        insert_data(anime_details, cur, conn)
        print(anime_details)
    except Exception as e:
        print(e)

''' class TestAllMethods(unittest.TestCase):
    def setUp(self):
        path = os.path.dirname(os.path.abspath(__file__))
        self.conn = sqlite3.connect(path + "/" + "pokemon.db") # we don't have our own test database
        self.cur = self.conn.cursor()
        self.data = read_data_from_file("pokemon.json") 


    def test_get_MAL_Info (self):
        ## what is our expected output?
        #self.assertEqual(x, x)
'''
if __name__ == "__main__":
    main()