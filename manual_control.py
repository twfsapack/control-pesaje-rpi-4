import RPi.GPIO as GPIO
def toggle_output(pin):
    current = GPIO.input(pin)
    GPIO.output(pin, not current)
    return not current

def set_output(pin, state):
    GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)
