import board
import neopixel 

PIXEL_PIN=board.D18

NUM_PIXELS=60

ORDER=neopixel.GRB

pixels=neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=1, auto_write=False, pixel_order=ORDER)

pixels.fill((255,0,0))
pixels.show()
