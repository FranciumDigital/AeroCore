import http.server
import socketserver
import folium
import threading
import os
import json
import re
PORT = 5001
MAP_FILE = "./templates/map.html"

m = None
_server_thread = None
dynamic_point = None
dynamic_points = []
dynamic_lines = []  # liste de dict {latitude, longitude}

def start(initial_point):
    global m
    m = folium.Map(location=(initial_point['latitude'], initial_point['longitude']), zoom_start=6)
    generate_map()
    start_server()

def generate_map():
    m.save(MAP_FILE)

    with open(MAP_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r"var (map_\w+) = L\.map\(", content)
    map_var = match.group(1) if match else "map"

    js = f"""
    <script src="https://rawcdn.githack.com/bbecquet/Leaflet.RotatedMarker/master/leaflet.rotatedMarker.js"></script>
    <script>
    var map_var = "{map_var}";
    var dynamicMarker = null;
    var extraMarkers = [];

    var planeIcon = L.icon({{
        iconUrl: 'plane-icon.png',
        iconSize: [64, 64],
        iconAnchor: [32, 32],
        popupAnchor: [0, -16]
    }});

    var dynamicLines = {{}};

    function updateLines(lines) {{
        const newLabels = lines.map(line => line.label);

        Object.keys(dynamicLines).forEach(label => {{
            if (!newLabels.includes(label)) {{
                window[map_var].removeLayer(dynamicLines[label]);
                delete dynamicLines[label];
            }}
        }});

        lines.forEach(line => {{
            const latlngs = line.coords.map(p => [p.latitude, p.longitude]);

            if (!dynamicLines[line.label]) {{
                dynamicLines[line.label] = L.polyline(latlngs, {{color: 'blue', weight: 3}}).addTo(window[map_var]);
            }} else {{
                dynamicLines[line.label].setLatLngs(latlngs);
            }}
        }});
    }}

    function updateMarker(lat, lng, heading) {{
        if (dynamicMarker) {{
            dynamicMarker.setLatLng([lat, lng]);
            dynamicMarker.setRotationAngle(heading || 0);

            if (dynamicMarker._icon && dynamicMarker._icon.parentNode) {{
                dynamicMarker._icon.parentNode.appendChild(dynamicMarker._icon);
            }}
        }}
    }}

    function updateExtraPoints(points) {{
        extraMarkers.forEach(m => window[map_var].removeLayer(m));
        extraMarkers = [];

        points.forEach(p => {{
            let markerOptions = {{}};

            if (p.icon) {{
                if (p.icon.type === "color") {{
                    markerOptions.icon = L.icon({{
                        iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${{p.icon.value}}.png`,
                        iconSize: [25, 41],
                        iconAnchor: [12, 41],
                        popupAnchor: [1, -34],
                        shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
                        shadowSize: [41, 41]
                    }});
                }} else if (p.icon.type === "image") {{
                    markerOptions.icon = L.icon({{
                        iconUrl: p.icon.value,
                        iconSize: [16, 16],
                        iconAnchor: [8, 8],
                    }});
                }}
            }}

            const marker = L.marker([p.latitude, p.longitude], markerOptions);
            if (p.popup) marker.bindPopup(p.popup);
            marker.addTo(window[map_var]);
            extraMarkers.push(marker);
        }});
    }}

    async function pollPosition() {{
        try {{
            const res = await fetch('/position');
            const data = await res.json();
            updateMarker(data.avion.latitude, data.avion.longitude, data.avion.heading);
            updateExtraPoints(data.points || []);
            updateLines(data.lines || []);
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
        }}).addTo(window[map_var]);
        if (dynamicMarker._icon) {{
            dynamicMarker._icon.classList.add('plane-marker');
        }}
        pollPosition();
    }});
    </script>
    """

    # Injecter le CSS séparément, par exemple juste avant </head> ou </body>
    style = """
    <style>
    .leaflet-marker-icon.plane-marker {
        z-index: 10000 !important;
    }
    </style>
    """

    # Injecter le CSS avant </head> ou avant </body>
    if "</head>" in content:
        content = content.replace("</head>", style + "</head>")
    else:
        content = content.replace("</body>", style + "</body>")

    # Injecter le JS avant </body>
    content = content.replace("</body>", js + "</body>")

    with open(MAP_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def start_server():
    global _server_thread
    if _server_thread and _server_thread.is_alive():
        print("✅ Serveur déjà en cours.")
        return

    def run_server():
        os.chdir('.')  # servir fichiers dans répertoire courant
        with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
            print(f"🚀 Serveur en ligne : http://localhost:{PORT}")
            httpd.serve_forever()

    _server_thread = threading.Thread(target=run_server, daemon=True)
    _server_thread.start()

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return
    
    def do_GET(self):
        if self.path == "/position":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            avion_data = {
                'latitude': 0,
                'longitude': 0,
                'heading': 0
            }

            if dynamic_point:
                avion_data.update({
                    'latitude': dynamic_point.get('latitude', 0),
                    'longitude': dynamic_point.get('longitude', 0),
                    'heading': dynamic_point.get('heading', 0),
                })

            self.wfile.write(json.dumps({
                'avion': avion_data,
                'points': dynamic_points,
                'lines': dynamic_lines
            }).encode())
        else:
            super().do_GET()

def move_avion(avion):
    global dynamic_point
    if dynamic_point is None:
        dynamic_point = avion.copy()
    else:
        dynamic_point['latitude'] = avion['latitude']
        dynamic_point['longitude'] = avion['longitude']
        dynamic_point['altitude'] = avion.get('altitude', 0)
        dynamic_point['heading'] = avion['heading']

def add_dynamic_point(point):
    dynamic_points.append(point.copy())

def update_dynamic_point(point):
    for i, p in enumerate(dynamic_points):
        if p.get('label') == point.get('label'):
            dynamic_points[i] = point.copy()  # Met à jour le point existant
            return
    dynamic_points.append(point.copy())  # Ajoute si pas trouvé

dynamic_lines = []  # liste globale de dicts {label: ..., coords: [...]}

def add_dynamic_line(line):
    global dynamic_lines
    dynamic_lines.append({
        'label': line['label'],
        'coords': [{'latitude': p['latitude'], 'longitude': p['longitude']} for p in line['coords']]
    })

def update_dynamic_line(line):
    global dynamic_lines
    for i, l in enumerate(dynamic_lines):
        if l['label'] == line['label']:
            dynamic_lines[i]['coords'] = [{'latitude': p['latitude'], 'longitude': p['longitude']} for p in line['coords']]
            return
    # Si pas trouvé, on ajoute la nouvelle ligne
    add_dynamic_line(line)
