from SimConnect import *
from math import *
import time
import autopilot
import map
import oscillo
import threading
import subprocess
import os
import stats
import variables

# Connexion SimConnect
sm = SimConnect()
aq = AircraftRequests(sm)

POINT_A = { # Paris
    'label': "POINT_A",
    'name': "PARIS",
    'latitude': 48.8566,
    'longitude': 2.3522,
    'altitude': 3000,
    'heading': 0,
    "icon": {
        "type": "color",
        "value": "green",
    }
}

POINT_B = { # Londres Heathrow
    'label': "POINT_B",
    'name': "LONDRES",
    'latitude': 51.3032,
    'longitude': 00.0332,
    'altitude': 1000,
    'heading': 0,
    "icon": {
        "type": "color",
        "value": "red",
    }
}

POINT_C = {
    'label': "POINT_C",
    'latitude': 0,
    'longitude': 0,
    'altitude': 0,
    'heading': 0,
    "icon": {
        "type": "color",
        "value": "blue",
    }
}

POINT_D = { # Aérodrome de Saint-François
    'label': "POINT_D",
    'name': "Aérodrome de Saint-François",
    'latitude': 16.2528,
    'longitude': -61.2545,
    'altitude': 2000,
    'heading': 0,
    "popup": "Départ",
    "icon": {
        "type": "color",  # ou "image"
        "value": "green"  # nom de couleur ou chemin image
    }
}

AIRPLANE = {
    # Avion
    'label': "AVION",
    'name': "Zlin Savage Cub",
    # Vitesses (en knots)
    'maximum_speed': 97,          # Vitesse max de croisière (Vno)
    'cruise_speed': 81,           # Vitesse de croisière
    'stall_speed': 33,            # Vitesse de décrochage
    'absolute_maximum_speed': 108,# Vne - Never Exceed Speed
    # Performances
    'range': 390,                 # Autonomie maximale (~430 km)
    'service_ceiling': 14400,     # Plafond opérationnel
    'climb_rate': 940,            # Vitesse de montée (ft/min)
    # Limitations d’attitude
    'max_bank_angle': 30,         # Inclinaison max recommandée
    'max_pitch_angle': 20,        # Tangage max typique (montée/descente)
    # Capacités
    'fuel_capacity': 64,          # Carburant (litres)
    'engine_power': 80,           # Puissance moteur
    # Configuration
    'seats': 2,
    'category': 'cub',
}

AIRPLANE_ACTUAL_DATA = {
    'label': "AIRPLANE_ACTUAL_DATA",
    'airspeed': 0,
    'bank': 0,
    'pitch': 0,
    'altitude': 0,
    'heading': 0,
    'throttle': 0,
    'aileron': 0,
    'elevator': 0,
    'rudder': 0,
    'latitude': 0,
    'longitude': 0,
    "icon": {
        "type": "image",
        "value": "purple-circle-icon.png",
    }
}

AIRPLANE_TARGET_DATA = {
    'label': "AIRPLANE_TARGET_DATA",
    'airspeed': 80,
    'bank': 0,
    'pitch': 0,
    'altitude': 2000,
    'heading': 0,
    'throttle': 0,
    'aileron': 0,
    'elevator': 0,
    'rudder': 0,
}

LIGNE_AB = {
    'label': "LIGNE_AB",
    'coords': [POINT_A, POINT_B]
}

LIGNE_AC = {
    'label': "LIGNE_AC",
    'coords': [POINT_A, POINT_C]
}

LIGNE_BC = {
    'label': "LIGNE_BC",
    'coords': [POINT_B, POINT_C]
}

LIGNE_XB = {
    'label': "LIGNE_XB",
    'coords': [AIRPLANE_ACTUAL_DATA, POINT_B]
}

LIGNE_XC = {
    'label': "LIGNE_XC",
    'coords': [AIRPLANE_ACTUAL_DATA, POINT_C]
}

def teleport_to_point(point):
    try:
        aq.set("PLANE_LATITUDE", point['latitude'])
        aq.set("PLANE_LONGITUDE", point['longitude'])
        aq.set("PLANE_ALTITUDE", point['altitude'])
        aq.set("PLANE_HEADING_DEGREES_MAGNETIC", point['heading'])
        aq.set("PLANE_BANK_DEGREES", 0)
        aq.set("PLANE_PITCH_DEGREES", 0)
        aq.set("AIRSPEED_TRUE", AIRPLANE['cruise_speed'])
        print(f"Téléportation effectuée vers lat={point['latitude']}, lon={point['longitude']}")
    except Exception as e:
        print("Erreur téléportation:", e)

def distance(p1, p2):
    return sqrt((p2['latitude'] - p1['latitude'])**2 + (p2['longitude'] - p1['longitude'])**2)

def calculateur():

    POINT_C['latitude'] = POINT_B['latitude']
    POINT_C['longitude'] = AIRPLANE_ACTUAL_DATA['longitude']

    BC = distance(POINT_B, POINT_C)
    CA = distance(POINT_C, POINT_A)

    angle_rad = atan(BC / CA)
    AIRPLANE_TARGET_DATA['heading'] = -degrees(angle_rad)


def inputs():
    try:
        AIRPLANE_ACTUAL_DATA['airspeed'] = aq.get("AIRSPEED_INDICATED")
        AIRPLANE_ACTUAL_DATA['bank'] = -degrees(aq.get("PLANE_BANK_DEGREES"))
        AIRPLANE_ACTUAL_DATA['pitch'] = -degrees(aq.get("PLANE_PITCH_DEGREES"))
        AIRPLANE_ACTUAL_DATA['altitude'] = aq.get("PLANE_ALTITUDE")
        AIRPLANE_ACTUAL_DATA['heading'] = degrees(aq.get("PLANE_HEADING_DEGREES_MAGNETIC"))
        AIRPLANE_ACTUAL_DATA['throttle'] = aq.get("GENERAL_ENG_THROTTLE_LEVER_POSITION:1")
        AIRPLANE_ACTUAL_DATA['aileron'] = aq.get("AILERON_POSITION")
        AIRPLANE_ACTUAL_DATA['elevator'] = aq.get("ELEVATOR_POSITION")
        AIRPLANE_ACTUAL_DATA['rudder'] = aq.get("RUDDER_POSITION")
        AIRPLANE_ACTUAL_DATA['latitude'] = aq.get("PLANE_LATITUDE")
        AIRPLANE_ACTUAL_DATA['longitude'] = aq.get("PLANE_LONGITUDE")
    except:
        print("inputs() -- SimConnect Error")

def outputs():
    aq.set("GENERAL_ENG_THROTTLE_LEVER_POSITION:1", AIRPLANE_TARGET_DATA['throttle'])
    variables.throttle_command = AIRPLANE_TARGET_DATA['throttle']
    
    aq.set("AILERON_POSITION", AIRPLANE_TARGET_DATA['aileron'])
    variables.aileron_command = AIRPLANE_TARGET_DATA['aileron']
    
    aq.set("ELEVATOR_POSITION", AIRPLANE_TARGET_DATA['elevator'])
    variables.elevator_command = AIRPLANE_TARGET_DATA['elevator']

    #aq.set("RUDDER_POSITION", commands['rudder'])
    
def main(): 
    i = 0
    dt = 0.001

    try:
         # Lancer le serveur Flask dans un thread daemon (arrière-plan)
        server_thread = threading.Thread(target=stats.run_server, daemon=True)
        server_thread.start()

        #teleport_to_point(POINT_A)
        map.start(POINT_A)
        map.add_dynamic_point(POINT_A)
        map.add_dynamic_point(POINT_B)
        map.move_avion(POINT_A)

        inputs()
        calculateur()
        map.add_dynamic_point(POINT_C)

        LIGNE_AB['coords'] = [POINT_A, POINT_B]
        LIGNE_AC['coords'] = [POINT_A, POINT_C]
        LIGNE_BC['coords'] = [POINT_B, POINT_C]
        LIGNE_XB['coords'] = [AIRPLANE_ACTUAL_DATA, POINT_B]
        LIGNE_XC['coords'] = [AIRPLANE_ACTUAL_DATA, POINT_C]

        #map.add_dynamic_line(LIGNE_AB)
        #map.add_dynamic_line(LIGNE_AC)
        map.add_dynamic_line(LIGNE_BC)
        map.add_dynamic_line(LIGNE_XB)
        map.add_dynamic_line(LIGNE_XC)




        autopilot.init()

        variables.target_airspeed = AIRPLANE_TARGET_DATA['airspeed']
        variables.target_altitude = AIRPLANE_TARGET_DATA['altitude']
        variables.target_heading = AIRPLANE_TARGET_DATA['heading']
        
        while True:   
            variables.actual_airspeed = AIRPLANE_ACTUAL_DATA['airspeed']
            variables.actual_altitude = AIRPLANE_ACTUAL_DATA['altitude']
            variables.actual_heading = AIRPLANE_ACTUAL_DATA['heading']

            #AIRPLANE_TARGET_DATA['airspeed'] = variables.target_heading
            #AIRPLANE_TARGET_DATA['altitude'] = variables.target_heading
            AIRPLANE_TARGET_DATA['heading'] = variables.target_heading

            #if(variables.teleport_airplane):
            #    teleport_to_point(POINT_D)
            #    i+=1
            #variables.teleport_airplane = False

            inputs()
            calculateur()
            autopilot.compute(dt, AIRPLANE_ACTUAL_DATA, AIRPLANE_TARGET_DATA)
            outputs()

            
            map.move_avion(AIRPLANE_ACTUAL_DATA)
            map.update_dynamic_point(POINT_C)
        
            LIGNE_BC['coords'] = [POINT_B, POINT_C]
            LIGNE_XB['coords'] = [AIRPLANE_ACTUAL_DATA, POINT_B]
            LIGNE_XC['coords'] = [AIRPLANE_ACTUAL_DATA, POINT_C]

            map.update_dynamic_line(LIGNE_BC)
            map.update_dynamic_line(LIGNE_XB)
            map.update_dynamic_line(LIGNE_XC)



            i += 1
            time.sleep(dt)
    except KeyboardInterrupt:
        print("Arrêt")

if __name__ == "__main__":
    thread = threading.Thread(target=main, daemon=True)
    thread.start()

    oscillo.init(-10, 370)