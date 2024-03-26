import threading
import time
from MidiProcessor import parseMidi
from Lightstrip import Strip
from l import Tuner

class Controller:
    
    def __init__(self, LED, Microphone, midi_file):
        self.LED = LED
        self.MIC = Microphone 
        self.timeline = parseMidi(midi_file, [0]) # for just right hand, otherwise leave it blank 
        self.detected_key = None
        
    def start(self):
        t_collect = threading.Thread(target=self.MIC.collect_samples)
        t_process = threading.Thread(target=self.MIC.process_samples)
        t_led = threading.Thread(target=self.run) 
        t_collect.start()
        t_process.start()
        t_led.start()
        t_collect.join()
        t_process.join()
        t_led.join()
        
    def stop(self):
        self.running = False
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()
        
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
                if (self.MIC.detected_note in current_set) and self.MIC.stale:
                    self.MIC.stale = False 
                    break 
            for event in event_list:
                self.LED.updateKeyColor(key=event.key, key_status=0)
            self.LED.show()
            #time.sleep(0.1)
                
            #time.sleep(0.001 * wait / (speed)) 
        self.LED.turnOffStrip()
        
def main():
    #Mic for game 1(SONATA SPARROW)
    MIDI_FILE = 'Danube.mid'
    LEDStrip = Strip()
    Mic = Tuner(1,115,75,30,10,40,120,0) 
    controller = Controller(LEDStrip, Mic, MIDI_FILE) 
    try:
        controller.start()
    except KeyboardInterrupt:
        controller.stop()
        print("Program stopped.")
    

main()

            
            
            
            
        