from flask import Flask, render_template, request
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


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_set = request.form['selected_set']
        card_name = request.form['card_name']

        #process part of the selected set

        print(f'Selected set: {selected_set}')
        print(f'Card name: {card_name}')
        
        return 'Form submitted successfully!'
    else:
        with open('sets-mtg.txt', 'r') as file:
            sets = [line.strip() for line in file.readlines()]
        return render_template('index.html', sets=sets)
if __name__ == "__main__":
    app.run(debug=True)