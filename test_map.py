import http.server
import socketserver
import folium
import threading
import json
import time
import os
import re

PORT = 5001
MAP_FILE = "map.html"

dynamic_point = {'latitude': 48.8566, 'longitude': 2.3522}  # Paris par défaut

def generate_map():
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=5)
    m.save(MAP_FILE)

    with open(MAP_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Extraire le nom de variable map_... créé par folium
    match = re.search(r"var (map_\w+) = L\.map\(", content)
    map_var = match.group(1) if match else "map"

    js = f"""
    <script>
    var dynamicMarker = null;
    function updateMarker(lat, lng) {{
        if (dynamicMarker) {{
            dynamicMarker.setLatLng([lat, lng]);
        }}
    }}

    async function pollPosition() {{
        try {{
            const res = await fetch('/position');
            const data = await res.json();
            updateMarker(data.latitude, data.longitude);
        }} catch (e) {{
            console.error("Erreur de mise à jour : ", e);
        }}
        setTimeout(pollPosition, 1000);
    }}

    document.addEventListener("DOMContentLoaded", function() {{
        dynamicMarker = L.marker([0, 0]).addTo({map_var});
        pollPosition();
    }});
    </script>
    </body>"""

    content = content.replace("</body>", js)

    with open(MAP_FILE, "w", encoding="utf-8") as f:
        f.write(content)

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/position":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(dynamic_point).encode())
        else:
            super().do_GET()

def start_server():
    os.chdir(".")
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        httpd.serve_forever()

def move_avion(lat, lng):
    global dynamic_point
    dynamic_point['latitude'] = lat
    dynamic_point['longitude'] = lng

def main():
    generate_map()

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Change la position de l'avion toutes les 2 secondes (exemple)
    coords = [
        (48.8566, 2.3522),    # Paris
        (51.5074, -0.1278),   # Londres
        (40.7128, -74.0060),  # NYC
        (35.6895, 139.6917)   # Tokyo
    ]
    i = 0
    while True:
        lat, lng = coords[i % len(coords)]
        print(f"Move avion to {lat}, {lng}")
        move_avion(lat, lng)
        i += 1
        time.sleep(2)

if __name__ == "__main__":
    main()
