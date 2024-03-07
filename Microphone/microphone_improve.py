import numpy as np
import pyaudio
import scipy.fftpack
import time

# Constants
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096  # Increased buffer size for better frequency resolution
DEVICE_INDEX = 1
AMPLITUDE_THRESHOLD = 5000

# Note frequencies (for a simple subset of notes, A4 = 440Hz standard tuning)
NOTE_FREQUENCIES = {
    'C0': 16.35, 'C#0/Db0': 17.32, 'D0': 18.35, 'D#0/Eb0': 19.45, 'E0': 20.60, 'F0': 21.83, 'F#0/Gb0': 23.12, 'G0': 24.50, 'G#0/Ab0': 25.96, 'A0': 27.50, 'A#0/Bb0': 29.14, 'B0': 30.87,
    'C1': 32.70, 'C#1/Db1': 34.65, 'D1': 36.71, 'D#1/Eb1': 38.89, 'E1': 41.20, 'F1': 43.65, 'F#1/Gb1': 46.25, 'G1': 49.00, 'G#1/Ab1': 51.91, 'A1': 55.00, 'A#1/Bb1': 58.27, 'B1': 61.74,
    'C2': 65.41, 'C#2/Db2': 69.30, 'D2': 73.42, 'D#2/Eb2': 77.78, 'E2': 82.41, 'F2': 87.31, 'F#2/Gb2': 92.50, 'G2': 98.00, 'G#2/Ab2': 103.83, 'A2': 110.00, 'A#2/Bb2': 116.54, 'B2': 123.47,
    'C3': 130.81, 'C#3/Db3': 138.59, 'D3': 146.83, 'D#3/Eb3': 155.56, 'E3': 164.81, 'F3': 174.61, 'F#3/Gb3': 185.00, 'G3': 196.00, 'G#3/Ab3': 207.65, 'A3': 220.00, 'A#3/Bb3': 233.08, 'B3': 246.94,
    'C4': 261.63, 'C#4/Db4': 277.18, 'D4': 293.66, 'D#4/Eb4': 311.13, 'E4': 329.63, 'F4': 349.23, 'F#4/Gb4': 369.99, 'G4': 392.00, 'G#4/Ab4': 415.30, 'A4': 440.00, 'A#4/Bb4': 466.16, 'B4': 493.88,
    'C5': 523.25, 'C#5/Db5': 554.37, 'D5': 587.33, 'D#5/Eb5': 622.25, 'E5': 659.25, 'F5': 698.46, 'F#5/Gb5': 739.99, 'G5': 783.99, 'G#5/Ab5': 830.61, 'A5': 880.00, 'A#5/Bb5': 932.33, 'B5': 987.77,
    'C6': 1046.50, 'C#6/Db6': 1108.73, 'D6': 1174.66, 'D#6/Eb6': 1244.51, 'E6': 1318.51, 'F6': 1396.91, 'F#6/Gb6': 1479.98, 'G6': 1567.98, 'G#6/Ab6': 1661.22, 'A6': 1760.00, 'A#6/Bb6': 1864.66, 'B6': 1975.53,
    'C7': 2093.00, 'C#7/Db7': 2217.46, 'D7': 2349.32, 'D#7/Eb7': 2489.02, 'E7': 2637.02, 'F7': 2793.83, 'F#7/Gb7': 2959.96, 'G7': 3135.96, 'G#7/Ab7': 3322.44, 'A7': 3520.00, 'A#7/Bb7': 3729.31, 'B7': 3951.07,
    'C8': 4186.01,
    # This includes all keys. For simplicity, only going up to C8. Add more if needed.
}


# Frequency tolerance for decay
FREQUENCY_TOLERANCE = 5  # Hz, adjust based on experimentation

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Open stream
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK, input_device_index=DEVICE_INDEX)

print("Detecting key presses... Press CTRL+C to stop.")

def find_closest_notes(frequencies, amplitudes):
    detected_notes = []
    for freq in frequencies[amplitudes > AMPLITUDE_THRESHOLD]:
        note, min_diff = None, float('inf')
        for note_name, note_freq in NOTE_FREQUENCIES.items():
            diff = abs(note_freq - freq)
            if diff < min_diff and diff <= FREQUENCY_TOLERANCE:
                note, min_diff = note_name, diff
        if note:
            detected_notes.append(note)
    return detected_notes
count = 0
try:
    while count < 10:
        count += 1
        data = stream.read(CHUNK, exception_on_overflow=False)
        signal = np.frombuffer(data, dtype=np.int16)
        
        # FFT
        freqs = scipy.fftpack.fftfreq(len(signal), 1.0/RATE)
        fft_signal = scipy.fftpack.fft(signal)
        amplitudes = np.abs(fft_signal)
        
        # Note detection
        detected_notes = find_closest_notes(freqs, amplitudes)
        if detected_notes:
            print(f"Detected notes: {', '.join(detected_notes)}")
        else:
            print("No note detected or below threshold.")

        time.sleep(0.1)  # Adjust based on real-time performance needs

except KeyboardInterrupt:
    print("Finished detecting.")

# Cleanup
stream.stop_stream()
stream.close()
audio.terminate()

