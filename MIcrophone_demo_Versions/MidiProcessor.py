import threading
import time
from rightHalf import Tuner as RightHalfTuner
from leftHalf import Tuner as LeftHalfTuner
import mido
from collections import deque 
MIDI_FILE = 'HappyBirthday.mid'
results = deque()
notes = ["C6","C2","B5"]
ptr = 0

class CentralMicrophone:
    def __init__(self):
        self.right_half_tuner = RightHalfTuner()
        self.left_half_tuner = LeftHalfTuner()
        self.running = True

    def start_tuners(self):
        # Start lower frequencies tuner in a separate thread
        self.right_half_thread = threading.Thread(target=self.right_half_tuner.start)
        self.right_half_thread.start()

        # Start left half tuner in a separate thread
        self.left_half_thread = threading.Thread(target=self.left_half_tuner.start)
        self.left_half_thread.start()

    def stop_tuners(self):
        self.right_half_tuner.stop()
        self.left_half_tuner.stop()
        self.running = False

    def run(self):
        global ptr
        #global notes
        global results
        print(results[0])
        try:
            self.start_tuners()
            while self.running:
                # Process detected notes from left half tuner
                note_left_half = None
                note_right_half = None
                if not self.left_half_tuner.results.empty():
                    #tup = self.left_half_tuner.results.get()
                    #note = tup[0]
                    note_left_half = self.left_half_tuner.results.get()
                    count = 0
                    """while not self.left_half_tuner.results.empty():
                        temp = self.left_half_tuner.results.queue[0]
                        if temp == note_left_half:
                            count += 1
                            self.left_half_tuner.results.get()
                        else:
                            break
                    pressType = None
                    if count <=3:
                        pressType = "short press"
                    else:
                        pressType = "Long or consecutive press"
                    """
                    print(f"Left Half Tuner Detected Note: {note_left_half}")
                    results.append(note_left_half)
                    
                        
                    #self.right_half_tuner.results.get()
                    
                # Process detected notes from lower frequencies tuner
                if not self.right_half_tuner.results.empty():
                    #tup = self.left_half_tuner.results.get()
                    #note = tup[0]                   
                    note_right_half = self.right_half_tuner.results.get()
                    count = 0
                    """while not self.right_half_tuner.results.empty():
                        temp = self.right_half_tuner.results.queue[0]
                        if temp == note_right_half:
                            count += 1
                            self.right_half_tuner.results.get()
                        else:
                            break
                    pressType = None
                    if count <=3:
                        pressType = "short press"
                    else:
                        pressType = "Long or consecutive press"
                        """
                    print(f"Right Half Tuner Detected Note: {note_right_half}")
                    results.append(note_right_half)
                """    
                if note_right_half == notes[ptr] or note_left_half == notes[ptr]:                   
                    print("key detected")
                    print("-------------------")
                    ptr += 1
                    if ptr == len(notes):
                       print("Stopping tuners...")
                       self.stop_tuners()
                       print("Tuners stopped.")
                """
                if len(results) != 0:
                    if note_right_half == results[0] or note_left_half == results[0]:
                        print("----------------------")
                        print("key detected")
                        print("----------------------")
                        results.popleft()
                        time.sleep(1)
                if len(results) == 0:
                    print("Stopping tuners...")
                    self.stop_tuners()
                    print("Tuners stopped.")
                

        except KeyboardInterrupt:
            print("Stopping tuners...")
            self.stop_tuners()
            print("Tuners stopped.")






"""
A python script that takes a midi file and converts it to a timeline of notes being played
"""

class Key:
    def __init__(self, key_num):
        self.original_key_num = key_num
        self.key_num = self.translate_to_61keys(key_num) - 12 
        self.note = self.get_note()

    def get_note(self):
        note = self.key_num % 12
        octave = self.key_num // 12
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return notes[note] + str(octave)
    
    def translate_to_61keys(self, key_num):
        key = key_num
        while key > 96:
            key -= 12
        while key < 36:
            key += 12
        return key 
    
class KeyEvent: 

    def __init__(self, key, event_type):
        self.key = key
        self.event_type = event_type

def parseTrack(track):
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


def parseMidi(midi_file):
    mid = mido.MidiFile(midi_file)
    combined_timeline = [event for track in mid.tracks for event in parseTrack(track) if track]
    combined_timeline.sort(key=lambda x: x[0])

    # add wait times to the timeline
    wait_times = []
    for i in range(len(combined_timeline) - 1):
        wait_time = combined_timeline[i + 1][0] - combined_timeline[i][0]
        wait_times.append(wait_time)
    wait_times.append(0)  # no wait time for the last event
    combined_timeline = [(time, wait, event) for (time, event), wait in zip(combined_timeline, wait_times)]
    return combined_timeline    



def main():
    global results
    timeline = parseMidi(MIDI_FILE)
    for time, wait, event in timeline:
        if event.event_type == 1:
            results.append(event.key.note)
            print(event.key.note)
    """
    #notes = ["C6"]
    print("hiiiii")
    for x in notes:
        detected = False
        while True:
            print(results.qsize())
            while not results.empty():
                temp = results.get()
                print("----------------")
                print("comparing")
                print(x,temp)
                print("----------------")
                if x == temp:
                    detected = True
                    break
            if detected:
                break
                print("detected")
                #while True:
            #while not results.empty():
                #if event.key.note == results.get():
                    #break
    ##for time, wait, event in timeline:
        #pass
        #print(time, wait, event.key.note, event.key.key_num, event.event_type)
        #keyPressed = False
        #print(event.key.note)
        #while True:
            #while not results.empty():
                #if event.key.note == results.get():
                    #break
            #break
    """
if __name__ == '__main__':
    main()
    central_microphone = CentralMicrophone()
    central_microphone.run()
    
    




