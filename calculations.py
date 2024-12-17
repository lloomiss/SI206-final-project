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
    return csv_file


def avg_rating_by_genre(csv_file):
    # genres with more than 1000 entries on myanimelist
    genres = ("Drama", "Action", "Adventure", "Sci-Fi",  "Fantasy",  "Comedy", "Sports", "Supernatural", "Mystery", "Romance", "Slice of Life")
    genre_ids = (2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13)
    
    genre_mapping = dict(zip(genres, genre_ids))
    
    genre_data = {genre_id: {'MAL_total': 0, 'RT_total': 0, 'count': 0} for genre_id in genre_ids}
    
    with open(csv_file, newline='', encoding='latin1') as csvfile:  # Use 'latin1' encoding here
        reader = csv.reader(csvfile)
        header = next(reader)  # Skip the header

        for row in reader:
            genre_name = row[3]  # Assuming genre name is in the 4th column
            genre_id = genre_mapping.get(genre_name)
            if genre_id in genre_data:
                try:
                    mal_score = float(row[2]) if row[2] else None
                except ValueError:  # In case it cannot convert to float
                    mal_score = None

                try:
                    rt_popcorn = float(row[9]) if row[9] else None
                except ValueError:  # In case it cannot convert to float
                    rt_popcorn = None

                if mal_score is not None:
                    genre_data[genre_id]['MAL_total'] += mal_score
                if rt_popcorn is not None:
                    genre_data[genre_id]['RT_total'] += rt_popcorn
                genre_data[genre_id]['count'] += 1

    # Calculate averages
    for genre_id in genre_ids:
        if genre_data[genre_id]['count'] > 0:
            genre_data[genre_id]['MAL_avg'] = genre_data[genre_id]['MAL_total'] / genre_data[genre_id]['count']
            genre_data[genre_id]['RT_avg'] = genre_data[genre_id]['RT_total'] / genre_data[genre_id]['count']
        else:
            genre_data[genre_id]['MAL_avg'] = 0
            genre_data[genre_id]['RT_avg'] = 0

    score_means = {
        'MyAnimeList Score': [genre_data[genre_id]['MAL_avg'] for genre_id in genre_ids],
        'Rotten Tomatoes Popcornmeter': [genre_data[genre_id]['RT_avg'] for genre_id in genre_ids]
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
        'Score': (5.89, 8.46, 8.27, 8.61, 9.32),
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
    ax.set_title('Current Top 5 Anime Ratings')
    ax.set_xticks(x + width / 2, anime)
    ax.legend(loc='upper left', ncols=2)
    ax.set_ylim(0, 11)  # Since scores are out of 10

    plt.show()

def top_5_most_reviewed_anime(csv_file):
    anime_data = []

    # Step 1: Read the CSV file and extract the relevant information
    try:
        with open(csv_file, newline='', encoding='latin1') as csvfile:  # Try 'utf-8' if 'latin1' does not work
            reader = csv.reader(csvfile)
            header = next(reader)  # Skip the header
            print(f"CSV Header: {header}")

            for row in reader:
                # Print each row for debugging
                print(f"CSV Row: {row}")
                
                try:
                    anime_id = row[0]
                    score = float(row[1]) if row[1] else None
                    genre_id = int(row[2]) if row[2] else None
                    num_episodes = int(row[3]) if row[3] else None
                    release_date = row[4]
                    num_reviews = int(row[5]) if row[5] else 0
                    tomatometer = float(row[6]) if row[6] else None
                    popcornmeter = float(row[7]) if row[7] else None

                    anime_data.append({
                        'anime_id': anime_id,
                        'score': score,
                        'genre_id': genre_id,
                        'num_episodes': num_episodes,
                        'release_date': release_date,
                        'num_reviews': num_reviews,
                        'tomatometer': tomatometer,
                        'popcornmeter': popcornmeter
                    })
                except ValueError as e:
                    print(f"ValueError: {e} in row {row}")
                    continue  # In case of conversion errors, skip the row

        # Debug print to verify data is being read correctly
        print(f"Total anime entries read: {len(anime_data)}")

        if not anime_data:
            print("No anime data available.")
            return

        # Step 2: Sort the anime data by num_reviews in descending order
        anime_data_sorted = sorted(anime_data, key=lambda x: x['num_reviews'], reverse=True)

        # Step 3: Select the top 5 most reviewed anime
        top_5_anime = anime_data_sorted[:5]

        # Debug print to verify top 5 data
        for idx, anime in enumerate(top_5_anime):
            print(f"{idx + 1}: {anime['anime_id']} with {anime['num_reviews']} reviews")

        # Step 4: Create the bar graph with the extracted data
        anime_titles = [anime['anime_id'] for anime in top_5_anime]
        scores = {
            'MAL score': [anime['score'] for anime in top_5_anime],
            'Tomatometer': [anime['tomatometer'] for anime in top_5_anime],
            'Popcornmeter': [anime['popcornmeter'] for anime in top_5_anime]
        }

        x = np.arange(len(anime_titles))  # the label locations
        width = 0.15  # the width of the bars
        multiplier = 0

        fig, ax = plt.subplots(layout='constrained')

        colors = {'MAL score': '#2e51a2', 'Tomatometer': '#fa320a', 'Popcornmeter': '#f9d320'}

        for attribute, measurement in scores.items():
            offset = width * multiplier
            rects = ax.bar(x + offset, measurement, width, label=attribute, color=colors[attribute])
            ax.bar_label(rects, padding=3)
            multiplier += 1

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Rating (out of 10)')
        ax.set_title('Top 5 Most Reviewed Anime Ratings')
        ax.set_xticks(x + width / 2, anime_titles)
        ax.legend(loc='upper left', ncols=2)
        ax.set_ylim(0, 11)  # Since scores are out of 10

        plt.show()

    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    try:
        #cur, conn = set_up_database('anime.db')
        #csv_file = combined_select_n_CSV(conn, cur)
        #avg_rating_by_genre('combined_anime_data_output.csv')
        #top_5_results()
        top_5_most_reviewed_anime('combined_anime_data_output.csv')
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()

