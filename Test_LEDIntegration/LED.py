import time
from rpi_ws281x import *
from MidiProcessor import parseMidi

class LEDStrip:

    # Class variables for colors
    GREEN = Color(0, 255, 0)
    OFF = Color(0, 0, 0)

    def __init__(self, brightness):
        self.LED_COUNT = 144
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

    def colorWipe(self, color=GREEN, wait_ms=50):
        for i in range(self.LED_COUNT):
            self.strip.setPixelColor(i, color)
            self.strip.show()
            time.sleep(wait_ms/1000.0)
        self.turnOffStrip()

    def playSet(self, led_index):
        self.turnOff()
        self.lightLEDS(led_index)
        
    def switchOnLED(self, led_index):
        self.strip.setPixelColor(led_index, LEDStrip.GREEN)

    def switchOffLED(self, led_index):
        self.strip.setPixelColor(led_index, LEDStrip.OFF)

    def show(self):
        self.strip.show()

    def lightLEDS(self, led_indices):
        # if the list is empty then return 
        if not led_indices:
            return
        for led_index in led_indices:
            self.strip.setPixelColor(led_index, LEDStrip.GREEN)
        self.strip.show()

    def turnOffLEDS(self, led_index):
        if not led_index:
            return
        for note in led_index:
            self.strip.setPixelColor(note, LEDStrip.OFF)
        self.strip.show()

    def turnOffStrip(self):
        for i in range(self.LED_COUNT):
            self.strip.setPixelColor(i, LEDStrip.OFF)
        self.strip.show()

    def playMidi(self, midi_file, speed=1.0):
        timeline = parseMidi(midi_file)
        for event_time, wait, event in timeline:
            print(event_time, wait, 'ON' if event.event_type else 'OFF', event.key.note, event.key.led_num)
            if event.event_type == 1:
                self.switchOnLED(event.key.led_num)
            else:
                self.switchOffLED(event.key.led_num)
            self.show()
            time.sleep(wait/(speed*1000))  # sleep for the duration of the note


# demoing the LEDStrip class with a midi file
LEDStrip = LEDStrip(50) # brightness set to 20/255
LEDStrip.begin()
LEDStrip.colorWipe()

"""
MIDI_FILE = 'Marriagedamour.mid'
LEDStrip.begin()
LEDStrip.colorWipe()
LEDStrip.playMidi(MIDI_FILE, 0.12)  
"""

