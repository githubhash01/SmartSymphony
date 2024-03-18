from rpi_ws281x import *

class Lightstrip:
    # Class variables for colors
    GREEN = Color(0, 255, 0)
    OFF = Color(0, 0, 0)

    def __init__(self, brightness):
        self.LED_COUNT = 128
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
        self.strip.begin()
        
    def switchOnLED(self, led_index):
        self.strip.setPixelColor(led_index, Lightstrip.GREEN)

    def switchOffLED(self, led_index):
        self.strip.setPixelColor(led_index, Lightstrip.OFF)

    async def play(self, timeline):
        while timeline.playing():
            event = timeline.get_event()
            if event.event_type == 1:
                self.switchOnLED(event.key.led_num)
            else:
                self.switchOffLED(event.key.led_num)
            self.strip.show()
            await timeline.wait()