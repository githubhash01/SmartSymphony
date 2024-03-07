import threading
import time
from rightMicrophoneWithSingleReading import Tuner as RightHalfTuner
from leftMicrophoneWithSingleReading import Tuner as LeftHalfTuner

class Microphone:
    """
    def __init__(self, controller):
        self.right_half_tuner = RightHalfTuner()
        #self.left_half_tuner = LeftHalfTuner()
        self.running = True
        self.controller = controller
    """

    def __init__(self):
        self.right_half_tuner = RightHalfTuner()
        self.left_half_tuner = LeftHalfTuner()
        self.running = True
        self.note = None

        
    def start_tuners(self):
        # Start lower frequencies tuner in a separate thread
        self.right_half_thread = threading.Thread(target=self.right_half_tuner.start)
        self.left_half_thread = threading.Thread(target=self.left_half_tuner.start)
        self.left_half_thread.start()
        self.right_half_thread.start()

        # Start left half tuner in a separate thread

    def stop_tuners(self):
        self.right_half_tuner.stop()
        self.left_half_tuner.stop()
        self.running = False
        
    def get_note(self):
        return self.note
        
    def run(self):
        try:
            self.start_tuners()
            while self.running:

                
                if len(self.right_half_tuner.results) != 0:             
                    note = self.right_half_tuner.results.popleft()
                    self.note = note
                    # time.sleep(2) 
                    
                if len(self.left_half_tuner.results) != 0:
                    note = self.left_half_tuner.results.popleft()
                    if len(self.right_half_tuner.results) == 0:
                        while len(self.left_half_tuner.results) != 0 and self.left_half_tuner.results[0] != "end":
                            self.left_half_tuner.results.popleft()
                    
                    while len(self.right_half_tuner.results) != 0 and self.right_half_tuner.results[0] != "end":                        
                        self.right_half_tuner.results.popleft()
                if self.note != None and self.note != "end":
                    self.note = note
                    print("note detected", self.note)
                
    

        except KeyboardInterrupt:
            print("Stopping tuners...")
            self.stop_tuners()
            print("Tuners stopped.")

if __name__ == "__main__":
    mic = Microphone()
    try:
        mic.run()
    except KeyboardInterrupt:
        mic.stop_tuners()
        print("Program stopped.")


