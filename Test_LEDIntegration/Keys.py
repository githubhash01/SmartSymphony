class Key:
    def __init__(self, key_num):
        self.key_num = key_num
        self.note = self.get_note()
        self.led_num = self.get_led()

    def get_note(self):
        note = self.key_num % 12
        octave = self.key_num // 12
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        note = notes[note]
        # constrain octave to be between 2 and 6
        if octave < 2:
            octave = 2
        elif octave > 5 and note != 'C':
            octave = 5
        elif octave > 5 and note == 'C':
            octave = 6
        note = note + str(octave)
        return note
    
    def get_led(self): 
        octave_2_dict = {'C':1, 'C#':2, 'D':3, 'D#':4, 'E':4, 'F':5, 'F#':6, 'G':7, 'G#':8, 'A':8, 'A#':9, 'B':10}
        octave_3_dict = {'C':11, 'C#':12, 'D':12, 'D#':13, 'E':14, 'F':15, 'F#':16, 'G':16, 'G#':17, 'A':18, 'A#':19, 'B':19}
        octave_4_dict = {'C':20, 'C#':21, 'D':22, 'D#':23, 'E':24, 'F':25, 'F#':25, 'G':26, 'G#':27, 'A':28, 'A#':28, 'B':29}
        octave_5_dict = {'C':30, 'C#':31, 'D':32, 'D#':32, 'E':33, 'F':34, 'F#':35, 'G':36, 'G#':36, 'A':37, 'A#':38, 'B':39}
        octave_6_dict = {'C':40}

        # get the octave of the note
        octave = self.note[-1]
        note = self.note[:-1]
        # return the led number based on the octave
        if octave == '2':
            return octave_2_dict[note]
        elif octave == '3':
            return octave_3_dict[note]
        elif octave == '4':
            return octave_4_dict[note]
        elif octave == '5':
            return octave_5_dict[note]
        elif octave == '6':
            return octave_6_dict[note]
        else:
            return -1

class KeyEvent:

    def __init__(self, key, event_type):
        self.key = key
        self.event_type = event_type
        
