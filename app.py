# app.py
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def parse_element(el):
    """Extract name and coordinates from Overpass element"""
    if 'tags' not in el or 'name' not in el['tags']:
        return None
    name = el['tags']['name']
    if 'lat' in el and 'lon' in el:
        lat, lon = el['lat'], el['lon']
    elif 'center' in el:
        lat, lon = el['center']['lat'], el['center']['lon']
    else:
        return None
    return {"name": name, "lat": lat, "long": lon}

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
        cities = [parse_element(el) for el in data.get('elements', [])]
        return [c for c in cities if c]  # filter None
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
        landmarks = [parse_element(el) for el in data.get('elements', [])]
        return [l for l in landmarks if l]
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

    cities = get_cities_from_bbox(north, south, east, west)
    landmarks = get_landmarks_from_bbox(north, south, east, west)

    # Remove landmarks that have the same name as a city
    city_names = {c['name'] for c in cities}
    landmark_filtered = [l for l in landmarks if l['name'] not in city_names]

    combined = (cities + landmark_filtered)[:200]
    return jsonify(combined)

if __name__ == '__main__':
    app.run(debug=True)

