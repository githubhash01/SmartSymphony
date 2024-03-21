import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

class Actuators:
    def __init__(self):
        self.motorPins = [12, 13, 5, 6, 16, 17, 22, 23, 24, 25, 26, 27]
        for pin in self.motorPins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
    
    async def play(self, timeline):
        try:
            await timeline.wait()
            while timeline.playing():
                event = timeline.get_event()
                if event.key.actuator:
                    if event.event_type == 1:
                        GPIO.output(event.key.actuator, GPIO.HIGH)
                    else:
                        GPIO.output(event.key.actuator, GPIO.LOW)
                await timeline.wait()
        except Exception as e:
            print(e)