from flask import Flask, render_template, request
import variables
import logging

app = Flask(__name__)

def safe_float(val, current):
    try:
        return float(val) if val.strip() != '' else current
    except ValueError:
        return current

@app.route('/', methods=['GET', 'POST'])
def airplane():
    if request.method == 'POST':
        if 'toggle' in request.form:
            variables.teleport_airplane = not variables.teleport_airplane

        elif 'apply' in request.form:
            variables.target_airspeed = safe_float(request.form.get('target_airspeed', ''), variables.target_airspeed)
            variables.target_altitude = safe_float(request.form.get('target_altitude', ''), variables.target_altitude)
            variables.target_heading = safe_float(request.form.get('target_heading', ''), variables.target_heading)

    return render_template('airplane.html', variables=variables)

@app.route('/stats', methods=['GET', 'POST'])
def stats():
    return render_template('stats.html', variables=variables)

def run_server():
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    app.run(debug=False, use_reloader=False)
