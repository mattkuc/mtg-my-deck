from flask import Flask, render_template, request, g, redirect, url_for, jsonify
from urllib.parse import urlencode
import requests
import sqlite3
import os
import json

app = Flask(__name__, static_url_path='/static')
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
                image_uri_normal TEXT,
                booster INTEGER,
                cardmarket_id INTEGER,
                colors TEXT,
                edhrec_rank INTEGER,
                flavor_text TEXT,
                foil INTEGER,
                keywords TEXT,
                lang TEXT,
                mana_cost TEXT,
                nonfoil INTEGER,
                power TEXT,
                preview_source TEXT, 
                preview_source_uri TEXT, 
                previewed_at TEXT,
                price_usd TEXT,
                price_eur TEXT,
                rarity TEXT,
                reprint INTEGER,
                rulings_uri TEXT,
                scryfall_uri TEXT,
                set_card TEXT,
                toughness TEXT,
                type_line TEXT,
                variation INTEGER
            )
        ''')

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        print("Table 'cards' created.")
    else:
        print("Database file exists, skipping table creation.")

@app.before_request
def before_request():
    if not hasattr(g, 'db_initialized'):
        create_table_if_not_exists()
        g.db_initialized = True
        print("Database initialized.")

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

    # Combine 'colors' into a single string
    colors_str = ''.join(card_data.get('colors', ''))

    # Combine 'keywords' into a single string with underscores
    keywords_str = '_'.join(card_data.get('keywords', ''))

    # Extract prices for each currency
    prices_dict = card_data.get('prices', {})
    price_usd = prices_dict.get('usd', '')
    price_eur = prices_dict.get('eur', '')

    # Extract preview parameters
    preview_source = card_data['preview'].get('source', '')
    preview_source_uri = card_data['preview'].get('source_uri', '')
    previewed_at = card_data['preview'].get('previewed_at', '')

    cursor.execute('''
        INSERT INTO cards (
            id, name, rarity, image_uri_normal, booster, cardmarket_id, colors,
            edhrec_rank, flavor_text, foil, keywords, lang, mana_cost, nonfoil,
            power, preview_source, preview_source_uri, previewed_at,
            price_usd, price_eur, rarity, reprint, rulings_uri, scryfall_uri,
            set_card, toughness, type_line, variation
        )
        VALUES (
            :id, :name, :rarity, :image_uri_normal, :booster, :cardmarket_id, :colors,
            :edhrec_rank, :flavor_text, :foil, :keywords, :lang, :mana_cost, :nonfoil,
            :power, :preview_source, :preview_source_uri, :previewed_at,
            :price_usd, :price_eur, :rarity, :reprint, :rulings_uri, :scryfall_uri,
            :set_card, :toughness, :type_line, :variation
        )
    ''', {
        'id': card_data['id'],
        'name': card_data['name'],
        'rarity': card_data['rarity'],
        'image_uri_normal': card_data['image_uris']['normal'],
        'booster': card_data.get('booster', ''),
        'cardmarket_id': card_data.get('cardmarket_id', ''),
        'colors': colors_str,
        'edhrec_rank': card_data.get('edhrec_rank', ''),
        'flavor_text': card_data.get('flavor_text', ''),
        'foil': card_data.get('foil', ''),
        'keywords': keywords_str,
        'lang': card_data.get('lang', ''),
        'mana_cost': card_data.get('mana_cost', ''),
        'nonfoil': card_data.get('nonfoil', ''),
        'power': card_data.get('power', ''),
        'preview_source': preview_source,
        'preview_source_uri': preview_source_uri,
        'previewed_at': previewed_at,
        'price_usd': price_usd,
        'price_eur': price_eur,
        'rarity': card_data.get('rarity', ''),
        'reprint': card_data.get('reprint', ''),
        'rulings_uri': card_data.get('rulings_uri', ''),
        'scryfall_uri': card_data.get('scryfall_uri', ''),
        'set_card': card_data.get('set', ''),
        'toughness': card_data.get('toughness', ''),
        'type_line': card_data.get('type_line', ''),
        'variation': card_data.get('variation', '')
    })

    db.commit()
    db.close()

def get_card_names_from_file():
    with open('card_names.txt', 'r') as file:
        card_names = [line.strip() for line in file.readlines()]
    return card_names



def get_matching_card_names(prefix):
    # Example function that returns matching card names
    # Replace this with your actual logic to fetch matching names
    card_names = get_card_names_from_file()
    matching_names = [name for name in card_names if name.lower().startswith(prefix.lower())]
    return matching_names

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    prefix = request.args.get('prefix', '')
    matching_names = get_matching_card_names(prefix)
    return jsonify(matching_names)

@app.route('/', methods=['GET', 'POST'])
def index():

    create_table_if_not_exists()
    
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

        # Calculate statistics
        total_cards = len(card_data_list)
        rarity_counts = {'common': 0, 'uncommon': 0, 'rare': 0, 'mythic': 0}

        for card in card_data_list:
            rarity = card['rarity']
            rarity_counts[rarity] += 1  # Increment the count for the specific rarity

        with open('sets-mtg.txt', 'r') as file:
            sets = [line.strip() for line in file.readlines()]

        with open('card_names.txt', 'r') as file:
            card_names = [line.strip() for line in file.readlines()]

        return render_template(
            'index.html',
            sets=sets,
            card_data_list=card_data_list,
            card_names=card_names,
            total_cards=total_cards,
            rarity_counts=rarity_counts
        )

if __name__ == "__main__":
    app.run(debug=True)