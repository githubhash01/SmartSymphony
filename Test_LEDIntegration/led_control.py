"""
A simple script to control the LED on a NeoPixel/WS2812/SK6812
"""
import board
import neopixel
import time
from MidiProcessor import parseMidi

MIDI_FILE = 'Ode-To-Joy.mid'
NUM_PIXELS = 97
PIXEL_PIN = board.D18
BRIGHTNESS = 0.2 # 20% brightness

GREEN = (0, 255, 0, 0) 
RED = (255, 0, 0, 0)
BLUE = (0, 0, 255, 0)

class Strip: 

    def __init__(self):
        self.num_pixels = NUM_PIXELS
        self.pixel_pin = PIXEL_PIN
        self.brightness = BRIGHTNESS
        self.pixels = neopixel.NeoPixel(self.pixel_pin, 
                                        self.num_pixels, 
                                        brightness=self.brightness, 
                                        auto_write=True, 
                                        pixel_order=neopixel.GRBW)
        
    def colorWipe(self, color, wait_ms=0.01):
        for i in range(self.num_pixels):
            self.pixels[i] = color
            self.pixels.show()
            time.sleep(wait_ms)
            
    def turnOffStrip(self):
        self.pixels.fill((0, 0, 0, 0))

    def lightPixels(self, leds, color):
        for l in leds: 
            self.pixels[l] = color

    def turnOffPixels(self, leds):
        for l in leds:
            self.pixels[l] = (0, 0, 0, 0)

    def playMidi(self, midi_file, speed=1): 
        timeline = parseMidi(midi_file)
        for event_time, wait, event in timeline:
            print(event.key.note)
            print(event.key.led_num)
            if event.event_type == 1:
                leds = [event.key.led_num -3, event.key.led_num -2] 
                self.lightPixels(leds, GREEN) # event note is a string 'C6'
            elif event.event_type == 0: 
                leds = [event.key.led_num -3, event.key.led_num + -2]
                self.turnOffPixels(leds)
            self.pixels.show()
            time.sleep(wait / (speed*1000))
        self.turnOffStrip()

strip = Strip()
print('Color Wipe')
strip.colorWipe(BLUE)
time.sleep(2)
strip.turnOffStrip()

# Now play some music!

print('Playing music')
strip.playMidi(MIDI_FILE, speed=1)
