import sqlite3
import os
from flask import  g
import requests

def create_table_if_not_exists(app):
    
    if not os.path.exists(app.config['DATABASE']):
        conn = sqlite3.connect(app.config['DATABASE'])

        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                id TEXT PRIMARY KEY,
                name TEXT,
                image_uri_normal TEXT,
                image_path TEXT,
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
                price_usd REAL,
                price_eur REAL,
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

        conn.commit()
        conn.close()

        print("Table 'cards' created.")
    else:
        print("Database file exists, skipping table creation.")

def get_db(app):
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('mtg-cards', None)
    if db is not None:
        db.close()

def save_card_to_db(app,card_data):
    db = get_db(app)
    cursor = db.cursor()

    card_name = card_data.get('name', '')
    image_url = card_data.get('image_uris', {}).get('normal', '')
    folder_path = os.path.join(app.static_folder, 'card_images')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = f"{card_name.replace(' ', '_')}.jpg"
    image_path = os.path.join('card_images', filename)
    save_image_to_folder(image_url, folder_path, filename)
    card_data['image_path'] = image_path.replace('\\', '/')

    colors_str = ''.join(card_data.get('colors', ''))

    keywords_str = '_'.join(card_data.get('keywords', ''))

    prices_dict = card_data.get('prices', {})

    preview_data = card_data.get('preview', {})
    preview_source = preview_data.get('source', '')
    preview_source_uri = preview_data.get('source_uri', '')
    previewed_at = preview_data.get('previewed_at', '')

    cursor.execute('''
        INSERT INTO cards (
            id, name, rarity, image_uri_normal, image_path,
            booster, cardmarket_id, colors, edhrec_rank, flavor_text, foil,
            keywords, lang, mana_cost, nonfoil, power, preview_source,
            preview_source_uri, previewed_at, price_usd, price_eur, rarity,
            reprint, rulings_uri, scryfall_uri, set_card, toughness, type_line,
            variation
        )
        VALUES (
            :id, :name, :rarity, :image_uri_normal, :image_path,
            :booster, :cardmarket_id, :colors, :edhrec_rank, :flavor_text,
            :foil, :keywords, :lang, :mana_cost, :nonfoil, :power,
            :preview_source, :preview_source_uri, :previewed_at,
            :price_usd, :price_eur, :rarity, :reprint, :rulings_uri,
            :scryfall_uri, :set_card, :toughness, :type_line, :variation
        )
    ''', {
        'id': card_data.get('id', None),
        'name': card_data.get('name', None),
        'rarity': card_data.get('rarity', None),
        'image_uri_normal': card_data.get('image_uris', {}).get('normal', None),
        'image_path': card_data.get('image_path', None),
        'booster': card_data.get('booster', None),
        'cardmarket_id': card_data.get('cardmarket_id', None),
        'colors': colors_str if colors_str else None,
        'edhrec_rank': card_data.get('edhrec_rank', None),
        'flavor_text': card_data.get('flavor_text', None),
        'foil': card_data.get('foil', None),
        'keywords': keywords_str if keywords_str else None,
        'lang': card_data.get('lang', None),
        'mana_cost': card_data.get('mana_cost', None),
        'nonfoil': card_data.get('nonfoil', None),
        'power': card_data.get('power', None),
        'preview_source': preview_source if preview_source else None,
        'preview_source_uri': preview_source_uri if preview_source_uri else None,
        'previewed_at': previewed_at if previewed_at else None,
        'price_usd': float(prices_dict.get('usd', 0.00)),  
        'price_eur': float(prices_dict.get('eur', 0.00)), 
        'rarity': card_data.get('rarity', None),
        'reprint': card_data.get('reprint', None),
        'rulings_uri': card_data.get('rulings_uri', None),
        'scryfall_uri': card_data.get('scryfall_uri', None),
        'set_card': card_data.get('set', None),
        'toughness': card_data.get('toughness', None),
        'type_line': card_data.get('type_line', None),
        'variation': card_data.get('variation', None)
    })

    db.commit()
    db.close()


def save_image_to_folder(image_url, folder_path, filename):
    response = requests.get(image_url)
    
    if response.status_code == 200:
        image_data = response.content
        file_path = os.path.join(folder_path, filename)

        with open(file_path, 'wb') as image_file:
            image_file.write(image_data)

        print(f"Image saved successfully: {file_path}")
        return file_path
    else:
        print(f"Error: Unable to fetch image from {image_url}")
        return None
