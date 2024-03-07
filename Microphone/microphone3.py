#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  microphone3.py
#  
#  Copyright 2024  <pi@porygon>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import pyaudio
import time
import numpy as np
from numpy import fromstring

class Values():
    SENSITIVITY = 0.1
    TONE = 300  # Bandwidth to eliminate noise
    BANDWIDTH = 30
    NUM_SAMPLES = 2048
    SAMPLING_RATE = 44100

    MIN_INTENSITY = 5 # intensity below which input is ignored
    PRECISION = 0.8 # number of Hertz to allow either side of a note

class PianoKeys():
    # Example frequencies for the keys, you may need to adjust these
    A3 = 220
    B3 = 246.94
    C4 = 261.63
    D4 = 293.66
    E4 = 329.63
    F4 = 349.23
    G4 = 392

class PianoDetector():
    def __init__(self):
        pa = pyaudio.PyAudio()
        self.stream = pa.open(
            format=pyaudio.paInt16, 
            channels=1, 
            rate=Values.SAMPLING_RATE,
            input=True, 
            frames_per_buffer=Values.NUM_SAMPLES
        )

    def get_frequency_from_samples(self, audio_data):
        normalized_data = audio_data / 32768.0
        intensity = np.abs(fft(normalized_data))[:Values.NUM_SAMPLES//2]
        frequencies = linspace(0.0, float(Values.SAMPLING_RATE)//2, num=Values.NUM_SAMPLES//2)

        max_intensity_index = intensity[1:].argmax() + 1
        
        # Use quadratic interpolation around the max
        if max_intensity_index != len(intensity)-1:
            y0, y1, y2 = log(intensity[max_intensity_index-1:max_intensity_index+2:])
            x1 = (y2 - y0) * 0.5 / (2 * y1 - y2 - y0)
            thefreq = (max_intensity_index+x1)*Values.SAMPLING_RATE/Values.NUM_SAMPLES
        else:
            thefreq = max_intensity_index*Values.SAMPLING_RATE/Values.NUM_SAMPLES

        theintensity = intensity[max_intensity_index]

        return thefreq, theintensity

    def listen(self):
        while True:
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
            
            # Example detection logic for piano keys
            if intensity >= Values.MIN_INTENSITY:
                if abs(freq - PianoKeys.A3) < Values.PRECISION:
                    print("A3 key pressed")
                elif abs(freq - PianoKeys.B3) < Values.PRECISION:
                    print("B3 key pressed")
                # Add more key comparisons for other piano keys

if __name__ == "__main__":
    detector = PianoDetector()
    detector.listen()
