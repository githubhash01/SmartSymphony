import asyncio

class VirtualActuators:
    def __init__(self, virtual_keyboard):
        self.stop()
        self.virtual_keyboard = virtual_keyboard
            
    def stop(self):
        pass
    
    def pause(self):
        self.stop()
        
    def start_note(self, key, hand=None):
        self.virtual_keyboard.press_key(key, hand)
    
    def stop_note(self, key, hand=None):
        self.virtual_keyboard.unpress_key(key)
    
    async def play_note(self, key, length):
        try:
            self.start_note(key)
            await asyncio.sleep(length)
            self.stop_note(key)
        except Exception as e:
            print(e)