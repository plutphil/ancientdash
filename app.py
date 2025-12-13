import requests
from flask import Flask, render_template, redirect, url_for, jsonify
import json
import time
import os


app = Flask(__name__)



def get_home_assistant_data(api_endpoint, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Get all entities
    entities_url = f"{api_endpoint}/core/api/states"
    entities_response = requests.get(entities_url, headers=headers)
    app.logger.info(entities_response)

    app.logger.info(entities_response.text)
    app.logger.info(api_endpoint+" "+access_token)
    entities_data = entities_response.json()

    # Filter out entities with state 'unavailable'
    filtered_entities = [entity for entity in entities_data if entity['state'] != 'unavailable']

    return filtered_entities

def toggle_switch(api_endpoint, access_token, entity_id):
    # Call the Home Assistant service to toggle the switch
    requests.post(
        f"{api_endpoint}/core/api/services/switch/toggle",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        json={"entity_id": entity_id}
    )

def get_favorites():
    try:
        with open('favorites.json', 'r') as file:
            favorites = json.load(file)
    except FileNotFoundError:
        favorites = []

    return favorites


def add_to_favorites(entity_id):
    global favorites
    try:
        with open('favorites.json', 'r') as file:
            favorites = json.load(file)
    except FileNotFoundError:
        favorites = []

    if entity_id not in favorites:
        favorites.append(entity_id)

        with open('favorites.json', 'w') as file:
            json.dump(favorites, file, indent=2)
            

# Retrieve environment variables
host = os.getenv("HOST")
host = "supervisor"
token = os.getenv("SUPERVISOR_TOKEN")


favorites = get_favorites()

api_endpoint = "http://supervisor"
access_token = token

@app.route('/')
def index():
    # Replace these values with your Home Assistant API endpoint and access token

    entities_data = get_home_assistant_data(api_endpoint, access_token)

    # Render HTML page with a table
    return render_template('sliderswitch.html', entities_data=entities_data, favorites=favorites)
    #return render_template('index.html', entities_data=entities_data, favorites=favorites)

@app.route('/all')
def listall():
    # Replace these values with your Home Assistant API endpoint and access token

    entities_data = get_home_assistant_data(api_endpoint, access_token)

    # Render HTML page with a table
    #return render_template('sliderswitch.html', entities_data=entities_data, favorites=favorites)
    return render_template('index.html', entities_data=entities_data, favorites=favorites)

@app.route('/toggle/<entity_id>')
def toggle_entity(entity_id):
    # Toggle the switch
    toggle_switch(api_endpoint, access_token, entity_id)
    #time.sleep(0.1)
    # Redirect back to the home page
    return redirect(url_for('index'))

@app.route('/add_to_favorites/<entity_id>')
def add_to_favorites_route(entity_id):
    add_to_favorites(entity_id)
    return redirect(url_for('index'))

@app.route('/favorites')
def favorites_route():
    return jsonify(favorites)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
