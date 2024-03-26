import board
import neopixel
import asyncio
from VariableMicrophone import Tuner
from timeline import Timeline
import time 
class Lightstrip:
    
    OFF = (0, 0, 0 , 0) 
    GREEN = (0, 255, 0, 0) 
    RED = (255, 0, 0, 0)
    BLUE = (0, 0, 255, 0)

    def __init__(self, brightness=0.2, wait=1, midi_file=None):
        self.num_pixels =  97
        self.pixel_pin = board.D18
        
        self.wait = wait
        self.timeline = Timeline(midi_file) 
        self.brightness = brightness
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
            
    # turn off strip 
    def turnOffStrip(self):
        self.pixels.fill((0, 0, 0, 0))
    
    def updateKey(self, key, key_status):
        leds = [key.led_num, key.led_num + 1]
        color = Lightstrip.OFF
        # if the key is being turned on 
        if key_status:
            color = Lightstrip.RED if '#' in key.note else Lightstrip.GREEN
        for l in leds: 
            self.pixels[l] = color
        self.pixels.show()
        time.sleep(self.wait) 
    

    async def play(self, timeline):  
        try:
            await timeline.wait()
            self.turnOffStrip()
            while timeline.playing():
                event = timeline.get_event()
                self.updateKey(event.key, event.event_type) 
                await timeline.wait()
        except Exception as e:
            print(e)
        self.turnOffStrip()

"""

async def main():
    MIDI_FILE = '/home/pi/Desktop/app/SmartSymphonyHardware/Test_LEDIntegration/Marriagedamour.mid'
    LEDStrip = Lightstrip(wait=0.2)
    time = Timeline(MIDI_FILE)
    await LEDStrip.play(time) 
        

if __name__ == "__main__":
    asyncio.run(main())
      
"""
