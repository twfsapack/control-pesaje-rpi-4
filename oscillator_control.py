import threading, time, RPi.GPIO as GPIO
class Oscillator:
    def __init__(self, pin, ton, toff, delay):
        self.pin = pin
        self.ton = ton
        self.toff = toff
        self.delay = delay
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._oscillate)
        self.thread.start()

    def _oscillate(self):
        time.sleep(self.delay)
        while self.running:
            GPIO.output(self.pin, GPIO.HIGH)
            time.sleep(self.ton)
            GPIO.output(self.pin, GPIO.LOW)
            time.sleep(self.toff)

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
