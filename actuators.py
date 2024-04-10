import RPi.GPIO as GPIO
import asyncio

GPIO.setmode(GPIO.BCM)

class Actuators:
    def __init__(self):
        self.motorPins = [23,12,22,13,25,24,6,5,16,26,17,27]
        for pin in self.motorPins:
            GPIO.setup(pin, GPIO.OUT)
    
    def stop(self):
        for pin in self.motorPins:
            GPIO.output(pin, GPIO.LOW)
    
    def pause(self):
        self.stop()
    
    def start_note(self, key, hand=None):
        GPIO.output(self.motorPins[key.actuator], GPIO.HIGH)
    
    def stop_note(self, key, hand=None):
        GPIO.output(self.motorPins[key.actuator], GPIO.LOW)
    
    async def play_note(self, key, length):
        try:
            GPIO.output(self.motorPins[key.actuator], GPIO.HIGH)
            await asyncio.sleep(length)
            GPIO.output(self.motorPins[key.actuator], GPIO.LOW)
        except Exception as e:
            print(e)