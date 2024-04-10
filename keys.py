class Key:
    def __init__(self, key_num, note=None):
        self.key_num = key_num
        if note:
            self.note = note
        else:
            self.note = self.get_note()
        self.led_num = self.get_led()
        self.actuator = self.get_actuator()

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
        octave_2_dict = {'C':0, 'C#':2, 'D':4, 'D#':6, 'E':8, 'F':10, 'F#':12, 'G':14, 'G#':16, 'A':18, 'A#':20, 'B':21}
        octave_3_dict = {'C':23, 'C#':25, 'D':27, 'D#':29, 'E':31, 'F':33, 'F#':35, 'G':37, 'G#':39, 'A':41, 'A#':43, 'B':45}
        octave_4_dict = {'C':47, 'C#':49, 'D':51, 'D#':53, 'E':55, 'F':57, 'F#':59, 'G':61, 'G#':62, 'A':64, 'A#':66, 'B':68}
        octave_5_dict = {'C':70, 'C#':72, 'D':74, 'D#':76, 'E':77, 'F':79, 'F#':81, 'G':83, 'G#':85, 'A':87, 'A#':89, 'B':91}
        octave_6_dict = {'C':93}

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
    
    def get_actuator(self):
        note_to_actuator_dict = {'C' : 0, 'C#' : 1, 'D' : 2, 'D#' : 3, 'E' : 4, 'F' : 5, 'F#' : 6, 'G' : 7, 'G#' : 8, 'A' : 9, 'A#' : 10, 'B' : 11}
        note = self.note[:-1]
        return note_to_actuator_dict.get(note)


class KeyEvent:
    def __init__(self, key, event_type):
        self.key = key
        self.event_type = event_type
        
