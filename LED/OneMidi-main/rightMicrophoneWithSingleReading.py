import pyaudio
from numpy import zeros, linspace, short, fromstring, hstack, transpose, log, log2, abs, mean
from scipy.fft import fft
import numpy as np
import threading
import queue
import time
from collections import deque

class Values():
    SENSITIVITY =  50 #50(this worked)
    TONE = 300  # Bandwidth to eliminate noise
    BANDWIDTH = 30
    RELATIVE_FREQ = 440.0
    NUM_SAMPLES = 4096 #8192
    SAMPLING_RATE = 44100
    MIN_INTENSITY = 75 #100(this worked)
    PRECISION = 0.8
    SAMPLES_FOR_AVERAGE = 5 #5(this worked)  # Number of samples to average
    MIN_FREQUENCY = 115
class NotesHz():
    C2  = 65.406
    #Cs2 = 69.30
    #Db2 = 69.30
    D2  = 73.42
    #Ds2 = 77.78
    #Eb2 = 77.78
    E2  = 82.41
    F2  = 87.31
    #Fs2 = 92.50
    #Gb2 = 92.50
    G2  = 98.00
    #Gs2 = 103.83
    #Ab2 = 103.83
    A2  = 110.00
    #As2 = 116.54
    #Bb2 = 116.54
    B2  = 123.47
    C3  = 130.81
    #Cs3 = 138.59
    #Db3 = 138.59
    D3  = 146.83
    #Ds3 = 155.56
    #Eb3 = 155.56
    E3  = 164.81
    F3  = 174.61
    #Fs3 = 185.00
    #Gb3 = 185.00
    G3  = 196.00
    #Gs3 = 207.65
    #Ab3 = 207.65
    A3  = 220.00
    #As3 = 233.08
    #Bb3 = 233.08
    B3  = 246.94
    C4  = 261.63
    #Cs4 = 277.18
    #Db4 = 277.18
    D4  = 293.66
    #Ds4 = 311.13
    #Eb4 = 311.13
    E4  = 329.63
    F4  = 349.23
    #Fs4 = 369.99
    #Gb4 = 369.99
    G4  = 392.00
    #Gs4 = 415.30
    #Ab4 = 415.30
    A4  = 440.00
    #As4 = 466.16
    #Bb4 = 466.16
    B4  = 493.88
    C5  = 523.25
    #Cs5 = 554.37
    #Db5 = 554.37
    D5  = 587.33
    #Ds5 = 622.25
    #Eb5 = 622.25
    E5  = 659.25
    F5  = 698.46
    #Fs5 = 739.99
    #Gb5 = 739.99
    G5  = 783.99
    #Gs5 = 830.61
    #Ab5 = 830.61
    A5  = 880.00
    #As5 = 932.33
    #Bb5 = 932.33
    B5  = 987.77
    C6  = 1046.50

class Tuner():
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=Values.SAMPLING_RATE,
            input=True,
            frames_per_buffer=Values.NUM_SAMPLES,
            input_device_index= 1 # Change this to the index of your input device if necessary
        )
        self.buffer = queue.Queue()
        self.running = True
        #self.results = queue.Queue()
        self.results = deque()

    def get_frequency_from_samples(self,audio_samples):
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
            if theintensity >= Values.MIN_INTENSITY:
                frequencies.append(thefreq)
                intensities.append(theintensity)

    # Zip and filter the results
        zipped = list(zip(frequencies, intensities))
        zipped = [(a, b) for a, b in zipped if b >= Values.MIN_INTENSITY and a >= Values.MIN_FREQUENCY]
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
                if (zipped[i][0] - zipped[i-1][0] > 100):
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


    def collect_samples(self):
        while self.running:
            audio_data = fromstring(self.stream.read(Values.NUM_SAMPLES, exception_on_overflow=False), dtype=short)
            self.buffer.put(audio_data)

    def process_samples(self):
        audio_samples = []
        last_freq = None
        while self.running or not self.buffer.empty():
            if not self.buffer.empty():
                val = None
                try:
                    val = self.buffer.get_nowait()
                    audio_samples.append(val)
                except:
                    continue
                #audio_samples.append(self.buffer.get_nowait())
                #audio_samples.append(self.buffer.get())
                if len(audio_samples) == Values.SAMPLES_FOR_AVERAGE:
                    vals = self.get_frequency_from_samples(audio_samples)
                    audio_samples = []
                    temp = []
                    if len(vals) != 0:
                        #len("right microphone signal detected", time.time())
                        for val in vals:
                            if val[1] > Values.MIN_INTENSITY:
                                detected_note = frequency_to_note(val[0])
                                temp.append(detected_note)
                        for note in temp:
                            if len(self.results) == 0:
                                self.results.append(note)
                            else:
                                if self.results[-1] != note:
                                    self.results.append(note)
                        self.results.append("end")
                        self.buffer.task_done()

    def start(self):
        t_collect = threading.Thread(target=self.collect_samples)
        t_process = threading.Thread(target=self.process_samples)
        t_collect.start()
        t_process.start()
        t_collect.join()
        t_process.join()

    def stop(self):
        self.running = False
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

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

"""
if __name__ == "__main__":
    tuner = Tuner()
    try:
        tuner.start()
    except KeyboardInterrupt:
        tuner.stop()
        print("Program stopped.")
"""
