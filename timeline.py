from keys import Key, KeyEvent
import mido
import asyncio
import pretty_midi as pm
import time

class Timeline:
    def __init__(self, midi_file):
        self.speed = 1.0
        instructions = []
        midi_data = pm.PrettyMIDI(midi_file)
        for instrument in midi_data.instruments:
            for note in instrument.notes:
                instructions.append((note.start, KeyEvent(Key(note.pitch), 1)))
                instructions.append((note.end, KeyEvent(Key(note.pitch), 0)))
        instructions.sort(key=lambda x: x[0])
        wait_times = []
        for i in range(len(instructions) - 1):
            wait_time = instructions[i + 1][0] - instructions[i][0]
            wait_times.append(wait_time)
        wait_times.append(0.0)
        instructions = [(time, wait, event) for (time, event), wait in zip(instructions, wait_times)]
        instructions_by_time = {}
        for event_time, wait, event in instructions:
            if event_time not in instructions_by_time: 
                instructions_by_time[event_time] = [wait, [event], event_time]
            else:
                instructions_by_time[event_time][1].append(event)
                if wait > instructions_by_time[event_time][0]:
                    instructions_by_time[event_time][0] = wait
        instructions_by_time = {k: instructions_by_time[k] for k in sorted(instructions_by_time)}
        self.instructions = [instructions_by_time[key] for key in instructions_by_time]
        self.current_instruction = 0
        self.current_events = None
        self.current_wait = 0.0
        self.waiting = False
        self.wait_time = 0.0
        self.other_awaiting = False
    
    def seek(self, time):
        self.current_instruction = 0
        next_event_time = float("inf")
        for _, _, event_time in self.instructions:
            if event_time >= time:
                next_event_time  = event_time
                break
            self.current_instruction += 1
        self.current_wait = next_event_time - time
        print(self.current_wait)
        self.waiting = True
    
    def playing(self):
        is_playing = self.instructions and self.current_instruction < len(self.instructions)
        if is_playing:
            instruction = self.instructions[self.current_instruction]
            wait = instruction[0]
            self.current_events = instruction[1]
            self.time = instruction[2]
            self.current_instruction += 1
            if not self.waiting:
                self.current_wait = wait
        else:
            self.current_event = None
            self.current_wait = 0.0
        return is_playing
    
    def get_events(self):
        return self.current_events
    
    def set_speed(self, speed):
        self.speed = speed
        
    async def wait(self):
        self.waiting = False
        try:
            current_time = time.time()
            await asyncio.sleep(self.current_wait / self.speed)
        except:
            if not self.other_awaiting:
                self.current_wait = (time.time() - current_time) * self.speed
            raise
