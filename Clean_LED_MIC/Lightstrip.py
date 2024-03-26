"""
A simple script to control the LED on a NeoPixel/WS2812/SK6812
"""
import board
import neopixel
import time
from MidiProcessor import parseMidi
from Keys import * 

MIDI_FILE = 'Ode-To-Joy.mid'
NUM_PIXELS = 97
PIXEL_PIN = board.D18
BRIGHTNESS = 0.2 # 20% brightness

OFF = (0, 0, 0, 0)
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
        
    # upon turning on strip, and to check all leds are working and responsive 
    def colorWipe(self, color, wait_ms=0.01):
        for i in range(self.num_pixels):
            self.pixels[i] = color
            self.pixels.show()
            time.sleep(wait_ms)
            
    def show(self):
        self.pixels.show()
    # turn off strip 
    def turnOffStrip(self):
        self.pixels.fill((0, 0, 0, 0))
    
    def updateKeyColor(self, key, key_status):
        leds = [key.led_num, key.led_num + 1]
        color = OFF
        # if the key is being turned on 
        if key_status:
            color = RED if '#' in key.note else GREEN
        for l in leds: 
            self.pixels[l] = color
        #self.pixels.show()
    
    def playMidi(self, midi_file, speed=1): 
        timeline = parseMidi(midi_file)
        # each time has a list of events 
        events_by_time = defaultdict(list) 
        for event_time, wait, event in timeline:
            events_by_time[event_time].append(event)
            
        for t in events_by_time:
            for event in events_by_time[t]:
                self.updateKeyColor(key=event.key, key_status=event.event_type)
            #time.sleep(0.001 * wait / (speed)) 
        self.turnOffStrip()
        
        
        
"""
strip = Strip()
print('Color Wipe')
strip.colorWipe(BLUE)
time.sleep(2)
strip.turnOffStrip()

# Now play some 
print('Playing music')
strip.playMidi(MIDI_FILE, 1)
"""
