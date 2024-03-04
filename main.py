from flask import Flask, render_template, request, g, redirect, url_for
from urllib.parse import urlencode
import requests
import sqlite3
import os

app = Flask(__name__)
app.config['DATABASE'] = 'mtg-cards.db'

def create_table_if_not_exists():
    # Check if the database file exists
    if not os.path.exists(app.config['DATABASE']):
        # Connect to the SQLite database (it will be created if it doesn't exist)
        conn = sqlite3.connect(app.config['DATABASE'])

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Create a table for storing card information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                id TEXT PRIMARY KEY,
                name TEXT,
                rarity TEXT,
                image_uri_normal TEXT
            )
        ''')

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

@app.before_request
def before_request():
    if not hasattr(g, 'db_initialized'):
        create_table_if_not_exists()
        g.db_initialized = True

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('mtg-cards', None)
    if db is not None:
        db.close()

@app.teardown_appcontext
def close_database(error):
    close_db()

def save_card_to_db(card_data):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        INSERT INTO cards (id, name, rarity, image_uri_normal)
        VALUES (:id, :name, :rarity, :image_uri_normal)
    ''', {
        'id': card_data['id'],
        'name': card_data['name'],
        'rarity': card_data['rarity'],
        'image_uri_normal': card_data['image_uris']['normal']
    })

    db.commit()
    db.close()

def get_card_names_from_file():
    with open('card_names.txt', 'r') as file:
        card_names = [line.strip() for line in file.readlines()]
    return card_names

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_card_name = request.form['selected_card_name']

        # Encode the query parameter to handle special characters
        encoded_card_name = urlencode({'exact': selected_card_name})

        # Construct the API URL with the encoded parameter
        api_url = f"https://api.scryfall.com/cards/named?{encoded_card_name}"

        response = requests.get(api_url)

        if response.status_code == 200:
            card_data = response.json()

            # Save the card data to the database
            save_card_to_db(card_data)

            return redirect(url_for('index'))  # Redirect to the index route after adding the card
        else:
            return f"Error: Unable to fetch card information for '{selected_card_name}'."

    else:
        db = get_db()
        cursor = db.cursor()

        # Fetch all cards from the database
        query = "SELECT id, name, rarity, image_uri_normal FROM cards"
        cards = cursor.execute(query).fetchall()

        # Convert the rows to a list of dictionaries for easier template rendering
        card_data_list = [dict(card) for card in cards]

        with open('sets-mtg.txt', 'r') as file:
            sets = [line.strip() for line in file.readlines()]

        with open('card_names.txt', 'r') as file:
            card_names = [line.strip() for line in file.readlines()]

        return render_template('index.html', sets=sets, card_data_list=card_data_list, card_names=card_names)

if __name__ == "__main__":
    app.run(debug=True)