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
    ORANGE = (255, 220, 125, 0)
    DARK_ORANGE = (255, 187, 0, 0)
    BLUE = (122, 122, 255, 0)
    DARK_BLUE = (0, 0, 255, 0)
    WHITE = (255, 255, 255, 0)
    DARK_WHITE = (180, 180, 180, 0)

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
        self.turn_off()
            
    def stop(self):
        self.pixels.fill(Lightstrip.BLACK)
        self.pixelsList = [[Lightstrip.BLACK] for _ in self.pixels]
    
    def pause(self):
        pass

    def light_pixels(self, leds, colour):
        for l in leds:
            self.pixelsList[l].append(colour)
            self.pixels[l] = colour

    def disable_pixels(self, leds, colour):
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
            return Lightstrip.BLUE if white_key else Lightstrip.DARK_BLUE
        elif hand == "right": 
            return Lightstrip.ORANGE if white_key else Lightstrip.DARK_ORANGE
        else:
            return Lightstrip.WHITE if white_key else Lightstrip.DARK_WHITE
    
    def start_note(self, key, hand=None):
        leds = self.get_leds(key)
        self.light_pixels(leds, self.get_colour(key, hand)) # event note is a string 'C6'
        self.pixels.show()
    
    def stop_note(self, key, hand=None):
        leds = self.get_leds(key)
        self.disable_pixels(leds, self.get_colour(key, hand))
        self.pixels.show()
    
    async def play_note(self, key, length):
        try:
            self.start_note(key)
            await asyncio.sleep(length)
            self.stop_note(key)
        except Exception as e:
            print(e)