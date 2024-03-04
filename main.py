from flask import Flask, render_template, request, g
import sqlite3
import json
import os

database_file = 'mtg-cards.db'

# # Check if the database file exists
# if not os.path.exists(database_file):
#     # Connect to the SQLite database (it will be created if it doesn't exist)
#     conn = sqlite3.connect(database_file)

#     # Create a cursor object to execute SQL commands
#     cursor = conn.cursor()

#     # Create a table for storing card information
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS cards (
#             id TEXT PRIMARY KEY,
#             name TEXT,
#             rarity TEXT,
#             image_uri_small TEXT,
#             image_uri_normal TEXT
#         )
#     ''')
# else:
#     # If the database file exists, just connect to it
#     conn = sqlite3.connect(database_file)
#     cursor = conn.cursor()

# # Read JSON data from the file
# with open('leinora.json', 'r') as json_file:
#     card_data = json.load(json_file)

# # Extract the specific fields from the JSON data
# name = card_data['name']
# rarity = card_data['rarity']
# image_uri_small = card_data['image_uris']['small']
# image_uri_normal = card_data['image_uris']['normal']

# # Insert card data into the table
# cursor.execute('''
#     INSERT INTO cards (id, name, rarity, image_uri_small, image_uri_normal)
#     VALUES (:id, :name, :rarity, :image_uri_small, :image_uri_normal)
# ''', {
#     'id': card_data['id'],
#     'name': name,
#     'rarity': rarity,
#     'image_uri_small': image_uri_small,
#     'image_uri_normal': image_uri_normal
# })

# # Commit the changes and close the connection
# conn.commit()
# conn.close()

app = Flask(__name__)
app.config['DATABASE'] = 'mtg-cards.db'

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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_set = request.form['selected_set']
        card_name = request.form['card_name']

        db = get_db()
        cursor = db.cursor()
        
    else:
        db = get_db()
        cursor = db.cursor()

        # Fetch all cards from the database
        query = "SELECT id, name, rarity, image_uri_small, image_uri_normal FROM cards"
        cards = cursor.execute(query).fetchall()

        # Convert the rows to a list of dictionaries for easier template rendering
        card_data_list = [dict(card) for card in cards]

        with open('sets-mtg.txt', 'r') as file:
            sets = [line.strip() for line in file.readlines()]

        return render_template('index.html', sets=sets, card_data_list=card_data_list)
if __name__ == "__main__":
    app.run(debug=True)