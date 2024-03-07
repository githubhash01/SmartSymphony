import pyaudio
from numpy import linspace, short, fromstring, hanning, log
from scipy.fft import fft
import numpy as np
from scipy.signal import butter, filtfilt
import time

class Values():
    SENSITIVITY = 50
    TONE = 300  # Bandwidth to eliminate noise
    BANDWIDTH = 30
    RELATIVE_FREQ = 440.0
    NUM_SAMPLES = 4096  # Increased for better frequency resolution
    SAMPLING_RATE = 44100
    MIN_INTENSITY = 2
    PRECISION = 0.8

class NotesHz():
    # Note frequencies
    C2  = 65.406
    D2  = 73.42
    E2  = 82.41
    F2  = 87.31
    G2  = 98.00
    A2  = 110.00

class Tuner():
    def __init__(self):
        pa = pyaudio.PyAudio()
        self.stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=Values.SAMPLING_RATE,
            input=True,
            frames_per_buffer=Values.NUM_SAMPLES,
            input_device_index=0  # Adjust as needed
        )

    def design_bandpass_filter(self, lowcut, highcut, fs, order=5):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a

    def apply_bandpass_filter(self, data, lowcut, highcut, fs, order=5):
        b, a = self.design_bandpass_filter(lowcut, highcut, fs, order=order)
        y = filtfilt(b, a, data)
        return y

    def get_frequency_from_samples(self, audio_data):
        # Apply bandpass filter
        filtered_data = self.apply_bandpass_filter(audio_data, 20, 4200, Values.SAMPLING_RATE, order=5)
        
        # Apply a Hanning window to the filtered data
        windowed_data = filtered_data * hanning(len(filtered_data))
        normalized_data = filtered_data / 32768.0
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

    def listen(self, note=NotesHz):
        num_samples = 10
        fr = []
        for i in range(num_samples):
            while self.stream.get_read_available() < Values.NUM_SAMPLES:
                time.sleep(0.01)  # Small delay to ensure buffer is full
            audio_data = fromstring(self.stream.read(Values.NUM_SAMPLES, exception_on_overflow=False), dtype=short)
            freq, intensity = self.get_frequency_from_samples(audio_data)
            if intensity < Values.MIN_INTENSITY or freq is None:
                return None, None
            else:
                fr.append(freq)
        
        # Processing frequencies
        median = np.median(fr)
        mad = np.median(np.abs(fr - median))
        threshold_value = 3.5 * mad
        print("fr",fr)
        cleaned_data = [value for value in fr if np.abs(value - median) <= threshold_value]
        print("cleaned_data",cleaned_data)
        if len(cleaned_data) == 0:  # Check if cleaned data is empty
            return None, None
        frequency = sum(cleaned_data) / len(cleaned_data)

        if frequency is not None and intensity > Values.MIN_INTENSITY:
            return frequency, intensity
        else:
            return None, None

def frequency_to_note(frequency):
    notes = {
        65.406: "C2", 69.30: "Db2",
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
        #415.30: "Ab4", 
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
    while True:
        frequency, intensity = tuner.listen()
        if frequency is not None:
            print(f"Detected frequency: {frequency:.2f} Hz, Intensity: {intensity:.2f}")
            detected_note = frequency_to_note(frequency)
            print(f"Detected note: {detected_note}")
