import board
import neopixel

class Lightstrip:
    # Class variables for colors
    NUM_PIXELS = 97
    PIXEL_PIN = board.D18
    BRIGHTNESS = 0.2 # 20% brightness

    GREEN = (0, 255, 0, 0) 
    RED = (255, 0, 0, 0)
    BLUE = (0, 0, 255, 0)

    def __init__(self):
        self.num_pixels = Lightstrip.NUM_PIXELS
        self.pixel_pin = Lightstrip.PIXEL_PIN
        self.brightness = Lightstrip.BRIGHTNESS
        self.pixels = neopixel.NeoPixel(self.pixel_pin, 
                                        self.num_pixels, 
                                        brightness=self.brightness, 
                                        auto_write=True, 
                                        pixel_order=neopixel.GRBW)
            
    def turnOffStrip(self):
        self.pixels.fill((0, 0, 0, 0))

    def lightPixels(self, leds, color):
        for l in leds: 
            self.pixels[l] = color

    def turnOffPixels(self, leds):
        for l in leds:
            self.pixels[l] = (0, 0, 0, 0)
            
            
    

    async def play(self, timeline):
        try:
            await timeline.wait()
            self.turnOffStrip()
            while timeline.playing():
                event = timeline.get_event()
                print(timeline.current_instruction)
                if event.event_type == 1:
                    leds = [event.key.led_num -3, event.key.led_num - 2] 
                    self.lightPixels(leds, Lightstrip.GREEN) # event note is a string 'C6'
                elif event.event_type == 0: 
                    leds = [event.key.led_num -3, event.key.led_num - 2]
                    self.turnOffPixels(leds)
                self.pixels.show()
                await timeline.wait()
        except Exception as e:
            print(e)
        self.turnOffStrip()
