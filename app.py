# app.py
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def get_cities_from_bbox(north, south, east, west, limit=200):
    query = f"""
    [out:json][timeout:25];
    (
      node["place"~"city|town|village"]({south},{west},{north},{east});
      way["place"~"city|town|village"]({south},{west},{north},{east});
    );
    out center {limit};
    """
    try:
        resp = requests.post(OVERPASS_URL, data={'data': query}, headers={'User-Agent': 'MyApp/1.0'})
        resp.raise_for_status()
        data = resp.json()
        cities = [el['tags']['name'] for el in data.get('elements', []) if 'tags' in el and 'name' in el['tags']]
        return list(dict.fromkeys(cities))[:limit]  # remove duplicates
    except Exception as e:
        print("Error fetching cities from Overpass:", e)
        return []

def get_landmarks_from_bbox(north, south, east, west, limit=200):
    query = f"""
    [out:json][timeout:25];
    (
      node["tourism"="attraction"]({south},{west},{north},{east});
      node["historic"]({south},{west},{north},{east});
      way["tourism"="attraction"]({south},{west},{north},{east});
      way["historic"]({south},{west},{north},{east});
    );
    out center {limit};
    """
    try:
        resp = requests.post(OVERPASS_URL, data={'data': query}, headers={'User-Agent': 'MyApp/1.0'})
        resp.raise_for_status()
        data = resp.json()
        landmarks = [el['tags']['name'] for el in data.get('elements', []) if 'tags' in el and 'name' in el['tags']]
        return list(dict.fromkeys(landmarks))[:limit]  # remove duplicates
    except Exception as e:
        print("Error fetching landmarks from Overpass:", e)
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_locations', methods=['POST'])
def get_locations():
    data = request.json
    north = data.get('north')
    south = data.get('south')
    east = data.get('east')
    west = data.get('west')

    if not all([north, south, east, west]):
        return jsonify({"error": "Missing coordinates"}), 400

    # Fetch cities and landmarks
    cities = get_cities_from_bbox(north, south, east, west)
    landmarks = get_landmarks_from_bbox(north, south, east, west)

    # Remove landmarks that match city names
    landmark_names = [l for l in landmarks if l not in cities]

    combined = (cities + landmark_names)[:200]
    return jsonify(combined)

if __name__ == '__main__':
    app.run(debug=True)

