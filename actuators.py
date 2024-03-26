import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

class Actuators:
    def __init__(self):
        self.motorPins = [23,12,22,13,25,24,6,5,16,26,17,27]
        for pin in self.motorPins:
            GPIO.setup(pin, GPIO.OUT)
    
    def turnOff(self):
        for pin in self.motorPins:
            GPIO.output(pin, GPIO.LOW)
    
    async def play_note(self, key, length):
        try:
            GPIO.output(event.key.actuator, GPIO.HIGH)
            await asyncio.sleep(length)
            GPIO.output(event.key.actuator, GPIO.LOW)
        except Exception as e:
            print(e)
    
    async def play(self, timeline, hand, output):
        try:
            await timeline.wait()
            while timeline.playing():
                events = timeline.get_events()
                for event in events:
                    if event.key.actuator:
                        if event.event_type == 1:
                            GPIO.output(event.key.actuator, GPIO.HIGH)
                        else:
                            GPIO.output(event.key.actuator, GPIO.LOW)
                await timeline.wait()
        except Exception as e:
            print(e)