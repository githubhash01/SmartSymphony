import threading
import time

from MidiProcessor import parseMidi

class Controller:
    
    def __init__(self, LED, midi_file):
        self.LED = LED
        self.timeline = parseMidi(midi_file, [0]) # 0 for just right hand
        #self.timeline = parseMidi(midi_file) 
        self.led_key = None 
        self.detected_key = None
        #second_octave = {'C2', 'C#2', 'D2', 'D#2', 'E2', 'F2', 'F#2', 'G2', 'G#2', 'A2', 'A#2', 'B2'}
        #part_three = {'C3', 'C#3', 'D3', 'D#3', 'E3', 'F3', 'F#3', 'G3', 'G#3'}
        #self.no_play = second_octave
        #self.time 
        
    
    def updateDetectedKey(self, key):
        self.detected_key = key
        time.sleep(0.3) 
        
    def run(self):
        # each time has a list of events 
        events_by_time = {}
        
        for event_time, wait, event in self.timeline:
            if event.event_type == 1:
                if event_time not in events_by_time: 
                    events_by_time[event_time] = [event]
                else:
                    events_by_time[event_time].append(event) 
        events_by_time = {k: events_by_time[k] for k in sorted(events_by_time)} 
        for t in events_by_time:
            event_list = events_by_time[t] 
            for event in event_list:
                self.LED.updateKeyColor(key=event.key, key_status=event.event_type)
            self.LED.show()
            time.sleep(1)
            current_set = set([event.key.note for event in event_list])
            while True:
                """
                if self.detected_key in current_set:
                    current_set.remove(self.detected_key)
                    if len(current_set) == 0:
                        break 
            
            """
                if self.detected_key in current_set:
                    break 
            for event in event_list:
                self.LED.updateKeyColor(key=event.key, key_status=0)
            self.LED.show()
            #time.sleep(0.1)
                
            #time.sleep(0.001 * wait / (speed)) 
        self.LED.turnOffStrip()
        
        """
        events = [] 
        for time, wait, event in self.timeline:
            #if time == self.time:
                #events
            if event.event_type and (event.key.note not in self.no_play):
                self.led_key = event.key
                self.LED.updateKeyColor(self.led_key, 1) 
                while True:
                    if self.detected_key == self.led_key.note:
                        break
                self.LED.updateKeyColor(self.led_key, 0)
        print("Congratulations - you finished the piece!") 
        self.LED.turnOff()
        """
                
            
            
            
            
        