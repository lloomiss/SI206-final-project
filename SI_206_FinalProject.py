import json
import re
import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import time

##create table for the genres (to prevent duplicate string)
##sort by ID (join on id)
##Getting rid of null values from csv (or instead, include an if statment to skip over the null if there is one)
##Getting rid of title from RT_table, and combine data
## 
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
    
    #makes sure no null titles are in the function
    if lower_title == 'null' and popcornmeter == 'NULL' and tomatometer == 'NULL':
        return None
    
    else: 
         return (lower_title, tomatometer, popcornmeter)


def get_RT_info(soup, start, stop) -> list:
    # initialize list of tuples to return
    RT_data_list = []

    # get the a and div tags
    a_data_tags = soup.find_all('a', {'data-track': 'scores'}, {'data-qa': 'discovery-media-list-item-caption'})
    div_data_tags = soup.find_all('div', {'data-track': 'scores'}, {'data-qa': 'discovery-media-list-item-caption'})

    # combine the a and div tags into one list
    data_tags = a_data_tags + div_data_tags

    # iterate through all the tags, extract the data, and append each tuple to RT_data_list
    if data_tags:
        for tag in data_tags[start:stop]:
            RT_data_list.append(tomato_extract(tag))
    else:
        print("No data found")

    print(f"Extracted {len(RT_data_list)} items from Rotten Tomatoes")
    return RT_data_list


def get_MAL_info(RT_data_list) -> list:
    info_list = []
    for anime in RT_data_list:
        RT_title = anime[0]
        #if RT_title == 'null':
            #continue
        #elif RT_title != 'null' and RT_title != '':
        print(f"Processing {RT_title} from RT_data_list")

        # Getting the search results of our title from RT_data_list
        url = f'https://api.jikan.moe/v4/anime?q={RT_title}'
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                fullInfo = []
                titleMatch = False
                for entry in data['data']:
                    time.sleep(2)
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
                            genre1 = genres_list[0].get('name', 'null') if genres_list else 'null'
                            studio_list = data2['data'].get('studios', [])
                            studio = studio_list[0].get('name', 'null') if studio_list else 'null'
                            numEpisodes = data2['data'].get('episodes', 'null')
                            releaseDate = data2['data']['aired'].get('string', 'null')
                            numReviews = data2['data'].get('scored_by', 'null')

                            fullInfo.append((RT_title, seasonScore, genre1, studio, numEpisodes, releaseDate, numReviews))
                            info_list.append(fullInfo)
                        else:
                            print(f"Failed to retrieve full data for MAL ID: {MAL_ID}. Response code: {response2.status_code}")
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
            print(f"No data found for title: {RT_title}")
    else:
        print(f"Failed to retrieve data: {response.status_code}")

    print(info_list)
    return info_list


def set_up_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(os.path.join(path, db_name))
    cur = conn.cursor()
    return cur, conn


def set_up_RT_table(data, cur, conn):
    meters_list = []
    for anime in data:
        #title = anime[0]
        tomatometer = anime[1]
        popcornmeter = anime[2]
        meters_list.append((tomatometer, popcornmeter))
    
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS RT_meters (
            anime_id INTEGER PRIMARY KEY,
            tomatometer INTEGER,
            popcornmeter INTEGER
        )
        '''
    )
    conn.commit()  # Ensure table creation is committed
    print("Created table RT_meters")

    for i in range(len(data)):
        cur.execute(
            '''
            INSERT OR IGNORE INTO RT_meters (tomatometer, popcornmeter) VALUES (?, ?)
            ''',
            (meters_list[i][1], meters_list[i][2])
        )
    conn.commit()
    print("Inserted data into RT_meters")


def set_up_genres_table(data, cur, conn):
    genre_list = []
    for anime in data:
        genre1 = anime[2]
        if genre1 not in genre_list:
            genre_list.append(genre1)
       
    cur.execute(
        "CREATE TABLE IF NOT EXISTS Genres (id INTEGER PRIMARY KEY, genre TEXT UNIQUE)"
    )
    for i in range(len(genre_list)):
        cur.execute(
            "INSERT OR IGNORE INTO Genres (id,genre) VALUES (?,?)", (i,
                                                                   genre_list[i])
        )
    conn.commit()

def set_up_MAL_table(data, cur, conn):
    cur.execute (
        '''
        CREATE TABLE IF NOT EXISTS MAL (
        anime_id INTEGER PRIMARY KEY,
        title TEXT,
        score TEXT,
        genre_id INTEGER,
        studio TEXT,
        numEpi INTEGER,
        releaseDate TEXT,
        numReviews INTEGER
        )
        '''
    )
    for anime in data:
        title = anime[0]
        MALscore = anime[1]
        genre = anime[2]
        studio = anime[3]
        numEpisodes = anime[4]
        releaseDate = anime[5]
        numReviews = anime[6]
        cur.execute("SELECT id FROM Genres WHERE genre = ?", (genre, ))
        genre_id = cur.fetchone()
        cur.execute(
            '''
            INSERT OR IGNORE INTO MAL (
            title, MALscore, genre_id, studio, numEpisodes, releaseDate, numReviews)
            )
            VALUES ( ?, ?, ?, ?, ?, ?, ?)
            ''', (title, MALscore, genre_id, studio, numEpisodes, releaseDate, numReviews)
        )
        conn.commit()

    print("Created table MAL")

def set_up_combined_table(data, cur, conn):
    # Create the combined table if it doesn't exist
    ## i feel like this might raise issue
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS combined_anime_data (
        anime_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        score REAL,
        genre TEXT,
        studio TEXT,
        numEpi INTEGER,
        releaseDate TEXT,
        numReviews INTEGER,
        tomatometer REAL,
        popcornmeter REAL
    );
    '''
    cur.execute(create_table_query)
    
    # Define the query to fetch combined data from both tables
    query1 = '''
    SELECT
        mal.title, mal.score AS MALscore, mal.genre, mal.studio,
        mal.numEpi, mal.releaseDate, mal.numReviews,
        rt.tomatometer, rt.popcornmeter
    FROM RT_meters rt
    INNER JOIN MAL mal ON rt.anime_id = mal.anime_id
    WHERE mal.anime_id = ?
    '''
    
    # We need another query to insert data into combined_anime_data
    insert_query = '''
    INSERT INTO combined_anime_data (
        title, score, genre, studio, numEpi,
        releaseDate, numReviews, tomatometer, popcornmeter
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    
    # Assuming data contains anime_id's; loop over them
    for i in range(len(data)):
        cur.execute(query1, (i,))
        row = cur.fetchone()
        if row:
            cur.execute(insert_query, row)
    
    # Commit changes and close connection
    conn.commit()

# Function to get the number of rows processed so far
def get_rows_processed(cursor):
    cursor.execute("SELECT rows_processed FROM progress_tracker WHERE id = 1")
    result = cursor.fetchone()
    if result is None:
        cursor.execute("INSERT INTO progress_tracker (id, rows_processed) VALUES (1, 0)")
        return 0
    return result[0]

# Function to update the number of rows processed
def update_rows_processed(cursor, rows_processed):
    cursor.execute("UPDATE progress_tracker SET rows_processed = ? WHERE id = 1", (rows_processed,))

# Function to create the progress tracking table
def create_progress_tracker_table(cur, conn):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS progress_tracker (
        id INTEGER PRIMARY KEY,
        rows_processed INTEGER
    )""")
    conn.commit()

# Function to upload a batch of rows to the database
def upload_batch(data, start, batch_size, cur, conn):
    end = min(start + batch_size, len(data))
    batch = data[start:end]
    
    # Process and insert data into MAL table
    for anime in batch:
        if len(anime) != 1:  # Ensure that the anime list has the correct structure
            print(f"Unexpected structure in anime data: {anime}")
            continue

        anime_data = anime[0]
        if len(anime_data) != 7:  # Ensure that the data has exactly 7 elements
            print(f"Unexpected number of elements in anime data: {anime_data}")
            continue

        title, score, genres, studio, numEpisodes, releaseDate, numReviews = anime_data
        genres = ', '.join(genres) if isinstance(genres, list) else genres
        cur.execute("SELECT id FROM Genres WHERE genre = ?", (genres, ))
        genre_id = cur.fetchone()

        cur.execute(
            '''
            INSERT OR IGNORE INTO MAL (
                title, score, genre_id, studio, numEpi, releaseDate, numReviews
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (title, score, genre_id, studio, numEpisodes, releaseDate, numReviews)
        )
    conn.commit()
    return end - start

def main():
    # Get the Rotten Tomatoes page
    url = 'https://www.rottentomatoes.com/browse/tv_series_browse/genres:anime~sort:popular?page=5'
    r = requests.get(url)
    
    if r.status_code == 200:
        html = r.text
        tomato_soup = BeautifulSoup(html, 'html.parser')
    else:
        print('Invalid URL')
        return

    cur, conn = set_up_database("anime.db")
    
    # Ensure the progress_tracker table exists
    create_progress_tracker_table(cur, conn)
    
    rows_processed = get_rows_processed(cur)
    batch_size = 25
    max_rows = 144  # Assuming 144 is the max number of items in the list
    
    stop = min(rows_processed + batch_size, max_rows)
    
    # Get new rows of RT info and corresponding MAL info
    RT_info = get_RT_info(tomato_soup, rows_processed, stop)
    new_data = get_MAL_info(RT_info)
    
    # Set up the RT table if not already done
    if rows_processed == 0:
        set_up_RT_table(RT_info, cur, conn)
        set_up_genres_table(new_data, cur, conn)
        set_up_MAL_table(new_data,cur,conn)
        
    # Upload the new batch of data
    rows_uploaded = upload_batch(new_data, 0, batch_size, cur, conn)
    
    # Update the progress tracker
    update_rows_processed(cur, rows_processed + rows_uploaded)
    
    print(f"Uploaded {rows_uploaded} rows to the database.")

if __name__ == "__main__":
    main()