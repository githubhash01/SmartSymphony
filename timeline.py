from keys import Key, KeyEvent
import mido
import asyncio

class Timeline:
    def __init__(self, midi_file):
        self.speed = 1.0
        self.instructions = self.parseMidi(midi_file)
        self.current_instruction = 0
        self.current_event = None
        self.current_wait = 0.0

    def parseTrack(self, track):
        timeline = []
        current_time = 0

        for msg in track:
            current_time += msg.time
            if msg.type in ['note_on', 'note_off']:
                key = Key(msg.note)
                event_type = 1 if msg.type == 'note_on' and msg.velocity != 0 else 0
                event = KeyEvent(key, event_type)
                timeline.append((current_time, event))

        return timeline

    def parseMidi(self, midi_file):
        mid = mido.MidiFile(midi_file)
        combined_timeline = [event for track in mid.tracks for event in self.parseTrack(track) if track]
        combined_timeline.sort(key=lambda x: x[0])

        # add wait times to the timeline
        wait_times = []
        for i in range(len(combined_timeline) - 1):
            wait_time = combined_timeline[i + 1][0] - combined_timeline[i][0]
            wait_times.append(wait_time)
        wait_times.append(0)  # no wait time for the last event
        combined_timeline = [(wait, event) for (_, event), wait in zip(combined_timeline, wait_times)]
        return combined_timeline
    
    def seek(self, time):
        self.current_instruction = 0
        current_time = 0.0
        for wait, _ in self.instructions:
            next_time = current_time + wait
            if next_time > time:
                break
            self.current_instruction += 1
        self.current_wait = time - current_time
    
    def playing(self):
        is_playing = self.instructions and self.current_instruction < len(self.instructions)
        if is_playing:
            self.current_wait, self.current_event = self.instructions[self.current_instruction]
            self.current_instruction += 1
        else:
            self.instructions = None
            self.current_event = None
            self.current_Wait = 0.0
        return is_playing
    
    def get_event(self):
        return self.current_event
    
    def set_speed(self, speed):
        self.speed = speed
    
    async def wait(self):
        await asyncio.sleep(self.current_wait / self.speed)