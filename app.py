import asyncio
import json
import sys

import websockets
import socket
import requests

this_module = sys.modules[__name__]

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
	
def cmd_load_midi(client, midi):
	# TODO: This function should load the MIDI file 'midi' to be used
	# with the actuators and lightbar
	print(midi)
	return True

def cmd_listen(client, enable):
	# TODO: This function should enable or disable client listening.
	# If listening is enabled, the client should be sent a message
	# every time a note begins to be played containing the note being
	# played as well as a message when a note stops being played.
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
			broadcast(create_error("TEST"))
	finally:
		CLIENTS.remove(client)

async def measure():
	playing = False
	while True:
		if playing:
			broadcast(create_message(None, "start", "C4"))
		else:
			broadcast(create_message(None, "end", "C4"))
		playing = not playing
		await asyncio.sleep(1.0)

async def main():
	asyncio.create_task(measure())
	async with websockets.serve(handler, "", 8001):
		await asyncio.Future()

BaseURL = "127.0.0.1:5000"

if __name__ == "__main__":
	payload = {
		"devicename": "test_device",
		"password": "test_password",
	}

	with requests.Session() as session:
		session.post("https://" + BaseURL + "/enable_device", data=payload, verify=False)

	try:
		asyncio.run(main())
	except:
		with requests.Session() as session:
			session.post("https://" + BaseURL + "/disable_device", data=payload, verify=False)

 
