import asyncio
from timeline import Timeline

class Controller:
    def __init__(self, microphone):
        self.microphone = microphone
        self.hardware = {"left" : None, "right" : None}
        self.feedback = {"left" : False, "right" : False}
        self.timeline = None
        self.playing_task = None
        self.speed = 1.0
        self.time = 0.0

    def set_hardware(self, hand, hardware):
        self.hardware[hand] = hardware
    
    def set_feedback(self, hand, feedback):
        self.feedback[hand] = feedback

    def set_midi(self, midi_file):
        self.timeline = Timeline(midi_file)
        self.timeline.seek(self.time)
        self.timeline.set_speed(self.speed)
    
    def seek(self, time):
        self.time = time
        if self.timeline:
            self.timeline.seek(time)
    
    def set_speed(self, speed):
        self.speed = speed
        if self.timeline:
            self.timeline.set_speed(speed)
    
    async def internal_play(self):
        try:
            await self.timeline.wait()
            while self.timeline.playing():
                events = self.timeline.get_events()
                for hand in events:
                    if not self.hardware[hand]:
                        continue
                    for event in events[hand]:
                        if event.event_type == 1:
                            self.hardware[hand].start_note(event.key, hand)
                        elif event.event_type == 0:
                            self.hardware[hand].stop_note(event.key, hand)
                notes = set()
                for hand in events:
                    if not self.hardware[hand]:
                        continue
                    if self.feedback[hand]:
                        for event in events[hand]:
                            if event.event_type == 1:
                                notes.add(event.key.note)
                if len(notes) > 0:
                    await self.microphone.set_awaiting(notes)
                await self.timeline.wait()
        except Exception as e:
            print(e)
    
    def play(self):
        if self.playing_task:
            return False
        if not self.hardware["left"] and not self.hardware["right"]:
            return False
        self.playing_task = asyncio.create_task(self.internal_play())
        return True
    
    def internal_stop(self):
        if not self.playing_task:
            return False
        self.playing_task.cancel()
        self.playing_task = None
        return True

    def stop(self):
        left_hardware = self.hardware["left"]
        if left_hardware:
            left_hardware.stop()
        right_hardware = self.hardware["left"]
        if right_hardware and right_hardware != left_hardware:
            right_hardware.stop()
        return self.internal_stop()
    
    def pause(self):
        left_hardware = self.hardware["left"]
        if left_hardware:
            left_hardware.pause()
        right_hardware = self.hardware["left"]
        if right_hardware and right_hardware != left_hardware:
            right_hardware.pause()
        return self.internal_stop()