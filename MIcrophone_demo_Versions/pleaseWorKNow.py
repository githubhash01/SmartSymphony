
# adapted from https://github.com/katrinamo/RPiPitch/blob/master/freqDetect.py

import pyaudio
from numpy import zeros, linspace, short, fromstring, hstack, transpose, log, log2
from scipy.fft import fft
import time
import sys
import numpy as np

class Values():
    SENSITIVITY = 0.1
    TONE = 300  # Bandwidth to eliminate noise
    BANDWIDTH = 30
    RELATIVE_FREQ = 440.0
    #NUM_SAMPLES = 2048
    NUM_SAMPLES = 2048
    SAMPLING_RATE = 44100
    MIN_INTENSITY = 1.5
    PRECISION = 0.8

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
        pa = pyaudio.PyAudio()
        self.stream = pa.open(
            format=pyaudio.paInt16, 
            channels=1, 
            rate=Values.SAMPLING_RATE,
            input=True, 
            frames_per_buffer=Values.NUM_SAMPLES,
            input_device_index=0  # Change this to the index of your USB microphone
        )

        
    def get_frequency_from_samples(self, audio_data):
        normalized_data = audio_data / 32768.0
        intensity = abs(fft(normalized_data))[:Values.NUM_SAMPLES//2]
        frequencies = linspace(0.0, float(Values.SAMPLING_RATE)//2, num=Values.NUM_SAMPLES//2)
        max_intensity_index = intensity[1:].argmax() + 1
        if max_intensity_index != len(intensity)-1:
            y0, y1, y2 = log(intensity[max_intensity_index-1:max_intensity_index+2:])
            x1 = (y2 - y0) * 0.5 / (2 * y1 - y2 - y0)
            thefreq = (max_intensity_index+x1)*Values.SAMPLING_RATE/Values.NUM_SAMPLES
        else:
            thefreq = max_intensity_index*Values.SAMPLING_RATE/Values.NUM_SAMPLES

        theintensity = intensity[max_intensity_index]

        if thefreq == -9999:
            return None, theintensity
        else:
            return thefreq, theintensity
            
    def remove_outliers(data,threshold=3.5):
        median=np.median(data)
        mad = np.median(np.abs(data-median))
        threshold_value= threshold * mad
        cleaned_data = [value for value in data if np.abs(value - median) <= threshold_value]
        return cleaned_data

    def listen(self, note=NotesHz):
        num_samples = 5
        frequency = 0
        fr = []
        count = -1
        for i in range(num_samples):
            while self.stream.get_read_available() < Values.NUM_SAMPLES:
                #print(self.stream.get_read_available())
                #if count == self.stream.get_read_available() and count >= 10:
                    #break
                #count = self.stream.get_read_available() 
                time.sleep(0.00000000001)	    
            audio_data = fromstring(
                self.stream.read(
                    self.stream.get_read_available(), 
                    exception_on_overflow=False
                    ), 
                    dtype=short
                )[-Values.NUM_SAMPLES:]
            freq, intensity = self.get_frequency_from_samples(audio_data)
            if intensity < Values.MIN_INTENSITY or freq is None:
                return None,None
            else:
                fr.append(freq)
                # frequency += freq
        #f = remove_outliers(fr)
        median=np.median(fr)
        mad = np.median(np.abs(fr-median))
        threshold_value= 3.5 * mad
        print(fr)
        sum_first_half = 0
        sum_second_half = 0
        count = 0
        frequency = 0
        for val in fr:
            if count <= 5 or (np.abs((sum_first_half/count)-10) < 15):
                count += 1
                sum_first_half += val
            else:
                sum_second_half += val
        print(np.abs((sum_first_half/5)-(sum_second_half/5)))
        if(((sum_second_half/(10-count)) != 0) and np.abs((sum_first_half/(count))-(sum_second_half/(10-count))) > 150):
            print("yesssss")
            frequency = sum_second_half/(10-count)
        else:
            cleaned_data = [value for value in fr if np.abs(value - median) <= threshold_value]
            frequency= sum(cleaned_data)/len(cleaned_data)
        # frequency /= num_samples

        if frequency is not None and intensity > Values.MIN_INTENSITY:
            return frequency, intensity
        else:
            return None,None
            


# Define a function to convert frequency to note
def frequency_to_note(frequency):
    notes = {
        65.406: "C2", #69.30: "Db2",
        73.42: "D2",
        77.78: "Eb2", 
        82.41: "E2", 87.31: "F2", 
        92.50: "Gb2", 
        98.00: "G2", 
        103.83: "Ab2", 
        110.00: "A2", 
        116.54: "Bb2", 
        123.47: "B2",
        130.81: "C3", 
        138.59: "Db3", 
        146.83: "D3", 155.56: "Eb3", 
        164.81: "E3", 174.61: "F3", 
        185.00: "Gb3",
        196.00: "G3", 
        207.65: "Ab3", 
        220.00: "A3", 
        233.08: "Bb3", 
        246.94: "B3",
        261.63: "C4", 
        277.18: "Db4", 
        293.66: "D4", 
        311.13: "Eb4", 
        329.63: "E4", 349.23: "F4", 
        369.99: "Gb4", 
        392.00: "G4", 
        415.30: "Ab4", 
        440.00: "A4", 
        466.16: "Bb4", 
        493.88: "B4",
        523.25: "C5", 
        554.37: "Db5", 
        587.33: "D5", 
        622.25: "Eb5", 
        659.25: "E5", 
        698.46: "F5", 783.99: "G5", 
        880.00: "A5", 
        932.33: "Bb5", 
        987.77: "B5",
        1046.50: "C6"

    }
    closest_note = min(notes.keys(), key=lambda x: abs(x - frequency))
    
    return(notes[closest_note])


if __name__ == "__main__":
    tuner = Tuner()
    counter = 0
    while True:
        counter += 1
        frequency, intensity = tuner.listen()
        if frequency is not None:
            print(f"Detected frequency: {frequency:.2f} Hz")
            detected_note = frequency_to_note(frequency)
            print(f"intensity: {intensity:.2f}")
            print(f"Detected note: {detected_note}")

