import asyncio

class VirtualLightstrip:
    BLACK = (0, 0, 0, 0)
    ORANGE = (255, 220, 125, 0)
    DARK_ORANGE = (255, 187, 0, 0)
    BLUE = (122, 122, 255, 0)
    DARK_BLUE = (0, 0, 255, 0)
    WHITE = (255, 0, 0, 0)
    DARK_WHITE = (180, 0, 0, 0)

    def __init__(self, virtual_keyboard):
        self.stop()
        self.virtual_keyboard = virtual_keyboard
            
    def stop(self):
        self.keysList = [[] for _ in range(128)]
    
    def pause(self):
        pass
    
    def get_colour(self, key, hand):
        white_key = key.note[1] != "#"
        if hand == "left":
            return VirtualLightstrip.BLUE if white_key else VirtualLightstrip.DARK_BLUE
        elif hand == "right": 
            return VirtualLightstrip.ORANGE if white_key else VirtualLightstrip.DARK_ORANGE
        else:
            return VirtualLightstrip.WHITE if white_key else VirtualLightstrip.DARK_WHITE
    
    def start_note(self, key, hand=None):
        colour = self.get_colour(key, hand)
        self.keysList[key.key_num].append(colour)
        self.virtual_keyboard.indicate_key(key, hand, colour)
    
    def stop_note(self, key, hand=None):
        self.keysList[key.key_num].remove(self.get_colour(key, hand))
        if self.keysList[key.key_num] == []:
            self.virtual_keyboard.unindicate_key(key)
        else:
            self.virtual_keyboard.indicate_key(key, hand, self.keysList[key.key_num][-1])
    
    async def play_note(self, key, length):
        try:
            self.start_note(key)
            await asyncio.sleep(length)
            self.stop_note(key)
        except Exception as e:
            print(e)