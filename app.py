import asyncio
import json
import sys
import websockets
import requests
import base64
from LED import LEDStrip
from microphone import Microphone
from Demo2Song import Actuators

this_module = sys.modules[__name__]

led_strip = LEDStrip(20) # brightness set to 20/255
led_strip.begin()

#actuators = Actuators()

microphone = Microphone()
microphone.start()
#tuner.start()

class Client:
    def __init__(self, websocket):
        self.websocket = websocket
        self.listen = False
    
    def get_websocket(self):
        return self.websocket
        
    def set_listening(self, listening):
        self.listen = listening
    
    def is_listening(self):
        return self.listen
        
def create_message(cmd_id, cmd_name, cmd_data):
    return json.dumps({
        "cmd_id": cmd_id,
        "cmd_name": cmd_name,
        "cmd_data": cmd_data
    })

def cmd_verify(client, requirements):
    # TODO: This function should return True IFF all the resources in
    # 'requirements' are connected
    print(requirements)
    return True
    
def cmd_is_playing_note(client, note):
    # TODO: This function should return True IFF the user is playing
    # the note 'note' on the keyboard. If 'note' is None, return True
    # IFF any note is being played. If 'note' is an array of notes,
    # return True IFF all notes in the array are being played
    print(note)
    return False
    
def cmd_play_note(client, info):
    # TODO: This function plays the note specified in 'info', either
    # on the actuators or lightbar, specified in 'info'. A play length
    # also provided in info
    print(info)
    
def cmd_load(client, info):
    decoded = base64.b64decode(info)
    with open("test.mid", "wb") as f:
        f.write(decoded)
    print("TEST")
    asyncio.create_task(led_strip.playMidi("test.mid", 0.75))
    return True
    
def cmd_play(client, start):
    # TODO: play the midi on the lightbar, return True IFF successful
    # false otherwise
    print(start)
    return True

# TODO: HACK!!! Fix this
num_listening = 0

def cmd_listen(client, enable):
    # TODO: This function should enable or disable client listening.
    # If listening is enabled, the client should be sent a message
    # every time a note begins to be played containing the note being
    # played as well as a message when a note stops being played.
    #if not client.is_listening() and enable:
    #    num_listening += 1
    #elif client.is_listening() and not enable:
    #    num_listening -= 1
    client.set_listening(enable)

def create_error(reason):
    return create_message(None, "error", reason)
    
CLIENTS = set()

async def send(websocket, message):
    try:
        await websocket.send(message)
    except websockets.ConnectionClosed:
        pass

def broadcast(message):
    for client in CLIENTS:
        if client.is_listening():
            asyncio.create_task(send(client.get_websocket(), message))

async def handler(websocket):
    client = Client(websocket)
    CLIENTS.add(client)
    try:
        async for message in websocket:
            print(message)
            message = json.loads(message)
            if not "cmd_name" in message:
                error = create_error("message has no cmd_name")
                await send(client.get_websocket(), error)
                continue
            cmd_id = message.get("cmd_id")
            cmd_name = message["cmd_name"]
            cmd_data = message["cmd_data"]
            try:
                cmd = getattr(this_module, f"cmd_{cmd_name}")
                result_data = cmd(client, cmd_data)
                result = create_message(cmd_id, cmd_name, result_data)
                await send(client.get_websocket(), result)
            except:
                error = create_error(f"error calling {cmd_name}")
                await send(client.get_websocket(), error)
                continue
    finally:
        CLIENTS.remove(client)

# TODO: clean and fix, how to keep track of connected users? Maybe a function or something
async def measure():
    prev_notes = set()
    while True:
        #if num_listening != 0:
        microphone.calculate_notes()
        current_notes = microphone.get_notes()
        in_notes = current_notes.difference(prev_notes)
        out_notes = prev_notes.difference(current_notes)
        for in_note in in_notes:
            broadcast(create_message(None, "start", in_note))
        for out_note in out_notes:
            broadcast(create_message(None, "end", out_note))
        prev_notes = current_notes.copy()
        await asyncio.sleep(0)
        
async def main():
    asyncio.create_task(measure())
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()

# Ideally, this would be something like
# https://smartsymphony.com, rather than
# an IP with a port. make sure to change
# it when you boot up the website to the
# website IP!
BaseURL = "http://172.24.47.44:5000"

if __name__ == "__main__":
    with open("credentials.txt") as credentials_file: 
        credentials_contents = credentials_file.read()
        credentials = json.loads(credentials_contents)
    
    assert "devicename" in credentials
    assert "password" in credentials
    assert "key" in credentials
    assert len(credentials) == 3
    
    with requests.Session() as session:
        session.post(BaseURL + "/enable_device", data=credentials)
    try:
        asyncio.run(main())
    except:
        with requests.Session() as session:
            session.post(BaseURL + "/disable_device", data=credentials)

