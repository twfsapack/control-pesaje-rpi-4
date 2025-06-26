import RPi.GPIO as GPIO
def setup_valves(valve_pins):
    for pin in valve_pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

def control_valve(valve_pin, state):
    GPIO.output(valve_pin, GPIO.HIGH if state else GPIO.LOW)
