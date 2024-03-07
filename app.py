import asyncio
import json

import websockets

async def handler(websocket):
	async for message in websocket:
		print(message)
		await websocket.send(message)
		x = {
			"cmd_name": "test_or_whatever",
			"cmd_data": "Nothing"
		}
		await websocket.send(json.dumps(x))


async def main():
	async with websockets.serve(handler, "", 8001):
		await asyncio.Future()


if __name__ == "__main__":
	asyncio.run(main())