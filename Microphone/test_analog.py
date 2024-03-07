import time
from numpy import zeros, linspace, short, fromstring, hstack, transpose, log, log2
from scipy.fft import fft
import numpy as np
from grove.adc import ADC

class Values():
    SENSITIVITY = 0.1
    TONE = 300  # Bandwidth to eliminate noise
    BANDWIDTH = 30
    RELATIVE_FREQ = 440.0
    NUM_SAMPLES = 2048
    SAMPLING_RATE = 44100
    MIN_INTENSITY = 0
    PRECISION = 0.8
    
class NotesHz():
    C0  = 16.35
    Cs0 = 17.32
    Db0 = 17.32
    D0  = 18.35
    Ds0 = 19.45
    Eb0 = 19.45
    E0  = 20.60
    F0  = 21.83
    Fs0 = 23.12
    Gb0 = 23.12
    G0  = 24.50
    Gs0 = 25.96
    Ab0 = 25.96
    A0  = 27.50
    As0 = 29.14
    Bb0 = 29.14
    B0  = 30.87
    C1  = 32.70
    Cs1 = 34.65
    Db1 = 34.65
    D1  = 36.71
    Ds1 = 38.89
    Eb1 = 38.89
    E1  = 41.20
    F1  = 43.65
    Fs1 = 46.25
    Gb1 = 46.25
    G1  = 49.00
    Gs1 = 51.91
    Ab1 = 51.91
    A1  = 55.00
    As1 = 58.27
    Bb1 = 58.27
    B1  = 61.74
    C2  = 65.406
    Cs2 = 69.30
    Db2 = 69.30
    D2  = 73.42
    Ds2 = 77.78
    Eb2 = 77.78
    E2  = 82.41
    F2  = 87.31
    Fs2 = 92.50
    Gb2 = 92.50
    G2  = 98.00
    Gs2 = 103.83
    Ab2 = 103.83
    A2  = 110.00
    As2 = 116.54
    Bb2 = 116.54
    B2  = 123.47
    C3  = 130.81
    Cs3 = 138.59
    Db3 = 138.59
    D3  = 146.83
    Ds3 = 155.56
    Eb3 = 155.56
    E3  = 164.81
    F3  = 174.61
    Fs3 = 185.00
    Gb3 = 185.00
    G3  = 196.00
    Gs3 = 207.65
    Ab3 = 207.65
    A3  = 220.00
    As3 = 233.08
    Bb3 = 233.08
    B3  = 246.94
    C4  = 261.63
    Cs4 = 277.18
    Db4 = 277.18
    D4  = 293.66
    Ds4 = 311.13
    Eb4 = 311.13
    E4  = 329.63
    F4  = 349.23
    Fs4 = 369.99
    Gb4 = 369.99
    G4  = 392.00
    Gs4 = 415.30
    Ab4 = 415.30
    A4  = 440.00
    As4 = 466.16
    Bb4 = 466.16
    B4  = 493.88
    C5  = 523.25
    Cs5 = 554.37
    Db5 = 554.37
    D5  = 587.33
    Ds5 = 622.25
    Eb5 = 622.25
    E5  = 659.25
    F5  = 698.46
    Fs5 = 739.99
    Gb5 = 739.99
    G5  = 783.99
    Gs5 = 830.61
    Ab5 = 830.61
    A5  = 880.00
    As5 = 932.33
    Bb5 = 932.33
    B5  = 987.77
    C6  = 1046.50
    Cs6 = 1108.73
    Db6 = 1108.73
    D6  = 1174.66
    Ds6 = 1244.51
    Eb6 = 1244.51
    E6  = 1318.51
    F6  = 1396.91
    Fs6 = 1479.98
    Gb6 = 1479.98
    G6  = 1567.98
    Gs6 = 1661.22
    Ab6 = 1661.22
    A6  = 1760.00
    As6 = 1864.66
    Bb6 = 1864.66
    B6  = 1975.53
    C7  = 2093.00
    Cs7 = 2217.46
    Db7 = 2217.46
    D7  = 2349.32
    Ds7 = 2489.02
    Eb7 = 2489.02
    E7  = 2637.02
    F7  = 2793.83
    Fs7 = 2959.96
    Gb7 = 2959.96
    G7  = 3135.96
    Gs7 = 3322.44
    Ab7 = 3322.44
    A7  = 3520.00
    As7 = 3729.31
    Bb7 = 3729.31
    B7  = 3951.07
    C8  = 4186.01
    Cs8 = 4434.92
    Db8 = 4434.92
    D8  = 4698.63
    Ds8 = 4978.03
    Eb8 = 4978.03
    E8  = 5274.04
    F8  = 5587.65
    Fs8 = 5919.91
    Gb8 = 5919.91
    G8  = 6271.93
    Gs8 = 6644.88
    Ab8 = 6644.88
    A8  = 7040.00
    As8 = 7458.62
    Bb8 = 7458.62
    B8  = 7902.13

class Tuner():
    def __init__(self):
        self.adc = ADC()
        self.channel = 0  # Adjust this according to the channel your Grove analog microphone is connected to
    def sound(self):
        '''
        Get the sound strength value

        Returns:
            (int): ratio, 0(0.0%) - 1000(100.0%)
        '''
        value = self.adc.read(self.channel)
        return value

    def get_frequency_from_samples(self, audio_data):
        normalized_data = audio_data / 32768.0
        intensity = abs(fft(normalized_data))[:Values.NUM_SAMPLES//2]
        frequencies = linspace(0.0, float(Values.SAMPLING_RATE)//2, num=Values.NUM_SAMPLES//2)
        max_intensity_index = intensity[1:].argmax() + 1
        
        if np.any(intensity == 0):
            return None, None
        
        y0, y1, y2 = log(intensity[max_intensity_index-1:max_intensity_index+2:])
        if (y1 - y2 - y0) == 0:
            return None, None
        x1 = (y2 - y0) * 0.5 / (2 * y1 - y2 - y0)
            	
        thefreq = (max_intensity_index+x1)*Values.SAMPLING_RATE/Values.NUM_SAMPLES
        
            #thefreq = max_intensity_index*Values.SAMPLING_RATE/Values.NUM_SAMPLES

        theintensity = intensity[max_intensity_index]

        if thefreq == -9999:
            return None, theintensity
        else:
            return thefreq, theintensity

    def listen(self, note=NotesHz):
        num_samples = 5
        frequency = 0
        fr = []
        for i in range(num_samples):
            while self.stream.get_read_available() < Values.NUM_SAMPLES:
                time.sleep(0.01)	    
            audio_data = fromstring(
                self.stream.read(
                    self.stream.get_read_available(), 
                    exception_on_overflow=False
                    ), 
                    dtype=short
                )[-Values.NUM_SAMPLES:]
            freq, intensity = self.get_frequency_from_samples(audio_data)
            if intensity < Values.MIN_INTENSITY or freq is None:
                return None
            else:
                fr.append(freq)
                # frequency += freq
        #f = remove_outliers(fr)
        median=np.median(fr)
        mad = np.median(np.abs(fr-median))
        threshold_value= 3.5 * mad
        print(fr)
        cleaned_data = [value for value in fr if np.abs(value - median) <= threshold_value]
        frequency= sum(cleaned_data)/len(cleaned_data)
        # frequency /= num_samples

        if frequency is not None and intensity > Values.MIN_INTENSITY:
            return frequency
        else:
            return None

    def get_audio_data(self):
        audio_data = zeros(0)
        for _ in range(Values.NUM_SAMPLES):
            value = self.adc.read(self.channel)
            audio_data = hstack((audio_data, value))
        return audio_data

# Define a function to convert frequency to note
def frequency_to_note(frequency):
    notes = {
        27.5: "A0", 29.14: "Bb0", 30.87: "B0",
        # Add the rest of the notes here
    }
    closest_note = min(notes.keys(), key=lambda x: abs(x - frequency))
    return notes[closest_note]

if __name__ == "__main__":
    tuner = Tuner()
    counter = 0
    while True:
        counter += 1
        frequency, intensity = tuner.listen()
        if frequency is not None:
            print(f"Detected frequency: {frequency:.2f} Hz")
            print(f"Detected intensity: {intensity:.2f}")
            detected_note = frequency_to_note(frequency)
            print(f"Detected note: {detected_note}")
