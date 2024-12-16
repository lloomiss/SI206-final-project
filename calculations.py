import json
import re
import requests
from bs4 import BeautifulSoup
import unittest
import sqlite3
import json
import os
import time
import matplotlib
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



def main():


    try:
        cur, conn =  set_up_database('anime.db')
        combined_select_n_CSV(conn, cur)
        

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()


