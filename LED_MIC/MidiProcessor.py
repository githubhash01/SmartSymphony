"""
A python script that takes a midi file and converts it to a timeline of notes being played
"""
from Keys import Key, KeyEvent
import mido

def parseTrack(track):
    timeline = []
    current_time = 0

    for msg in track:
        current_time += msg.time
        if msg.type in ['note_on', 'note_off']:
            key = Key(msg.note - 12)
            event_type = 1 if msg.type == 'note_on' and msg.velocity != 0 else 0
            event = KeyEvent(key, event_type)
            timeline.append((current_time, event))

    return timeline


def parseMidi(midi_file, track_nums=None):
    mid = mido.MidiFile(midi_file)
    
    if track_nums:
        mid.tracks = [mid.tracks[i] for i in track_nums] 
    combined_timeline = [event for track in mid.tracks for event in parseTrack(track) if track]
    combined_timeline.sort(key=lambda x: x[0])

    # add wait times to the timeline
    wait_times = []
    for i in range(len(combined_timeline) - 1):
        wait_time = combined_timeline[i + 1][0] - combined_timeline[i][0]
        wait_times.append(wait_time)
    wait_times.append(0)  # no wait time for the last event
    combined_timeline = [(time, wait, event) for (time, event), wait in zip(combined_timeline, wait_times)]
    return combined_timeline



