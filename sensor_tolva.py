import RPi.GPIO as GPIO
def setup_sensor(sensor_pin):
    GPIO.setup(sensor_pin, GPIO.IN)

def is_product_available(sensor_pin):
    return GPIO.input(sensor_pin) == GPIO.HIGH
