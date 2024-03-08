import time
from rpi_ws281x import *

class LEDStrip:

    # Class variables for colors
    GREEN = Color(0, 255, 0)
    OFF = Color(0, 0, 0)

    def __init__(self, brightness):
        self.LED_COUNT = 60
        self.LED_PIN = 18 # must be PWM
        self.LED_FREQ_HZ = 800000
        self.DMA = 10
        self.INVERT = False
        self.BRIGHTNESS = brightness
        self.LED_CHANNEL = 0
        self.strip = Adafruit_NeoPixel(self.LED_COUNT, 
                                       self.LED_PIN, 
                                       self.LED_FREQ_HZ, 
                                       self.DMA, 
                                       self.INVERT,
                                       self.BRIGHTNESS,
                                       self.LED_CHANNEL)
        
    def begin(self):
        self.strip.begin()

    def colorWipe(self, color, wait_ms=500):
        for i in range(self.LED_COUNT):
            self.strip.setPixelColor(i, color)
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    def playSet(self, notes):
        self.turnOff()
        self.playNotes(notes)
        
    def playNotes(self, notes):
        # if the list is empty then return 
        if not notes:
            return
        for note in notes:
            self.strip.setPixelColor(note, LEDStrip.GREEN)
        self.strip.show()

    def turnOffNotes(self, notes):
        if not notes:
            return
        for note in notes:
            self.strip.setPixelColor(note, LEDStrip.OFF)
        self.strip.show()

    def turnOff(self):
        for i in range(self.LED_COUNT):
            self.strip.setPixelColor(i, LEDStrip.OFF)
        self.strip.show()


