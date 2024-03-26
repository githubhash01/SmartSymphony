import asyncio
import json
import sys
import websockets
import requests
import base64
import io
from lightstrip import Lightstrip
from actuators import Actuators
from controller import Controller
from keys import Key
from VariableMicrophone import Tuner

this_module = sys.modules[__name__]

# Ideally, this would be something like
# https://smartsymphony.com, rather than
# an IP with a port. make sure to change
# it when you boot up the website to the
# website IP!.
BaseURL = "http://172.24.53.168:5000"

lightstrip = Lightstrip()
actuators = Actuators()
microphone = Tuner(1, 115, 75, 30, 10, 40, 120, 0) 
controller = Controller(microphone)

class Client:
    def __init__(self, websocket):
        self.websocket = websocket
        self.listen = False
        self.authenticated = False
    
    def get_websocket(self):
        return self.websocket
        
    def set_listening(self, listening):
        self.listen = listening
    
    def is_listening(self):
        return self.listen

class ClientManager:
    def __init__(self):
        self.clients = set()
        self.num_listening = 0
    
    def add_client(self, client):
        if len(self.clients) == 0:
            self.clients.add(client)
            return True
        return False
    
    def remove_client(self, client):
        if client.is_listening():
            self.num_listening -= 1
        self.clients.remove(client)
    
    def set_listening(self, client, listening):
        if not client.is_listening() and listening:
            self.num_listening += 1
        elif client.is_listening() and not listening:
            self.num_listening -= 1
        client.set_listening(listening)
    
    def broadcast(self, message):
        for client in self.clients:
            if client.is_listening():
                asyncio.create_task(send(client.get_websocket(), message))
    
    def any_listening(self):
        return self.num_listening > 0

cm = ClientManager()

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

def cmd_verify_all(client, requirements):
    result = {}
    for requirement in requirements:
        result[requirement] = True
    return result
    
def cmd_is_playing_note(client, note):
    return note in microphone.get_notes()
    
def cmd_play_note(client, info):
    info = json.loads(info)
    key = Key(0, info["note"])
    if info["hardware"] == "lightstrip":
        asyncio.create_task(lightstrip.play_note(key, float(info["length"])))
    elif info["hardware"] == "actuators":
        asyncio.create_task(lightstrip.play_note(key, float(info["length"])))
    
def cmd_start_note(client, info):
    info = json.loads(info) 
    key = Key(0, info["note"])
    if info["hardware"] == "lightstrip":
        lightstrip.start_note(key)
    elif info["hardware"] == "actuators":
        lightstrip.start_note(key)
    
def cmd_stop_note(client, info):
    info = json.loads(info)
    key = Key(0, info["note"])
    if info["hardware"] == "lightstrip":
        lightstrip.stop_note(key)
    elif info["hardware"] == "actuators":
        lightstrip.stop_note(key)
    
def cmd_set_speed(client, speed):
    controller.set_speed(speed)
    
def cmd_set_time(client, time):
    controller.seek(time)
    
def cmd_set_play(client, start):
    if start:
        return controller.play()
    return controller.pause()
    
def cmd_set_hardware(client, info):
    info = json.loads(info)
    feedback = False
    hardware = None
    if info["hardware"] == "actuators":
        feedback = False
        hardware = actuators
    elif info["hardware"] == "lightstrip":
        feedback = False
        hardware = lightstrip
    elif info["hardware"] == "feedback":
        feedback = True
        hardware = lightstrip
    controller.set_feedback(info["hand"], feedback)
    controller.set_hardware(info["hand"], hardware)
    
def cmd_set_midi(client, info):
    info = json.loads(info)
    left_midi_file = io.BytesIO(base64.b64decode(info["left"]))
    right_midi_file = io.BytesIO(base64.b64decode(info["right"]))
    controller.set_midi(left_midi_file, right_midi_file)

def cmd_listen(client, listening):
    cm.set_listening(client, listening)

def create_error(reason):
    return create_message(None, "error", reason)

async def send(websocket, message):
    try:
        await websocket.send(message)
    except websockets.ConnectionClosed:
        pass

async def handler(websocket, path):
    path = path[1:]
    auth_user = dict(item.split("=") for item in path.split(","))
    auth_user = dict([key, int(value)] for key, value in auth_user.items())
    assert "user_id" in auth_user
    assert "auth_code" in auth_user
    assert len(auth_user) == 2
    global credentials
    auth_user = credentials | auth_user
    valid = False
    with requests.Session() as session:
        valid = session.post(BaseURL + "/auth_user", data=auth_user).json()
    if valid:
        client = Client(websocket)
        if cm.add_client(client):
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
                    except Exception as e:
                        print(e)
                        error = create_error(f"error calling {cmd_name}")
                        await send(client.get_websocket(), error)
                        continue
            finally:
                controller.stop()
                cm.remove_client(client)
            
async def measure_microphone():
    prev_notes = set()
    was_awaiting = False
    while True:
        if cm.any_listening():
            microphone.start()
            microphone.process_samples()
            current_notes = microphone.get_notes()
            in_notes = current_notes.difference(prev_notes)
            out_notes = prev_notes.difference(current_notes)
            for in_note in in_notes:
                print("start: ", in_note) 
                cm.broadcast(create_message(None, "start", in_note))
            for out_note in out_notes:
                cm.broadcast(create_message(None, "end", out_note))
            prev_notes = current_notes.copy()
            is_awaiting = microphone.is_awaiting()
            if was_awaiting != is_awaiting:
                cm.broadcast(create_message(None, "awaiting", is_awaiting))
                was_awaiting = is_awaiting
        else:
            microphone.stop()
        await asyncio.sleep(0.1)
        
async def main():
    asyncio.create_task(measure_microphone())
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()

if __name__ == "__main__":
    global credentials

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

