from keys import Key, KeyEvent
import mido
import asyncio
import pretty_midi as pm
import time

class Timeline:
    def __init__(self, midi_file):
        self.speed = 1.0
        self.instructions = []
        midi_data = pm.PrettyMIDI(midi_file)
        for instrument in midi_data.instruments:
            for note in instrument.notes:
                self.instructions.append((note.start, KeyEvent(Key(note.pitch), 1)))
                self.instructions.append((note.end, KeyEvent(Key(note.pitch), 0)))
        self.instructions.sort(key=lambda x: x[0])
        wait_times = []
        for i in range(len(self.instructions) - 1):
            wait_time = self.instructions[i + 1][0] - self.instructions[i][0]
            wait_times.append(wait_time)
        wait_times.append(0.0)
        self.instructions = [(wait, event) for (time, event), wait in zip(self.instructions, wait_times)]
        self.current_instruction = 0
        self.current_event = None
        self.current_wait = 0.0
        self.waiting = False
        self.wait_time = 0.0
    
    def seek(self, time):
        self.current_instruction = 0
        current_time = 0.0
        for wait, _ in self.instructions:
            next_time = current_time + wait
            if next_time > time:
                break
            self.current_instruction += 1
            current_time = next_time
        self.current_wait = next_time - time
        self.waiting = True
    
    def playing(self):
        is_playing = self.instructions and self.current_instruction < len(self.instructions)
        if is_playing:
            wait, self.current_event = self.instructions[self.current_instruction]
            self.current_instruction += 1
            if self.waiting:
                self.waiting = False
            else:
                self.current_wait = wait
        else:
            self.current_event = None
            self.current_wait = 0.0
        return is_playing
    
    def get_event(self):
        return self.current_event
    
    def set_speed(self, speed):
        self.speed = speed
    
    async def wait(self):
        try:
            current_time = time.time()
            await asyncio.sleep(self.current_wait / self.speed)
        except:
            self.current_wait = (time.time() - current_time) * self.speed
            raise
