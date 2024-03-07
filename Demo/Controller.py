import threading
import time 

class Controller:
    
    def __init__(self, LED, Microphone):
        self.sequence = [31,32,33, 35,36,37, 39,40,41] 
        self.dict = {31:"C5",
                         32:"C#5",
                         33:"D5",
                         34: "D#5",
                         35:"F5",
                         36:"F#5",
                         37:"G5",
                         38:"G#5",
                         39:"A#5",
                         40:"B5",
                         41:"C6"}
        self.index = -1
        self.LED = LED
        self.MIC = Microphone
        
        # thread for the strip functions to be called
        self.led_thread = threading.Thread(target=self.LED.begin)
        # one thread for the microphone to run in the background
        self.mic_thread = threading.Thread(target=self.MIC.run)
        
    
    def testLED(self):
        self.LED.colorWipe()
        time.sleep(2)
        self.LED.turnOff()
        
    def nextLED(self):
        self.index += 1
        self.LED.turnOff()
        note = self.sequence[self.index]
        print(note)
        self.LED.playNote(note)
    
    def end():
        self.LED.turnOff()
        self.MIC.stop_tuners()
        print('end')
        
    def run(self):
        self.led_thread.start()
        self.mic_thread.start()
        
        self.nextLED()
        
        while True:
            note = self.MIC.get_note()
            #print(note) 
            if note!= None and note!='end':
                print(note)
                print(expected)
                if note == self.dict[self.sequence[self.index]]: 
                    if self.index == len(self.sequence):
                        self.end()
                    else: 
                        self.nextLED()

    """
    def key_played(note):
        # turn the LED for that note off 
        self.LED.turnOffNote(note)
    """
    
        

