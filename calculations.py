import json
import re
import unittest
import sqlite3
import json
import os
import time
import matplotlib.pyplot as plt
import numpy as np
import csv


def set_up_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    cur = conn.cursor()
    return cur, conn


def combined_select_n_CSV(conn, cur):
    query = 'SELECT * FROM combined_anime_data'
    cur.execute(query)
    rows = cur.fetchall()
    column_names = [description[0] for description in cur.description]

    csv_file = 'combined_anime_data_output.csv'  # Output CSV file name
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        # Optional: Write the column headers
        writer.writerow(column_names)
        # Write the data rows
        writer.writerows(rows)
    conn.close()

    print(f"Data has been written to {csv_file}")


def avg_rating_by_genre(csv_file):
    # genres with more than 1000 entries on myanimelist
    genres = ("Action", "Adventure", "Comedy", "Drama", "Fantasy", "Romance", "Sci-Fi", "Slice of Life", "Supernatural")
    
    genre_data = {genre: {'MAL_total': 0, 'RT_total': 0, 'count': 0} for genre in genres}
    
    with open(csv_file, newline='', encoding='latin1') as csvfile:  # Use 'latin1' encoding here
        reader = csv.reader(csvfile)
        header = next(reader)  # Skip the header

        for row in reader:
            genre = row[3]
            if genre in genre_data:
                try:
                    mal_score = float(row[2]) if row[2] else None
                except ValueError:  # In case it cannot convert to float
                    mal_score = None

                try:
                    rt_popcorn = float(row[9]) if row[9] else None
                except ValueError:  # In case it cannot convert to float
                    rt_popcorn = None

                if mal_score is not None:
                    genre_data[genre]['MAL_total'] += mal_score
                if rt_popcorn is not None:
                    genre_data[genre]['RT_total'] += rt_popcorn
                genre_data[genre]['count'] += 1

    # Calculate averages
    for genre in genres:
        if genre_data[genre]['count'] > 0:
            genre_data[genre]['MAL_avg'] = genre_data[genre]['MAL_total'] / genre_data[genre]['count']
            genre_data[genre]['RT_avg'] = genre_data[genre]['RT_total'] / genre_data[genre]['count']
        else:
            genre_data[genre]['MAL_avg'] = 0
            genre_data[genre]['RT_avg'] = 0

    score_means = {
        'MyAnimeList Score': [genre_data[genre]['MAL_avg'] for genre in genres],
        'Rotten Tomatoes Popcornmeter': [genre_data[genre]['RT_avg'] for genre in genres]
    }

    x = np.arange(len(genres))  # the label locations
    width = 0.35  # the width of the bars
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained')

    colors = {'MyAnimeList Score': '#2e51a2', 'Rotten Tomatoes Popcornmeter': '#fa320a'}

    for attribute, measurement in score_means.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute, color=colors[attribute])
        ax.bar_label(rects, padding=3)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Average Rating (out of 10)')
    ax.set_title('Average Rating by Platform and Genre')
    ax.set_xticks(x + width / 2, genres)
    ax.legend(loc='upper left', ncols=2)
    ax.set_ylim(0, 11)  # Since scores are out of 10

    plt.show()


def top_5_results():
    anime = ("Uzumaki", "Pluto", "Solo Leveling", "Delicious in Dungeon", "Frieren: Beyond Journey's End")
    scores = {
        'MAL score': (5.89, 8.46, 8.27, 8.61, 9.32),
        'Tomatometer': (8, 10, 10, 10, 10),
        'Popcornmeter': (7, 9.5, 8.4, 9.6, 9.5)
    }

    x = np.arange(len(anime))  # the label locations
    width = 0.15  # the width of the bars
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained')

    colors = {'Score': '#2e51a2', 'Tomatometer': '#fa320a', 'Popcornmeter': '#f9d320'}

    for attribute, measurement in scores.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute, color=colors[attribute])
        ax.bar_label(rects, padding=3)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Rating (out of 10)')
    ax.set_title('Current Top 10 Anime Ratings')
    ax.set_xticks(x + width / 2, anime)
    ax.legend(loc='upper left', ncols=2)
    ax.set_ylim(0, 11)  # Since scores are out of 10

    plt.show()



def main():


    try:
        #cur, conn =  set_up_database('anime.db')
        #combined_select_n_CSV(conn, cur)
        avg_rating_by_genre("combined_anime_data_output.csv")
        #top_5_results()

        

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()


