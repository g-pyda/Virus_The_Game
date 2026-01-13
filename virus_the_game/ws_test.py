import asyncio
import websockets

ROOM = "ROOM123"
HOST_PORT = 8000

HOST_URL = f"ws://127.0.0.1:{HOST_PORT}/ws/game/{ROOM}/host/"
PLAYER_URL = f"ws://127.0.0.1:{HOST_PORT}/ws/game/{ROOM}/player/1/"

async def host_listener():
    async with websockets.connect(HOST_URL) as ws:
        print("[HOST] connected:", HOST_URL)
        while True:
            msg = await ws.recv()
            print("[HOST] recv:", msg)

async def player_sender():
    async with websockets.connect(PLAYER_URL) as ws:
        print("[PLAYER] connected:", PLAYER_URL)
        test_msg = '{"action":"attack","card_id":1,"target_id":2}'
        await ws.send(test_msg)
        print("[PLAYER] sent:", test_msg)

        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=2)
            print("[PLAYER] recv:", msg)
        except asyncio.TimeoutError:
            print("[PLAYER] no message within 2s")

async def main():
    host_task = asyncio.create_task(host_listener())
    await asyncio.sleep(0.2)
    await player_sender()
    host_task.cancel()

asyncio.run(main())
