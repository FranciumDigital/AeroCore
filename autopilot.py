from pid import PIDController
import oscillo

throttle_pid = PIDController(14, 0.5, 0)

heading_pid = PIDController(1, 0, 0)
bank_pid = PIDController(0.04, 0.02, 0)

altitude_pid = PIDController(0.04, 0.02, 0)
pitch_pid = PIDController(0.04, 0.02, 0)

def init():
    print("init")

def throttle(dt, actual_airspeed, target_airspeed):
    if (actual_airspeed is not None):
        command = throttle_pid.compute(actual_airspeed, target_airspeed, dt)
        command = max(0, min(command, 100))
        return command
    return 0

def heading(dt, actual_heading, target_heading):
    if (actual_heading is not None):
        if(actual_heading>180):
            actual_heading-=360
        if(target_heading>180):
            target_heading-=360
        command = heading_pid.compute(actual_heading, target_heading, dt)
        command = max(-20, min(command, 20))
        return command
    return 0

def bank(dt, actual_bank, target_bank):
    if (actual_bank is not None):
        command = bank_pid.compute(actual_bank, target_bank, dt)
        command = max(-100, min(command, 100))
        return command
    return 0

def altitude(dt, actual_altitude, target_altitude):
    if (actual_altitude is not None):
        command = altitude_pid.compute(actual_altitude, target_altitude, dt)
        command = max(-10, min(command, 10))
        return command
    return 0

def pitch(dt, target_pitch, actual_data, target_data):
    if (actual_data['pitch'] is not None):
        if (actual_data['elevator'] == target_data['elevator']):
            target_data['elevator'] = pitch_pid.compute(actual_data['pitch'], target_pitch, dt)
            target_data['elevator'] = max(-100, min(target_data['elevator'], 100))
        else:
            target_data['elevator'] = actual_data['elevator']
    return 99

def compute(dt, actual_data, target_data):
        target_data['throttle'] = throttle(dt, actual_data['airspeed'], target_data['airspeed'])
        
        heading_command = heading(dt, actual_data['heading'], target_data['heading'])
        oscillo.channel[0] = actual_data['heading']
        oscillo.channel[1] = target_data['heading']
        target_data['aileron'] = bank(dt, actual_data['bank'], heading_command)

        altitude_command = altitude(dt, actual_data['altitude'], target_data['altitude'])
        pitch(dt, altitude_command, actual_data, target_data)

        #if AIRPLANE_ACTUAL_DATA['bank'] is not None:
        #    aileron_cmd = calculer_pid(target_bank, AIRPLANE_ACTUAL_DATA['bank'], 0.04, 0.02, 0, dt, pid_states['bank'])
        #    aileron_cmd = max(-100, min(aileron_cmd, 100))

        #if AIRPLANE_ACTUAL_DATA['altitude'] is not None:
        #    target_pitch = calculer_pid(target_altitude, AIRPLANE_ACTUAL_DATA['altitude'], 0.4, 0.02, 0, dt, pid_states['height'])
        #    target_pitch = max(-10, min(target_pitch, 10))

        #if AIRPLANE_ACTUAL_DATA['pitch'] is not None:
        #    elevator_cmd = calculer_pid(target_pitch, AIRPLANE_ACTUAL_DATA['pitch'], 0.04, 0.02, 0, dt, pid_states['pitch'])
        #    elevator_cmd = max(-100, min(elevator_cmd, 100))
        #    #print(target_altitude," - ",actual_altitude," - ",target_pitch," - ",actual_pitch," - ",elevator_cmd)

        #if AIRPLANE_ACTUAL_DATA['actual_heading'] is None:
        #    if(AIRPLANE_ACTUAL_DATA['actual_heading']>180):
        #        AIRPLANE_ACTUAL_DATA['actual_heading']-=360
        #    if(target_heading>180):
        #        target_heading-=360
        #    heading_cmd = calculer_pid(target_heading, AIRPLANE_ACTUAL_DATA['actual_heading'], 0.03, 0, 0, dt, pid_states['heading'])
        #    heading_cmd = max(-100, min(heading_cmd, 100))