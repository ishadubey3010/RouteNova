from flask import Flask, render_template, request, redirect, session
import sqlite3
from graph import dijkstra
import folium
import requests

coordinates = {
    'Bhopal': (23.2599, 77.4126),
    'Indore': (22.7196, 75.8577),
    'Nagpur': (21.1458, 79.0882),
    'Mumbai': (19.0760, 72.8777)
}
def get_real_route(start, end):
    api_key = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjdhOTU3M2ZmZmRkZTQ5Nzk5MDc1MTMzYzVhNmZhZmZiIiwiaCI6Im11cm11cjY0In0="

    coords = {
        'Bhopal': [77.4126, 23.2599],
        'Indore': [75.8577, 22.7196],
        'Nagpur': [79.0882, 21.1458],
        'Mumbai': [72.8777, 19.0760]
    }

    url = "https://api.openrouteservice.org/v2/directions/driving-car"

    body = {
        "coordinates": [
            coords[start],
            coords[end]
        ]
    }

    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=body, headers=headers)

    data = response.json()

    distance = data['routes'][0]['summary']['distance'] / 1000  # km
    duration = data['routes'][0]['summary']['duration'] / 60   # minutes

    steps = data['routes'][0]['segments'][0]['steps']

    directions = [step['instruction'] for step in steps]

    return round(distance, 2), round(duration, 2), directions

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- ROUTES ----------

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
        user = cur.fetchone()
        conn.close()

        if user:
            session['user'] = username
            return redirect('/dashboard')
        else:
            return "Invalid Login"

    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username,password) VALUES (?,?)", (username,password))
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    nodes = ['Bhopal', 'Indore', 'Nagpur', 'Mumbai']
    result = None
    map_file = None

    if request.method == 'POST':
        start = request.form.get('start')
        end = request.form.get('end')
        route_type = request.form.get('type')   # ✅ FIX HERE

        if not start or not end:
            return render_template('dashboard.html', nodes=nodes, result=None, map_file=None)

        distance, duration, directions = get_real_route(start, end)

        if route_type == 'traffic':
            cost, path = dijkstra(start, end, mode='traffic')
        else:
            cost, path = dijkstra(start, end, mode='distance')  # keep for logic explanation

        # MAP CODE
        m = folium.Map(location=[22.5, 78], zoom_start=5)

        for city in path:
            folium.Marker(location=coordinates[city], popup=city).add_to(m)

        route_coords = [coordinates[city] for city in path]
        folium.PolyLine(route_coords, color="blue").add_to(m)

        map_file = "static/map.html"
        m.save(map_file)

        result = {
    "path": path,
    "cost": cost,
    "type": route_type,
    "distance": distance,
    "duration": duration,
    "directions": directions
}

    return render_template('dashboard.html', nodes=nodes, result=result, map_file=map_file)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)

route_type = request.form.get('type')