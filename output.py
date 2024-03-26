import asyncio
from timeline import Timeline

class Output:
    def __init__(self, microphone):
        self.left_hand_hardware = None
        self.right_hand_hardware = None
        self.left_hand_midi = None
        self.right_hand_midi = None
        self.left_hand_output = None
        self.right_hand_output = None
        self.left_hand_task = None
        self.right_hand_task = None
        self.microphone = microphone
        self.playing = False
        self.speed = 1.0
        self.time = 0.0

    def set_hardware(self, hand, hardware):
        if hand == "left":
            self.left_hand_hardware = hardware
        elif hand == "right":
            self.right_hand_hardware = hardware
        if self.playing:
            self.internal_play()

    def set_midi(self, hand, midi_file):
        timeline = Timeline(midi_file)
        timeline.seek(self.time)
        timeline.set_speed(self.speed)
        if hand == "left":
            self.left_hand_midi = timeline
        elif hand == "right":
            self.right_hand_midi = timeline
        if self.playing:
            self.internal_play()
    
    def set_feedback(self, hand, feedback):
        if hand == "left":
            self.left_hand_output = self if feedback else None
        elif hand == "right":
            self.right_hand_output = self if feedback else None
    
    async def set_awaiting(self, hand, notes):
        if hand == "left":
            if self.right_hand_task:
                self.right_hand_task.cancel()
                self.right_hand_task = None
                print("TEST", self.left_hand_midi.time)
                self.right_hand_midi.other_awaiting = True
                self.right_hand_midi.current_wait = self.right_hand_midi.instructions[self.right_hand_midi.current_instruction][2] - self.left_hand_midi.time
                print(self.right_hand_midi.current_wait)
            await self.microphone.set_awaiting(notes)
            self.right_hand_midi.other_awaiting = False
        elif hand == "right":
            if self.left_hand_task:
                self.left_hand_task.cancel()
                self.left_hand_task = None
            await self.microphone.set_awaiting(notes)
        self.internal_play()
    
    def seek(self, time):
        self.time = time
        if self.left_hand_midi:
            self.left_hand_midi.seek(time)
        if self.right_hand_midi:
            self.right_hand_midi.seek(time)
        if self.playing:
            self.internal_play()
    
    def set_speed(self, speed):
        self.speed = speed
        if self.left_hand_midi:
            self.left_hand_midi.set_speed(speed)
        if self.right_hand_midi:
            self.right_hand_midi.set_speed(speed)
        if self.playing:
            self.internal_play()
    
    def turn_off(self):
        if self.left_hand_hardware:
            self.right_hand_hardware.turnOff()
        if self.left_hand_hardware:
            self.right_hand_hardware.turnOff()
    
    def internal_play(self):
        left_active = self.left_hand_hardware and self.left_hand_midi
        right_active = self.right_hand_hardware and self.right_hand_midi
        if not left_active and not right_active:
            return False
        if left_active and not self.left_hand_task:
            self.left_hand_task = asyncio.create_task(self.left_hand_hardware.play(self.left_hand_midi, "left", self.left_hand_output))
        if right_active and not self.right_hand_task:
            self.right_hand_task = asyncio.create_task(self.right_hand_hardware.play(self.right_hand_midi, "right", self.right_hand_output))
        self.playing = True
        return True
    
    def play(self):
        self.turn_off()
        if self.left_hand_task:
            self.left_hand_task.cancel()
            self.left_hand_task = None
        if self.right_hand_task:
            self.right_hand_task.cancel()
            self.right_hand_task = None
        return self.internal_play()
    
    def internal_stop(self):
        if not self.playing:
            return False
        if self.left_hand_task:
            self.left_hand_task.cancel()
            self.left_hand_task = None
        if self.right_hand_task:
            self.right_hand_task.cancel()
            self.right_hand_task = None
        self.playing = False
        return True

    def stop(self):
        self.turn_off()
        return self.internal_stop()