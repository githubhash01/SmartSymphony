import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

class Actuators:
    def __init__(self):
        self.motorPins = [12, 5, 16, 18, 22, 24, 26]
        for pin in self.motorPins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
    
    async def play(self, timeline):
        while timeline.playing():
            event = timeline.get_event()
            if event.key.actuator:
                if event.event_type == 1:
                    GPIO.output(event.key.actuator, GPIO.HIGH)
                else:
                    GPIO.output(event.key.actuator, GPIO.LOW)
            await timeline.wait()