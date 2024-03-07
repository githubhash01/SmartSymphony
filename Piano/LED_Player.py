import mido 
import time
from rpi_ws281x import *

GREEN = Color(0, 255, 0)
OFF = Color(0, 0, 0)
    
class LEDStrip:

    # Class variables for colors


    def __init__(self, brightness=30):
        self.LED_COUNT = 60
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
        time.sleep(2)
        self.turnOff()
        time.sleep(0.5) 
        print('Starting LED Strip')
        self.colorWipe()
        self.turnOff()
        time.sleep(0.5)
        print('LED Strip Ready!') 
        

    def colorWipe(self,wait_ms=30):
        for i in range(self.LED_COUNT):
            self.strip.setPixelColor(i, GREEN)
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    def playSet(self, notes):
        print(notes) 
        for i in range(self.LED_COUNT):
            if i not in notes:
                self.strip.setPixelColor(i, OFF)
            elif i in notes:
                self.strip.setPixelColor(i, GREEN)
        self.strip.show()
        
    def playNotes(self, notes):
        # if the list is empty then return
        print(notes) 
        if not notes:
            return
        for note in notes:
            self.strip.setPixelColor(note, GREEN)
        self.strip.show()

    def turnOffNotes(self, notes):
        if not notes:
            return
        for note in notes:
            self.strip.setPixelColor(note, OFF)
        self.strip.show()

    def turnOff(self):
        for i in range(self.LED_COUNT):
            self.strip.setPixelColor(i, OFF)
        self.strip.show()



class Midi_Reader:

    def __init__(self, file_path):
        self.midi_file = mid = mido.MidiFile(str(file_path), clip=True)
        self.active_LEDS = set()  # Set to keep track of active (currently playing) LEDs
        
        self.LED_Strip = LEDStrip()
        self.LED_Strip.begin()

    # will convert notes to 61-key keyboard index
    def piano_converter(self, note_number):
        start_note = 36
        if start_note <= note_number <= 96:
            return note_number - start_note
        else:
            raise ValueError("Note number is out of range for a 61-key keyboard")
        
    # Only works given piano_channel is 0
    
    def midi_playback(self, playback_speed=1, piano_channel=0):
        for msg in self.midi_file.play():
            if not msg.is_meta and msg.channel == piano_channel:
                if msg.type == 'note_on' and msg.velocity > 0:
                    self.active_LEDS.add(self.piano_converter(msg.note))
                    if msg.time > 0: 
                        time.sleep(playback_speed*msg.time)
                        self.LED_Strip.playSet(self.active_LEDS)
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    self.active_LEDS.discard(self.piano_converter(msg.note))
                    if msg.time > 0:
                        time.sleep(playback_speed*msg.time)
                        #print(self.active_LEDS)
                    
# Example usage
midi_reader = Midi_Reader("fur-elise.mid")
midi_reader.midi_playback()

