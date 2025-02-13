import pyaudio
from numpy import zeros, linspace, short, fromstring, hstack, transpose, log, log2, abs, mean
from scipy.fft import fft
import numpy as np
#import threading
import queue
from collections import deque
import time
import math
import asyncio


class Values():
    SENSITIVITY =  50#5(individual works good) #50(this worked)
    TONE = 300  # Bandwidth to eliminate noise
    BANDWIDTH = 30
    RELATIVE_FREQ = 440.0
    NUM_SAMPLES =  4096 #8192(this worked)
    SAMPLING_RATE = 44100 #44100
    PRECISION = 0.8
    Frequency_Difference_Threshold = 100

class Tuner():
    def __init__(self,SAMPLES_FOR_AVERAGE,RIGHT_MIN_FREQUENCY,RIGHT_MIN_INTENSITY,LEFT_MAX_INTENSITY,LEFT_MIN_INTENSITY,LEFT_MIN_FREQUENCY,LEFT_MAX_FREQUENCY,WAIT_CYCLE_TIME):
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=Values.SAMPLING_RATE,
            input=True,
            frames_per_buffer=Values.NUM_SAMPLES,
            input_device_index= 0 # Change this to the index of your input device if necessary
        )
        self.buffer = queue.Queue()
        self.running = False
        #self.results = deque()
        self.results = []
        self.mapped_results = {}
        self.SAMPLES_FOR_AVERAGE = SAMPLES_FOR_AVERAGE #5(this worked)  # Number of samples to average
        self.RIGHT_MIN_FREQUENCY = RIGHT_MIN_FREQUENCY
        self.RIGHT_MIN_INTENSITY = RIGHT_MIN_INTENSITY
        self.LEFT_MAX_INTENSITY = LEFT_MAX_INTENSITY #30(worked)
        self.LEFT_MIN_INTENSITY = LEFT_MIN_INTENSITY
        self.LEFT_MIN_FREQUENCY = LEFT_MIN_FREQUENCY
        self.LEFT_MAX_FREQUENCY = LEFT_MAX_FREQUENCY
        self.WAIT_CYCLE_TIME = WAIT_CYCLE_TIME
        self.awaiting = False
        self.detected_note = None
        self.stale = False
        self.notes = set()

    def get_frequency_from_samples_right(self,audio_samples):
        frequencies = []
        intensities = []
        for audio_data in audio_samples:
            normalized_data = audio_data / 32768.0  # Normalize audio data
            intensity = abs(fft(normalized_data))[:Values.NUM_SAMPLES // 2]
            frequencies_sample = linspace(0.0, float(Values.SAMPLING_RATE) // 2, num=Values.NUM_SAMPLES // 2)
            max_intensity_index = intensity[1:].argmax() + 1
            if max_intensity_index != len(intensity) - 1:
                y0, y1, y2 = log(intensity[max_intensity_index - 1:max_intensity_index + 2:])
                x1 = (y2 - y0) * 0.5 / (2 * y1 - y2 - y0)
                thefreq = (max_intensity_index + x1) * Values.SAMPLING_RATE / Values.NUM_SAMPLES
            else:
                thefreq = max_intensity_index * Values.SAMPLING_RATE / Values.NUM_SAMPLES

            theintensity = intensity[max_intensity_index]
            if theintensity >= self.RIGHT_MIN_INTENSITY:
                frequencies.append(thefreq)
                intensities.append(theintensity)

    # Zip and filter the results
        zipped = list(zip(frequencies, intensities))
        zipped = [(a, b) for a, b in zipped if b >= self.RIGHT_MIN_INTENSITY and a >= self.RIGHT_MIN_FREQUENCY]
        if len(zipped) == 0:
            return []

    # Sort by frequency
        zipped.sort(key=lambda x: x[0])

    # Group frequencies based on a threshold gap
        groups = []
        current_group = [zipped[0]]
        for i in range(1, len(zipped)):
            if (zipped[i][0] > 1150):
                continue
            elif (zipped[i][1] - zipped[i-1][1] > 0):  # Threshold for a new group
                groups.append(current_group)
                current_group = [zipped[i]]
            else:
                if (zipped[i][0] - zipped[i-1][0] > Values.Frequency_Difference_Threshold):
                   continue
                current_group.append(zipped[i])
        groups.append(current_group)  # Add the last group

    # Calculate average frequency and intensity for each group
        averages = []
        for group in groups:
            avg_freq = np.mean([f for f, _ in group])
            avg_intensity = np.mean([i for _, i in group])
            averages.append((avg_freq, avg_intensity))

        return averages

    def get_frequency_from_samples_left(self,audio_samples):
        frequencies = []
        intensities = []
        for audio_data in audio_samples:
            normalized_data = audio_data / 32768.0  # Normalize audio data
            intensity = abs(fft(normalized_data))[:Values.NUM_SAMPLES // 2]
            frequencies_sample = linspace(0.0, float(Values.SAMPLING_RATE) // 2, num=Values.NUM_SAMPLES // 2)
            max_intensity_index = intensity[1:].argmax() + 1
            if max_intensity_index != len(intensity) - 1:
                y0, y1, y2 = log(intensity[max_intensity_index - 1:max_intensity_index + 2:])
                x1 = (y2 - y0) * 0.5 / (2 * y1 - y2 - y0)
                thefreq = (max_intensity_index + x1) * Values.SAMPLING_RATE / Values.NUM_SAMPLES
            else:
                thefreq = max_intensity_index * Values.SAMPLING_RATE / Values.NUM_SAMPLES

            theintensity = intensity[max_intensity_index]
            if theintensity <= self.LEFT_MAX_INTENSITY and self.LEFT_MIN_INTENSITY <= theintensity:
                frequencies.append(thefreq)
                intensities.append(theintensity)

    # Zip and filter the results
        zipped = list(zip(frequencies, intensities))
        zipped = [(a, b) for a, b in zipped if b <= self.LEFT_MAX_INTENSITY and self.LEFT_MIN_INTENSITY <= b and self.LEFT_MAX_FREQUENCY >= a and self.LEFT_MIN_FREQUENCY <= a]
        if len(zipped) == 0:
            return []

    # Sort by frequency
        zipped.sort(key=lambda x: x[0])

    # Group frequencies based on a threshold gap
        groups = []
        current_group = None
        for i in range(0,len(zipped)):
            if current_group == None:
                if zipped[i][0] > self.LEFT_MAX_FREQUENCY:
                    continue
                else:
                    current_group = [zipped[i]]
            elif (zipped[i][0] > self.LEFT_MAX_FREQUENCY):
                continue
            elif (zipped[i][1] - zipped[i-1][1] > 0):  # Threshold for a new group
                groups.append(current_group)
                current_group = [zipped[i]]
            else:
                if (zipped[i][0] - zipped[i-1][0] > Values.Frequency_Difference_Threshold):
                   continue
                current_group.append(zipped[i])
        if current_group == None and len(groups) == 0:
            return None
        groups.append(current_group)  # Add the last group

    # Calculate average frequency and intensity for each group
        averages = []
        #print("group",groups)
        for group in groups:
            avg_freq = np.mean([f for f, _ in group])
            avg_intensity = np.mean([i for _, i in group])
            averages.append((avg_freq, avg_intensity))

        return averages

    def collect_samples(self):
        audio_data = fromstring(self.stream.read(Values.NUM_SAMPLES,exception_on_overflow=False), dtype=short)
        self.buffer.put(audio_data)
        
    async def set_awaiting(self, notes):
        self.awaiting = True
        while True:
            if len(self.notes) != 0 and self.notes.issubset(notes):
                break
            await asyncio.sleep(0)
        self.awaiting = False
    
    def is_awaiting(self):
        return self.awaiting

    def process_samples(self):
        audio_samples = []
        count = 0
        temp = []
        right = False
        started = False
        prev_note = None
        time_played = None
        #while self.running or not self.buffer.empty():
        if self.buffer.empty():
            self.collect_samples()
            self.notes = set()
        if not self.buffer.empty():
            audio_samples.append(self.buffer.get_nowait())
            if len(audio_samples) == self.SAMPLES_FOR_AVERAGE:
                if started:
                    count += 1
                vals_right = self.get_frequency_from_samples_right(audio_samples)
                vals_left = self.get_frequency_from_samples_left(audio_samples)
                audio_samples = []
                vals = None
                side = None
                if len(vals_left) != 0:
                    vals = vals_left
                    side = "left"
                    right = False
                else:
                    vals = vals_right
                    side = "right"
                    right = True
                if(vals != None and len(vals) != 0):
                    for val in vals:
                        detected_note = frequency_to_note(val[0])
                        if(right == True) and (count <= self.WAIT_CYCLE_TIME):
                                temp.append((detected_note,val[1]))
                                #print(detected_note)
                                #print("time",time.time())
                                #print("frequency",val[0])
                                #print("intensity",val[1])
                                started = True
                                prev_note = detected_note
                                time_played = time.time()
                        elif(right == False):
                                #if prev_note != note or (prev_note == note and time.time()-time_played > 1):
                                    self.results.append(detected_note)
                                    #self.detected_key = note
                                    self.stale= True
                                    self.detected_note = detected_note 
                                    prev_note = detected_note
                                    time_played = time.time()
                                    self.notes = set()
                                    self.notes.add(detected_note)
                                
                if count >=self.WAIT_CYCLE_TIME and len(temp) != 0:
                    for note,t in temp:
#                           # print("note detected "+note+" by right" )
#                           #print(t)
                        #if prev_note != note or (prev_note == note and time.time()-time_played > 1):
                        self.results.append(note)
                            #self.detected_key = note
                        self.stale= True
                        self.detected_note = note 
                        prev_note = note
                        time_played = time.time()
                        self.notes = set()
                        self.notes.add(note)
                            
                    temp = []
                    count = 0
                    started = False
                    self.buffer.task_done()


    def clear(self):
        self.results = deque()
        
    def stop(self):
        if self.running:
            self.stream.stop_stream()
            self.running = False

    def get_notes(self):
        if self.notes == None:
            return set()
        return self.notes
    
    def start(self):
        if not self.running:
            self.stream.start_stream()
            self.running = True
# frequency_to_note function and NotesHz class remain unchanged
def frequency_to_note(frequency):
    notes = {
        65.406: "C2", 69.30: "C#2",
        73.42: "D2",
        77.78: "D#2",
        82.41: "E2", 87.31: "F2",
        92.50: "F#2",
        98.00: "G2",
        103.83: "G#2",
        110.00: "A2",
        116.54: "A#2",
        123.47: "B2",
        130.81: "C3",
        138.59: "C#3",
        146.83: "D3", 155.56: "D#3",
        164.81: "E3", 174.61: "F3",
        185.00: "F#3",
        196.00: "G3",
        207.65: "G#3",
        220.00: "A3",
        233.08: "A#3",
        246.94: "B3",
        261.63: "C4",
        277.18: "C#4",
        293.66: "D4",
        311.13: "D#4",
        329.63: "E4", 349.23: "F4",
        369.99: "F#4",
        392.00: "G4",
        415.30: "G#4",
        440.00: "A4",
        466.16: "A#4",
        493.88: "B4",
        523.25: "C5",
        554.37: "C#5",
        587.33: "D5",
        622.25: "D#5",
        659.25: "E5",
        698.46: "F5",
        739.99: "F#5",
        783.99: "G5",
        831.61: "G#5",
        880.00: "A5",
        932.33: "A#5",
        987.77: "B5",
        1046.50: "C6"

    }
    closest_note = min(notes.keys(), key=lambda x: abs(x - frequency))

    return(notes[closest_note])

"""Mic = Tuner(1,115,75,30,10,40,120,0)
while True:
    Mic.process_samples()
    if len(Mic.get_notes()) != 0:
        print("THese are the detected notes",Mic.get_notes())
        """



