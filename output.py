import asyncio
from timeline import Timeline

class Output:
    def __init__(self):
        self.left_hand_hardware = None
        self.right_hand_hardware = None
        self.left_hand_midi = None
        self.right_hand_midi = None
        self.left_hand_task = None
        self.right_hand_task = None
        self.playing = False
        self.speed = 1.0
        self.time = 0.0

    def set_left_hand_hardware(self, hardware):
        self.left_hand_hardware = hardware
        if self.playing:
            self.play()

    def set_right_hand_hardware(self, hardware):
        self.right_hand_hardware = hardware
        if self.playing:
            self.play()

    def set_left_hand_midi(self, midi_file):
        self.left_hand_midi = Timeline(midi_file)
        self.left_hand_midi.seek(self.time)
        self.left_hand_midi.set_speed(self.speed)
        if self.playing:
            self.play()

    def set_right_hand_midi(self, midi_file):
        self.right_hand_midi = Timeline(midi_file)
        self.right_hand_midi.seek(self.time)
        self.right_hand_midi.set_speed(self.speed)
        if self.playing:
            self.play()
    
    def seek(self, time):
        self.time = time
        if self.left_hand_midi:
            self.left_hand_midi.seek(time)
        if self.right_hand_midi:
            self.right_hand_midi.seek(time)
        if self.playing:
            self.play()
    
    def set_speed(self, speed):
        self.speed = speed
        if self.left_hand_midi:
            self.left_hand_midi.set_speed(speed)
        if self.right_hand_midi:
            self.right_hand_midi.set_speed(speed)
        if self.playing:
            self.play()
    
    def play(self):
        if not self.left_hand_hardware or not self.left_hand_midi or not self.right_hand_hardware or not self.left_hand_midi:
            return False
        if self.left_hand_task:
            self.left_hand_task.cancel()
        self.left_hand_task = asyncio.create_task(self.left_hand_hardware.play(self.left_hand_midi))
        if self.right_hand_task:
            self.right_hand_task.cancel()
        self.right_hand_task = asyncio.create_task(self.right_hand_hardware.play(self.right_hand_midi))
        self.playing = True
        return True

    def stop(self):
        if not self.playing:
            return False
        self.left_hand_task.cancel()
        self.right_hand_task.cancel()
        self.playing = False
        return True