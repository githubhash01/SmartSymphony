import time
from rpi_ws281x import *

class LEDStrip:

    # Class variables for colors
    GREEN = Color(0, 255, 0)
    OFF = Color(0, 0, 0)

    def __init__(self, brightness, reverse=False):
        self.LED_COUNT = 60
        self.LED_PIN = 18 # must be PWM
        self.LED_FREQ_HZ = 800000
        self.DMA = 10
        self.INVERT = False
        self.BRIGHTNESS = brightness
        self.LED_CHANNEL = 0
        self.REVERSE = reverse
        self.strip = Adafruit_NeoPixel(self.LED_COUNT, 
                                       self.LED_PIN, 
                                       self.LED_FREQ_HZ, 
                                       self.DMA, 
                                       self.INVERT,
                                       self.BRIGHTNESS,
                                       self.LED_CHANNEL)
        
    def begin(self):
        self.strip.begin()

    def colorWipe(self, color=GREEN, wait_ms=100):
        for i in range(self.LED_COUNT):
            self.strip.setPixelColor(i, color)
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    def playSet(self, notes):
        self.turnOff()
        self.playNotes(notes)
    
    def playNote(self, note):
        if self.REVERSE:
            note = 60 - note
        self.strip.setPixelColor(note, LEDStrip.GREEN)
        self.strip.show()
        
    def playIndex(self, index):
        self.strip.setPixelColor(index, LEDStrip.GREEN) 
        
    def turnOffNote(self, note):
        if self.REVERSE:
            note = 60 - note
        self.strip.setPixelColor(note, LEDStrip.OFF) 
        
    def playNotes(self, notes, wait=0):
        # if the list is empty then return 
        if not notes:
            return
        for note in notes:
            self.playNote(note)
        self.strip.show()
        if wait > 0: 
            time.sleep(wait) 

    def turnOffNotes(self, notes):
        if not notes:
            return
        for note in notes:
            self.turnOffNote(note)
        self.strip.show()

    def turnOff(self):
        for i in range(self.LED_COUNT):
            self.strip.setPixelColor(i, LEDStrip.OFF)
        self.strip.show()


