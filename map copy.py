import http.server
import socketserver
import folium
import threading
import os
import json
import re  # ajouté

PORT = 5001
MAP_FILE = "./templates/map.html"

m = None
_server_thread = None
dynamic_point = None
dynamic_points = []

def start(initial_point):
    global m
    m = folium.Map(location=(initial_point['latitude'], initial_point['longitude']), zoom_start=6)
    generate_map()
    start_server()

def generate_map():
    m.save(MAP_FILE)

    # Lire le contenu de la map
    with open(MAP_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Extraire le nom de variable de la carte générée par folium (ex: map_xxxx)
    match = re.search(r"var (map_\w+) = L\.map\(", content)
    map_var = match.group(1) if match else "map"

    js = f"""
    <script src="https://rawcdn.githack.com/bbecquet/Leaflet.RotatedMarker/master/leaflet.rotatedMarker.js"></script>
    <script>
    var dynamicMarker = null;

    var planeIcon = L.icon({{
        iconUrl: 'plane-icon.png',
        iconSize: [64, 64],
        iconAnchor: [32, 32],
        popupAnchor: [0, -16]
    }});

    function updateMarker(lat, lng, heading) {{
        if (dynamicMarker) {{
            dynamicMarker.setLatLng([lat, lng]);
            dynamicMarker.setRotationAngle(heading || 0);  // Appliquer la rotation
        }}
    }}

    async function pollPosition() {{
        try {{
            const res = await fetch('/position');
            const data = await res.json();
            updateMarker(data.latitude, data.longitude, data.heading);
        }} catch (e) {{
            console.error("Erreur de mise à jour : ", e);
        }}
        setTimeout(pollPosition, 1000);
    }}

    document.addEventListener("DOMContentLoaded", function() {{
        dynamicMarker = L.marker([0, 0], {{
            icon: planeIcon,
            rotationAngle: 0,
            rotationOrigin: 'center center'
        }}).addTo(window.{map_var});
        pollPosition();
    }});
    </script>
    </body>"""

    content = content.replace("</body>", js)

    with open(MAP_FILE, "w", encoding="utf-8") as f:
        f.write(content)

def start_server():
    global _server_thread
    if _server_thread and _server_thread.is_alive():
        print("✅ Serveur déjà en cours.")
        return

    def run_server():
        os.chdir('.')  # pour servir les fichiers dans le répertoire courant
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
            print(f"🚀 Serveur en ligne : http://localhost:{PORT}")
            httpd.serve_forever()

    _server_thread = threading.Thread(target=run_server, daemon=True)
    _server_thread.start()

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/position":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            if dynamic_point:
                self.wfile.write(json.dumps({
                    'latitude': dynamic_point['latitude'],
                    'longitude': dynamic_point['longitude'],
                    'heading': dynamic_point['heading'],
                }).encode())
            else:
                self.wfile.write(json.dumps({'latitude': 0, 'longitude': 0}).encode())
        else:
            super().do_GET()

def move_avion(avion):
    global dynamic_point
    if dynamic_point is None:
        dynamic_point = avion.copy()
    else:
        dynamic_point['latitude'] = avion['latitude']
        dynamic_point['longitude'] = avion['longitude']
        dynamic_point['altitude'] = avion['altitude']
        dynamic_point['heading'] = avion['heading']

def add_dynamic_point(point):
    dynamic_points.append(point)