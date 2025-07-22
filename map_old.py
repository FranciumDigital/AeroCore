import http.server
import socketserver
import folium
import threading
import os
import webbrowser
import json

PORT = 5001
MAP_FILE = "./templates/map.html"

points = []
default_icon_color = 'blue'
couleurs = [
    'red', 'blue', 'green', 'purple', 'orange', 'darkred',
    'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue',
    'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen',
    'gray', 'black', 'lightgray'
]

m = None
_server_thread = None
dynamic_point = None

def start(initial_point, initial_point_icon_color=default_icon_color):
    global m
    points.clear()
    m = folium.Map(location=(initial_point['latitude'], initial_point['longitude']), zoom_start=11)
    generate_map()
    start_server()

def generate_map():
    m.save(MAP_FILE)

    # Injecter du JS pour rendre le marqueur 'avion' dynamique
    with open(MAP_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    js = """
    <script>
    var dynamicMarker = null;
    function updateMarker(lat, lng) {
        if (dynamicMarker) {
            dynamicMarker.setLatLng([lat, lng]);
        }
    }

    // Exemple de récupération périodique de position via endpoint `/position`
    async function pollPosition() {
        try {
            const res = await fetch('/position');
            const data = await res.json();
            updateMarker(data.latitude, data.longitude);
        } catch (e) {
            console.error("Erreur de mise à jour : ", e);
        }
        setTimeout(pollPosition, 1000);
    }

    // Attendre que la carte soit chargée
    document.addEventListener("DOMContentLoaded", function() {
        dynamicMarker = L.marker([0, 0]).addTo(window.map);  // Par défaut (0,0)
        pollPosition();
    });
    </script>
    </body>"""

    # Inject JS avant la balise </body>
    content = content.replace("</body>", js)

    with open(MAP_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def start_server():
    global _server_thread
    if _server_thread and _server_thread.is_alive():
        print("✅ Serveur déjà en cours.")
        return

    def run_server():
        os.chdir('.')  # Pour servir index.html
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
            print(f"🚀 Serveur en ligne : http://localhost:{PORT}")
            httpd.serve_forever()

    _server_thread = threading.Thread(target=run_server, daemon=True)
    _server_thread.start()


"""
def addPoint(point, icon_color=default_icon_color):
    points.append(point)

    popup_content = (
        f"<b>{point['label']}</b><br>"
        f"Latitude : {point['latitude']}<br>"
        f"Longitude : {point['longitude']}<br>"
        f"Altitude : {point['altitude']} m<br>"
        f"Heading : {point['heading']}°"
    )

    folium.Marker(
        location=(point['latitude'], point['longitude']),
        tooltip=point['label'],
        popup=popup_content,
        icon=folium.Icon(color=icon_color, icon="info-sign")
    ).add_to(m)

    generate_map()

def removePoint(label):
    before = len(points)
    points[:] = [p for p in points if p.get("label") != label]
    if len(points) < before:
        # Re-générer la carte à partir des points restants
        if points:
            center = (points[0]['latitude'], points[0]['longitude'])
        else:
            center = (0, 0)
        m = folium.Map(location=center, zoom_start=11)
        for p in points:
            addPoint(p)  # va regénérer la carte
        generate_map()

def addLine(pointA, pointB, color='purple'):
    folium.PolyLine(
        locations=[
            [pointA['latitude'], pointA['longitude']],
            [pointB['latitude'], pointB['longitude']],
        ],
        color=color,
        weight=2,
        smooth_factor=1,
    ).add_to(m)
    generate_map()

"""

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/position":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            if dynamic_point:
                self.wfile.write(json.dumps({
                    'latitude': dynamic_point['latitude'],
                    'longitude': dynamic_point['longitude']
                }).encode())
            else:
                self.wfile.write(json.dumps({'latitude': 0, 'longitude': 0}).encode())
        else:
            super().do_GET()

def move_avion(avion):
    global dynamic_point
    if dynamic_point is None:
        # Crée une copie initiale de l'avion
        dynamic_point = avion.copy()
    else:
        # Met à jour les champs existants
        dynamic_point['latitude'] = avion['latitude']
        dynamic_point['longitude'] = avion['longitude']
        if 'altitude' in avion:
            dynamic_point['altitude'] = avion['altitude']
        if 'heading' in avion:
            dynamic_point['heading'] = avion['heading']
