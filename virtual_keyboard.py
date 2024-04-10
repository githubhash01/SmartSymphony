from subprocess import Popen, PIPE
import asyncio

class VirtualKeyboard:
    def __init__(self):
        self.p = Popen(["VirtualPiano.exe"], shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        self.messages = []
    
    def __del__(self):
        self.p.kill()
    
    def get_hand_index(self, hand):
        if hand == None:
            return 1
        if hand == "left":
            return 2
        if hand == "right":
            return 3
        return 0
    
    async def update(self):
        while True:
            self.messages.append("\n")
            for message in self.messages:
                message_bytes = bytes(message, "UTF-8")
                self.p.stdin.write(message_bytes)
            self.p.stdin.flush()
            self.p.stdout.flush()
            self.messages = []
            await asyncio.sleep(0.01)
    
    def press_key(self, key, hand):
        self.messages.append(f"p {key.key_num - 21} {self.get_hand_index(hand)},")
    
    def unpress_key(self, key):
        self.messages.append(f"p {key.key_num - 21} {0},")
    
    def indicate_key(self, key, hand, colour):
        r, g, b, _ = colour
        self.messages.append(f"i {key.key_num - 21} {self.get_hand_index(hand)} {r} {g} {b},")
    
    def unindicate_key(self, key):
        self.messages.append(f"i {key.key_num - 21} {0},")