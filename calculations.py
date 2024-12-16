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
    genres = ("Action", "Adventure", "Comedy", "Drama", "Fantasy", "Romance", "Sci-Fi", "Slice of Life", "Supernatural")
    
    genre_data = {genre: {'MAL_total': 0, 'RT_total': 0, 'count': 0} for genre in genres}
    
    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # Skip the header
        
        for row in reader:
            genre = row[3]
            if genre in genre_data:
                genre_data[genre]['MAL_total'] += float(row[2])  # Assuming column 2 is MAL score
                genre_data[genre]['RT_total'] += float(row[9])   # Assuming column 9 is RT popcornmeter
                genre_data[genre]['count'] += 1
    
    avg_MAL_action = genre_data['Action']['MAL_total'] / genre_data['Action']['count'] if genre_data['Action']['count'] > 0 else 0
    avg_RT_action = genre_data['Action']['RT_total'] / genre_data['Action']['count'] if genre_data['Action']['count'] > 0 else 0
    
    score_means = {
        'MAL score': (avg_MAL_action, 7.9733, 7.7625, 7.385, 7.69, 7.545, 6.345, 8.17, 8.62),
        'RT popcornmeter': (avg_RT_action, 8.7125, 8.8667, 7.6714, 8.9, 7.6, 6.8, 9.6, 9.6),
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



def main():


    try:
        #cur, conn =  set_up_database('anime.db')
        #combined_select_n_CSV(conn, cur)
        avg_rating_by_genre("combined_anime_data_output.csv")
        

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()


