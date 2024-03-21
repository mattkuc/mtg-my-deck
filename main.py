from flask import Flask, render_template, request, g, redirect, send_from_directory, url_for, jsonify
from urllib.parse import urlencode
import requests
import sqlite3
import os
import json
from database import create_table, create_table_if_not_exists, download_cards, get_available_tables, get_db, close_db, retrieve_card_data, save_card_to_db, table_exists
from card_operations import get_card_names_from_file, get_matching_card_names

app = Flask(__name__, static_url_path='/static')
app.config['DATABASE'] = 'database/mtg-cards.db'

@app.before_request
def before_request():
    if not hasattr(g, 'db_initialized'):
        create_table_if_not_exists(app,'main_cards')
        g.db_initialized = True
        print("Database initialized.")

@app.teardown_appcontext
def close_database(error):
    close_db()

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    prefix = request.args.get('prefix', '')
    matching_names = get_matching_card_names(prefix)
    return jsonify(matching_names)

@app.route('/remove/<card_id>', methods=['GET'])
def remove_card(card_id):
    db = get_db(app)
    cursor = db.cursor()

    query = "DELETE FROM cards WHERE id = ?"
    cursor.execute(query, (card_id,))

    db.commit()
    db.close()

    return redirect(url_for('index'))


@app.route('/static/card_images/<path:filename>')
def card_image(filename):
    return send_from_directory('static/card_images', filename)

@app.route('/update_possession/<table_name>/<card_id>', methods=['POST'])
def update_possession(table_name, card_id):
    db = get_db(app)
    cursor = db.cursor()

    query = f"""
        UPDATE {table_name}
        SET in_possession = CASE WHEN in_possession = 0 THEN 1 ELSE 0 END
        WHERE id = ?
    """
    cursor.execute(query, (card_id,))
    db.commit()

    return jsonify({'success': True})

@app.route('/collector', methods=['GET','POST'])
def collector():
    db = get_db(app)
    cursor = db.cursor()

    if request.method == 'POST':
        selected_card_set = request.form['selected_card_set']

        if not table_exists(app,selected_card_set):
            create_table(app,selected_card_set)
            print("DOWNLOAD CARDS")
            download_cards(app,selected_card_set)

        query = f"""
            SELECT
                COUNT(*) AS total_cards,
                SUM(CAST(price_usd AS FLOAT)) AS cumulative_price_usd,
                SUM(CAST(price_eur AS FLOAT)) AS cumulative_price_eur
            FROM {selected_card_set};
        """
        result = cursor.execute(query).fetchone()

        total_cards = result['total_cards']
        cumulative_price_usd = result['cumulative_price_usd']
        cumulative_price_eur = result['cumulative_price_eur']

        query = f"SELECT id, name, rarity, image_uri_normal, image_path,set_card, in_possession FROM {selected_card_set}"
        cards = cursor.execute(query).fetchall()

        card_data_list = [dict(card) for card in cards]

        total_cards = len(card_data_list)
        rarity_counts = {'common': 0, 'uncommon': 0, 'rare': 0, 'mythic': 0}

        for card in card_data_list:
            rarity = card['rarity']
            rarity_counts[rarity] += 1 

        available_tables = get_available_tables(app)
        return render_template('collector.html', card_data_list=card_data_list,total_cards=total_cards,
            rarity_counts=rarity_counts,
            cumulative_price_usd=cumulative_price_usd,
            cumulative_price_eur=cumulative_price_eur,
            available_tables=available_tables)
    else:
        available_tables = get_available_tables(app)
        return render_template('collector.html', card_data_list=[],total_cards=0,
            rarity_counts=[],
            cumulative_price_usd=[],
            cumulative_price_eur=[],
            available_tables=available_tables)



@app.route('/', methods=['GET', 'POST'])
def index():
    main_db = 'main_cards'

    create_table_if_not_exists(app,main_db)
    
    if request.method == 'POST':
        selected_card_name = request.form['selected_card_name']
        selected_card_name = selected_card_name.replace('"','')
        encoded_card_name = urlencode({'exact': selected_card_name})

        api_url = f"https://api.scryfall.com/cards/named?{encoded_card_name}"

        response = requests.get(api_url)

        if response.status_code == 200:
            card_data = response.json()
            save_card_to_db(app,main_db,card_data)

            return redirect(url_for('index'))
        else:
            return f"Error: Unable to fetch card information for '{selected_card_name}'."

    else:
        db = get_db(app)
        cursor = db.cursor()


        query = """
            SELECT
                COUNT(*) AS total_cards,
                SUM(CAST(price_usd AS FLOAT)) AS cumulative_price_usd,
                SUM(CAST(price_eur AS FLOAT)) AS cumulative_price_eur
            FROM main_cards;
        """
        result = cursor.execute(query).fetchone()

        total_cards = result['total_cards']
        cumulative_price_usd = result['cumulative_price_usd']
        cumulative_price_eur = result['cumulative_price_eur']

        query = "SELECT id, name, rarity, image_uri_normal, image_path FROM main_cards"
        cards = cursor.execute(query).fetchall()

        card_data_list = [dict(card) for card in cards]

        total_cards = len(card_data_list)
        rarity_counts = {'common': 0, 'uncommon': 0, 'rare': 0, 'mythic': 0}

        for card in card_data_list:
            rarity = card['rarity']
            rarity_counts[rarity] += 1 



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
            rarity_counts=rarity_counts,
            cumulative_price_usd=cumulative_price_usd,
            cumulative_price_eur=cumulative_price_eur
        )

if __name__ == "__main__":
    app.run(debug=True)