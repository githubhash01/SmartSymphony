import numpy as np
import pyaudio
import scipy.fftpack

# Constants
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Mono audio
RATE = 44100  # Sample rate
CHUNK = 1024  # Frames per buffer
RECORD_SECONDS = 5  # Seconds to record
DEVICE_INDEX = 1  # Device index found by arecord -l, may need adjustment

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Open stream
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK, input_device_index=DEVICE_INDEX)

print("Recording...")

frames = []

# Record for a few seconds
for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(np.frombuffer(data, dtype=np.int16))

print("Finished recording.")

# Stop and close the stream
stream.stop_stream()
stream.close()
audio.terminate()

# Concatenate all the numpy arrays into one
signal = np.concatenate(frames)

# Perform FFT
freqs = scipy.fftpack.fftfreq(len(signal), 1.0/RATE)
fft_signal = scipy.fftpack.fft(signal)

# Find the peak frequency
dominant_freq = freqs[np.argmax(np.abs(fft_signal))]

print(f"Dominant frequency: {dominant_freq} Hz")



