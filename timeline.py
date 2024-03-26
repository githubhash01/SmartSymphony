from keys import Key, KeyEvent
import asyncio
import pretty_midi as pm
import time

class Timeline:
    def __init__(self, left_midi_file, right_midi_file):
        self.speed = 1.0
        self.instructions = self.get_instructions(left_midi_file, right_midi_file)
        self.current_instruction = 0
        self.current_events = None
        self.current_wait = 0.0
        self.waiting = False
    
    def get_instructions(self, left_midi_file, right_midi_file):
        instructions = []
        left_midi_data = pm.PrettyMIDI(left_midi_file)
        for instrument in left_midi_data.instruments:
            for note in instrument.notes:
                instructions.append((note.start, "left", KeyEvent(Key(note.pitch), 1)))
                instructions.append((note.end, "left", KeyEvent(Key(note.pitch), 0)))
        right_midi_data = pm.PrettyMIDI(right_midi_file)
        for instrument in right_midi_data.instruments:
            for note in instrument.notes:
                instructions.append((note.start, "right", KeyEvent(Key(note.pitch), 1)))
                instructions.append((note.end, "right", KeyEvent(Key(note.pitch), 0)))
        instructions.sort(key=lambda x: x[0])
        wait_times = []
        for i in range(len(instructions) - 1):
            wait_time = instructions[i + 1][0] - instructions[i][0]
            wait_times.append(wait_time)
        wait_times.append(0.0)
        instructions = [(time, wait, hand, event) for (time, hand, event), wait in zip(instructions, wait_times)]
        instructions_by_time = {}
        for time, wait, hand, event in instructions:
            if time not in instructions_by_time: 
                instructions_by_time[time] = [time, 0.0, {"left" : [], "right" : []}]
            if wait > instructions_by_time[time][1]:
                instructions_by_time[time][1] = wait
            instructions_by_time[time][2][hand].append(event)
        instructions = {k: instructions_by_time[k] for k in sorted(instructions_by_time)}
        return instructions
    
    def seek(self, time):
        self.current_instruction = 0
        next_event_time = float("inf")
        for event_time, _, _, _ in self.instructions:
            if event_time >= time:
                next_event_time  = event_time
                break
            self.current_instruction += 1
        self.current_wait = next_event_time - time
        self.waiting = True
    
    def set_speed(self, speed):
        self.speed = speed
    
    def playing(self):
        is_playing = self.instructions and self.current_instruction < len(self.instructions)
        if is_playing:
            self.time, wait, self.current_events = self.instructions[self.current_instruction]
            self.current_instruction += 1
            if not self.waiting:
                self.current_wait = wait
        else:
            self.current_event = None
            self.current_wait = 0.0
        return is_playing
    
    def get_events(self):
        return self.current_events
        
    async def wait(self):
        self.waiting = False
        try:
            current_time = time.time()
            await asyncio.sleep(self.current_wait / self.speed)
        except:
            self.current_wait = (time.time() - current_time) * self.speed
            raise
