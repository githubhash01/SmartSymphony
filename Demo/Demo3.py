# Simple python file used for demo only


from LED import LEDStrip
from CentralMicrophone import Microphone
from Controller import Controller


mic = Microphone()

led = LEDStrip(5, True)

controller = Controller(led, mic)
controller.run()







