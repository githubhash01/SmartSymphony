import pyaudio

pa = pyaudio.PyAudio()

for i in range(pa.get_device_count()):
    device_info = pa.get_device_info_by_index(i)
    print(f"Index: {i}, Name: {device_info['name']}, Input Channels: {device_info['maxInputChannels']}")
