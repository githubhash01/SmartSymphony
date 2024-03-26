import pyaudio
import sys
import numpy as np
import aubio
from keys import Key
import asyncio

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
        self.pitch_o.set_tolerance(2.0)
        self.running = False
        self.note = None
        self.notes = set()
        self.awaiting = False
    
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
    
    async def set_awaiting(self, notes):
        self.awaiting = True
        while True:
            if notes.issubset(self.notes):
                break
            await asyncio.sleep(0)
        self.awaiting = False
    
    async def await_other(self):
        while self.awaiting:
            await asyncio.sleep(0)
    
    def is_awaiting(self):
        return self.awaiting
    
    def get_notes(self):
        return self.notes
    
    def calculate_notes(self):
        if not self.running:
            raise Exception("Trying to calculate note without starting mic, aborting...")
        audiobuffer = self.stream.read(1024, exception_on_overflow=False)
        signal = np.fromstring(audiobuffer, dtype=np.float32)

        key_num = int(np.round(self.pitch_o(signal)[0])) - 12
        self.notes.clear()
        if key_num != 0:
            key = Key(key_num).note
            self.notes.add(key)