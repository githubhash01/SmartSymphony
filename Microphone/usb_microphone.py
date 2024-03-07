#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  usb_microphone.py
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
#!/usr/bin/env python
import pyaudio
import numpy as np
from scipy.fft import fft
from scipy.signal import butter, lfilter
from time import sleep
import mido

# Constants for audio processing
NUM_SAMPLES = 2048
SAMPLING_RATE = 44100
NOISE_THRESHOLD = 0.01  # Threshold for noise reduction, adjust based on environment

# Comprehensive list of note frequencies for an 88-key piano
note_frequencies = {
    'A0': 27.50, 'A#0': 29.14, 'B0': 30.87,
    'C1': 32.70, 'C#1': 34.65, 'D1': 36.71, 'D#1': 38.89, 'E1': 41.20, 'F1': 43.65, 'F#1': 46.25, 'G1': 48.99, 'G#1': 51.91, 'A1': 55.00, 'A#1': 58.27, 'B1': 61.74,
    'C2': 65.41, 'C#2': 69.30, 'D2': 73.42, 'D#2': 77.78, 'E2': 82.41, 'F2': 87.31, 'F#2': 92.50, 'G2': 97.99, 'G#2': 103.83, 'A2': 110.00, 'A#2': 116.54, 'B2': 123.47,
    'C3': 130.81, 'C#3': 138.59, 'D3': 146.83, 'D#3': 155.56, 'E3': 164.81, 'F3': 174.61, 'F#3': 185.00, 'G3': 196.00, 'G#3': 207.65, 'A3': 220.00, 'A#3': 233.08, 'B3': 246.94,
    'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13, 'E4': 329.63, 'F4': 349.23, 'F#4': 369.99, 'G4': 392.00, 'G#4': 415.30, 'A4': 440.00, 'A#4': 466.16, 'B4': 493.88,
    'C5': 523.25, 'C#5': 554.37, 'D5': 587.33, 'D#5': 622.25, 'E5': 659.25, 'F5': 698.46, 'F#5': 739.99, 'G5': 783.99, 'G#5': 830.61, 'A5': 880.00, 'A#5': 932.33, 'B5': 987.77,
    'C6': 1046.50, 'C#6': 1108.73, 'D6': 1174.66, 'D#6': 1244.51, 'E6': 1318.51, 'F6': 1396.91, 'F#6': 1479.98, 'G6': 1567.98, 'G#6': 1661.22, 'A6': 1760.00, 'A#6': 1864.66, 'B6': 1975.53,
    'C7': 2093.00, 'C#7': 2217.46, 'D7': 2349.32, 'D#7': 2489.02, 'E7': 2637.02, 'F7': 2793.83, 'F#7': 2959.96, 'G7': 3135.96, 'G#7': 3322.44, 'A7': 3520.00, 'A#7': 3729.31, 'B7': 3951.07,
    'C8': 4186.01
}

# MIDI note frequencies
midi_note_frequencies = {
    21: 'A0', 22: 'A#0', 23: 'B0',
    # Rest of the MIDI note frequencies
}

# Function to read MIDI file and extract note events
def read_midi(filename):
    mid = mido.MidiFile(filename)
    notes = []
    for msg in mid:
        if msg.type == 'note_on':
            notes.append((msg.note, msg.time))
    return notes

# Butterworth bandpass filter functions
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def find_nearest_note(frequency):
    nearest_note = min(note_frequencies, key=lambda note: abs(note_frequencies[note] - frequency))
    return nearest_note

def main(midi_filename):
    # Read MIDI file
    midi_notes = read_midi(midi_filename)
    midi_note_iter = iter(midi_notes)

    # Initialize PyAudio
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=SAMPLING_RATE,
                 input=True, frames_per_buffer=NUM_SAMPLES)

    print("Piano key detector working. Press CTRL-C to quit.")

    correct_count = 0
    missed_count = 0
    wrong_count = 0

    while True:
        # Wait for enough samples to accumulate
        while stream.get_read_available() < NUM_SAMPLES:
            sleep(0.01)

        # Read data from the microphone
        audio_data = np.frombuffer(stream.read(stream.get_read_available(), exception_on_overflow=False), dtype=np.int16)[-NUM_SAMPLES:]
        # Normalize the audio data
        normalized_data = audio_data / np.max(np.abs(audio_data))
        # Apply band-pass filter
        filtered_data = butter_bandpass_filter(normalized_data, 27.5, 4186, SAMPLING_RATE, order=6)
        # Perform FFT and find the dominant frequency
        intensity = np.abs(fft(filtered_data))[:NUM_SAMPLES//2]
        frequencies = np.linspace(0.0, float(SAMPLING_RATE)/2, num=NUM_SAMPLES//2)
        # Apply noise threshold
        intensity[intensity < NOISE_THRESHOLD] = 0
        dominant_index = np.argmax(intensity)
        if intensity[dominant_index] > 0:  # Check if there's a dominant frequency above the threshold
            dominant_frequency = frequencies[dominant_index]

            # Find the nearest note to the detected frequency
            nearest_note = find_nearest_note(dominant_frequency)
            print(f"Detected note: {nearest_note} ({dominant_frequency:.2f} Hz)")

            # Compare with MIDI notes
            try:
                midi_note, _ = next(midi_note_iter)
                if nearest_note == midi_note_frequencies[midi_note]:
                    correct_count += 1
                else:
                    wrong_count += 1
            except StopIteration:
                missed_count += 1
                print("MIDI file has ended.")

        sleep(0.01)  # Short delay to prevent overwhelming the CPU

if __name__ == '__main__':
    midi_filename = 'your_midi_file.mid'  # Provide the path to your MIDI file
    main(midi_filename)


