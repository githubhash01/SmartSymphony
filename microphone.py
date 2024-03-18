import pyaudio
import sys
import numpy as np
import aubio
from keys import Key

class Microphone:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32,
                            channels=1,
                            rate=44100,
                            input=True,
                            frames_per_buffer=1024,
                            start=False)
        self.pitch_o = aubio.pitch("default", 4096, 1024, 44100)
        self.pitch_o.set_unit("midi")
        self.pitch_o.set_tolerance(0.8)
        self.running = False
        self.note = None
        self.notes = set()
    
    def __del__(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
    
    def start(self):
        if not self.running:
            self.stream.start_stream()
            self.running = True
    
    def stop(self):
        if self.running:
            self.stream.stop_stream()
            self.running = False
    
    def get_notes(self):
        return self.notes
    
    def calculate_notes(self):
        if not self.running:
            raise Exception("Trying to calculate note without starting mic, aborting...")
        audiobuffer = self.stream.read(1024, exception_on_overflow=False)
        signal = np.fromstring(audiobuffer, dtype=np.float32)

        key_num = int(np.round(self.pitch_o(signal)[0]))
        self.notes.clear()
        if key_num != 0:
            key = Key(key_num).note
            self.notes.add(key)