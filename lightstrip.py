import board
import neopixel
import asyncio
from timeline import Timeline

class Lightstrip:
    # Class variables for colors
    NUM_PIXELS = 97
    PIXEL_PIN = board.D18
    
    BRIGHTNESS = 0.2 # 20% brightness
    
    BLACK = (0, 0, 0, 0)
    GREEN = (50, 255, 50, 0)
    DARK_GREEN = (0, 255, 0, 0)
    RED = (255, 0, 0, 0)
    DARK_RED = (255, 50, 50, 0)
    BLUE = (0, 0, 255, 0)
    DARK_BLUE = (50, 50, 255, 0)

    def __init__(self):
        self.num_pixels = Lightstrip.NUM_PIXELS
        self.pixel_pin = Lightstrip.PIXEL_PIN
        self.brightness = Lightstrip.BRIGHTNESS
        self.pixels = neopixel.NeoPixel(self.pixel_pin, 
                                        self.num_pixels, 
                                        brightness=self.brightness, 
                                        auto_write=True, 
                                        pixel_order=neopixel.GRBW)
        self.pixelsList = [[Lightstrip.BLACK] for _ in self.pixels]
        self.turnOff()
            
    def turnOff(self):
        self.pixels.fill(Lightstrip.BLACK)
        self.pixelsList = [[Lightstrip.BLACK] for _ in self.pixels]

    def lightPixels(self, leds, colour):
        for l in leds:
            self.pixelsList[l].append(colour)
            self.pixels[l] = colour

    def turnOffPixels(self, leds, colour):
        for l in leds:
            try:
                self.pixelsList[l].remove(colour)
                self.pixels[l] = self.pixelsList[l][-1]
            except:
                pass
    
    def get_leds(self, key):
        return [key.led_num, key.led_num + 1]
    
    def get_colour(self, key, hand):
        white_key = key.note[1] == "#"
        if hand == "left":
            return Lightstrip.RED if white_key else Lightstrip.DARK_RED
        elif hand == "right": 
            return Lightstrip.GREEN if white_key else Lightstrip.DARK_GREEN
        else:
            return Lightstrip.BLUE if white_key else Lightstrip.DARK_BLUE
    
    def start_note(self, key, hand=None):
        leds = self.get_leds(key)
        self.lightPixels(leds, self.get_colour(key, hand)) # event note is a string 'C6'
        self.pixels.show()
    
    def stop_note(self, key, hand=None):
        leds = self.get_leds(key)
        self.turnOffPixels(leds, self.get_colour(key, hand))
        self.pixels.show()
    
    async def play_note(self, key, length):
        try:
            self.start_note(key)
            await asyncio.sleep(length)
            self.stop_note(key)
        except Exception as e:
            print(e)
    
    async def play(self, timeline, hand, output):
        try:
            await timeline.wait()
            while timeline.playing():
                events = timeline.get_events()
                for event in events:
                    if event.event_type == 1:
                        self.start_note(event.key, hand)
                    elif event.event_type == 0:
                        self.stop_note(event.key, hand)
                if output and event.event_type == 1:
                    notes = set()
                    for event in events:
                        if event.event_type == 1:
                            notes.add(event.key.note)
                    await output.set_awaiting(hand, notes)
                await timeline.wait()
            self.turnOffStrip()
        except Exception as e:
            print(e)
      