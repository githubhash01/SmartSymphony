import threading
import time
from rightHalf import Tuner as RightHalfTuner
from leftHalf import Tuner as LeftHalfTuner

class Microphone:
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
        try:
            self.start_tuners()
            while self.running:
                # Process detected notes from left half tuner
                if not self.left_half_tuner.results.empty():
                    #tup = self.left_half_tuner.results.get()
                    #note = tup[0]
                    note = self.left_half_tuner.results.get()
                    count = 0
                    while not self.left_half_tuner.results.empty():
                        temp = self.left_half_tuner.results.queue[0][0]
                        if temp == note:
                            count += 1
                            self.left_half_tuner.results.get()
                        else:
                            break
                    pressType = None
                    if count <=3:
                        pressType = "short press"
                    else:
                        pressType = "Long or consecutive press"
                    print(f"Left Half Tuner Detected Note: {pressType} {note}")
                    continue
                        
                    #self.right_half_tuner.results.get()
                    
                # Process detected notes from lower frequencies tuner
                if not self.right_half_tuner.results.empty():
                    #tup = self.left_half_tuner.results.get()
                    #note = tup[0]                   
                    note = self.right_half_tuner.results.get()
                    count = 0
                    while not self.right_half_tuner.results.empty():
                        temp = self.right_half_tuner.results.queue[0][0]
                        if temp == note:
                            count += 1
                            self.right_half_tuner.results.get()
                        else:
                            break
                    pressType = None
                    if count <=3:
                        pressType = "short press"
                    else:
                        pressType = "Long or consecutive press"
                    print(f"Right Half Tuner Detected Note: {pressType} {note}")

        except KeyboardInterrupt:
            print("Stopping tuners...")
            self.stop_tuners()
            print("Tuners stopped.")


