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


def avg_rating_by_genre():
    genres = ("Adventure", "Comedy", "Drama", "Fantasy", "Romance", "Sci-Fi", "Slice of Life", "Supernatural")
    score_means = {
        'MAL score': (7.9733, 7.7625, 7.385, 7.69, 7.545, 6.345, 8.17, 8.62),
        'RT popcornmeter': (8.7125, 8.8667, 7.6714, 8.9, 7.6, 6.8, 9.6, 9.6),
    }

    x = np.arange(len(genres))  # the label locations
    width = 0.35  # the width of the bars
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained')

    for attribute, measurement in score_means.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        ax.bar_label(rects, padding=3)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Average Rating (out of 10)')
    ax.set_title('Average Rating by Platform and Genre')
    ax.set_xticks(x + width / 2, genres)
    ax.legend(loc='upper left', ncols=2)
    ax.set_ylim(0, 10)  # Since scores are out of 10

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

    for attribute, measurement in scores.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
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
        #avg_rating_by_genre()
        top_5_results()

        

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()


