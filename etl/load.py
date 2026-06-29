import mysql.connector as conn
import pandas as pd
from mysql.connector import Error

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "mysql@naveen45",
    "database": "stattrack"
}

"""
Connects to MySQL and loads data from CSVs into pre-existing tables.
Assumes the schema has already been created. Run the schema.sql file before running this file
"""
try:
    with conn.connect(**db_config) as connection:
        cursor = connection.cursor()
        print("Connection to MySQL successful.")

        print("--- Loading Data from CSVs (in strict order) ---")
        
        files_to_load = [
            {'name': 'teams', 'file': 'teams.csv', 'query': 'INSERT INTO teams (team_id, team_name) VALUES (%s, %s)'},
            {'name': 'agents', 'file': 'agents.csv', 'query': 'INSERT INTO agents (agent_id, agent_name, role) VALUES (%s, %s, %s)'},
            {'name': 'players', 'file': 'players.csv', 'query': 'INSERT INTO players (player_id, player_name, team_id) VALUES (%s, %s, %s)'},
            {'name': 'games', 'file': 'games.csv', 'query': 'INSERT INTO games (game_id, team1_id, team2_id, map, winner_id, w_score, l_score) VALUES (%s, %s, %s, %s, %s, %s, %s)'},
            {'name': 'stats', 'file': 'stats.csv', 'query': 'INSERT INTO stats (player_id, game_id, agent_id, rating, acs, kills, deaths, assists, kast_percent, adr, hs_percent, first_kills, first_deaths) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'}
        ]

        for item in files_to_load:
            df = pd.read_csv(item['file'])
            data_tuples = [tuple(row) for row in df.itertuples(index=False)]
            cursor.executemany(item['query'], data_tuples)
            connection.commit()
            print(f"Loaded {cursor.rowcount} records into '{item['name']}'.")

        print("All data loaded successfully.")
        cursor.close()

except FileNotFoundError as e:
    print(f"The file '{e.filename}' was not found.")
except Error as e:
    print(f"A database error occurred: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
