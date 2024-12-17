import json
import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import time


def tomato_extract(tag):
    title_tag = tag.find('span', {'data-qa': 'discovery-media-list-item-title'})
    tomatometer_tag = tag.find('rt-text', {'slot': 'criticsScore'})
    popcornmeter_tag = tag.find('rt-text', {'slot': 'audienceScore'})
    title = title_tag.get_text(strip=True) if title_tag else "NULL"
    lower_title = title.lower()
    if tomatometer_tag:
        tomatometer_text = tomatometer_tag.get_text(strip=True)
        tomatometer = float(tomatometer_text[:-1]) / 10 if tomatometer_text.endswith('%') else "NULL"
    else:
        tomatometer = "NULL"
    if popcornmeter_tag:
        popcornmeter_text = popcornmeter_tag.get_text(strip=True)
        popcornmeter = float(popcornmeter_text[:-1]) / 10 if popcornmeter_text.endswith('%') else "NULL"
    else:
        popcornmeter = "NULL"
    if lower_title == 'null' and popcornmeter == 'NULL' and tomatometer == 'NULL':
        return None
    else:
        return (lower_title, tomatometer, popcornmeter)


def get_RT_info(soup, start, stop) -> list:
    RT_data_list = []
    a_data_tags = soup.find_all('a', {'data-track': 'scores'}, {'data-qa': 'discovery-media-list-item-caption'})
    div_data_tags = soup.find_all('div', {'data-track': 'scores'}, {'data-qa': 'discovery-media-list-item-caption'})
    data_tags = a_data_tags + div_data_tags
    if data_tags:
        for tag in data_tags[start:stop]:
            extracted_data = tomato_extract(tag)
            if extracted_data:
                RT_data_list.append(extracted_data)
    else:
        print("No data found")
    print(f"Extracted {len(RT_data_list)} items from Rotten Tomatoes")
    return RT_data_list


def get_MAL_info(RT_data_list) -> list:
    info_list = []
    for anime in RT_data_list:
        if anime is None: #accounts for assigning of none value from the tomato extract function
            continue
        if len(anime) < 1:
            print(f"Invalid length of anime tuple: {anime}")
            continue
        RT_title = anime[0]
        print(f"Processing {RT_title} from RT_data_list")
        url = f'https://api.jikan.moe/v4/anime?q={RT_title}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                titleMatch = False
                for entry in data['data']:
                    time.sleep(2)
                    MAL_titles = entry.get('titles')
                    for MAL_title in MAL_titles:
                        lowerMAL = MAL_title['title'].lower()
                        if lowerMAL == RT_title:
                            titleMatch = True
                            break ## stops the loop -- transfering to the next statment
                    if titleMatch:
                        MAL_ID = entry.get('mal_id')
                        full_url = f'https://api.jikan.moe/v4/anime/{MAL_ID}/full'
                        time.sleep(2)
                        response2 = requests.get(full_url)
                        if response2.status_code == 200:
                            data2 = response2.json()
                            seasonScore = data2['data'].get('score', 'null')
                            genres_list = data2['data'].get('genres', [])
                            genre1 = genres_list[0].get('name', 'null') if genres_list else 'null'
                            studio_list = data2['data'].get('studios', [])
                            studio = studio_list[0].get('name', 'null') if studio_list else 'null'
                            numEpisodes = data2['data'].get('episodes', 'null')
                            releaseDate = data2['data']['aired'].get('string', 'null')
                            numReviews = data2['data'].get('scored_by', 'null')
                            info_list.append((RT_title, seasonScore, genre1, studio, numEpisodes, releaseDate, numReviews))
                        else:
                            print(f"Failed to retrieve full data for MAL ID: {MAL_ID}. Response code: {response2.status_code}")
                        break
                if not titleMatch:
                    info_list.append((RT_title, 'null', 'null', 'null', 'null', 'null', 'null'))
        else:
            print(f"No data found for title: {RT_title}")
    return info_list


def set_up_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(os.path.join(path, db_name))
    cur = conn.cursor()
    return cur, conn


def create_tables(cur, conn):
    # Creation handled without inserting data to avoid duplication during batch upload
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS RT_meters (
            anime_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tomatometer REAL,
            popcornmeter REAL
        )
        '''
    )
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS Genres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            genre TEXT UNIQUE
        )'''
    )
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS MAL (
            anime_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            score REAL,
            genre_id INTEGER,
            studio TEXT,
            numEpi INTEGER,
            releaseDate TEXT,
            numReviews INTEGER,
            FOREIGN KEY (genre_id) REFERENCES Genres(id)
        )
        '''
    )
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS progress_tracker (
            id INTEGER PRIMARY KEY,
            rows_processed INTEGER
        )
        '''
    )
    cur.execute("INSERT OR IGNORE INTO progress_tracker (id, rows_processed) VALUES (1, 0)")
    conn.commit()


def get_rows_processed(cur):
    cur.execute("SELECT rows_processed FROM progress_tracker WHERE id = 1")
    result = cur.fetchone()
    if result:
        return result[0]
    return 0


def update_rows_processed(cur, conn, rows_processed):
    cur.execute("UPDATE progress_tracker SET rows_processed = ? WHERE id = 1", (rows_processed,))
    conn.commit()


def upload_batch(RT_info, MAL_info, cur, conn):
    if not RT_info or not MAL_info:
        print("No data to upload.")
        return 0

    rows_uploaded = 0

    # Upload RT data
    for row in RT_info:
        if row == None or len(row) != 3:
            print(f"Skipping invalid row in RT data: {row}")
            continue
        tomatometer, popcornmeter = row[1:3]
        cur.execute(
            '''
            INSERT OR IGNORE INTO RT_meters (tomatometer, popcornmeter) VALUES (?, ?)
            ''', (tomatometer, popcornmeter)
        )
    # Upload MAL data
    for anime in MAL_info:
        if not anime or len(anime) != 7:
            print(f"Skipping invalid anime data: {anime}")
            continue
        title, score, genre, studio, numEpisodes, releaseDate, numReviews = anime
        cur.execute("SELECT id FROM Genres WHERE genre = ?", (genre,))
        genre_id = cur.fetchone()
        if not genre_id:
            cur.execute("INSERT INTO Genres (genre) VALUES (?)", (genre,))
            conn.commit()
            cur.execute("SELECT id FROM Genres WHERE genre = ?", (genre,))
            genre_id = cur.fetchone()[0]
        else:
            genre_id = genre_id[0]
        
        cur.execute(
            '''
            INSERT OR IGNORE INTO MAL (
                title, score, genre_id, studio, numEpi, releaseDate, numReviews
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (title, score, genre_id, studio, numEpisodes, releaseDate, numReviews)
        )
        rows_uploaded += 1
        print(rows_uploaded)

    conn.commit()
    return rows_uploaded

def set_up_combined_tables(cur, conn):
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS combined_anime_data (
            anime_id INTEGER PRIMARY KEY AUTOINCREMENT,
            score REAL,
            genre_id INTEGER,
            studio TEXT,
            numEpi INTEGER,
            releaseDate TEXT,
            numReviews INTEGER,
            tomatometer REAL,
            popcornmeter REAL,
            FOREIGN KEY (genre_id) REFERENCES Genres(id)
        )
        '''
    )
    
    conn.commit()

    cur.execute(
        '''
        INSERT OR IGNORE INTO combined_anime_data (
            anime_id, score, genre_id, studio, numEpi, releaseDate, numReviews, tomatometer, popcornmeter
        )
        SELECT
            MAL.anime_id, MAL.score, MAL.genre_id, MAL.studio, MAL.numEpi, MAL.releaseDate, MAL.numReviews, RT_meters.tomatometer, RT_meters.popcornmeter
        FROM MAL
        INNER JOIN RT_meters ON MAL.anime_id = RT_meters.anime_id
        '''
    )

    conn.commit()



def main():
    url = 'https://www.rottentomatoes.com/browse/tv_series_browse/genres:anime~sort:popular?page=5'
    response = requests.get(url)
    
    if response.status_code == 200:
        html = response.text
        tomato_soup = BeautifulSoup(html, 'html.parser')
    else:
        print('Invalid URL')
        return

    cur, conn = set_up_database("anime.db")
    create_tables(cur, conn)

    rows_processed = get_rows_processed(cur)
    batch_size = 25
    max_rows = 144

    stop = min(rows_processed + batch_size, max_rows)
    RT_info = get_RT_info(tomato_soup, rows_processed, stop)
    MAL_info = get_MAL_info(RT_info)

    rows_uploaded = upload_batch(RT_info, MAL_info, cur, conn)
    update_rows_processed(cur, conn, rows_processed + rows_uploaded)

    print(f"Uploaded {rows_uploaded} rows to the database.")

    set_up_combined_tables(cur, conn)

if __name__ == "__main__":
    main()