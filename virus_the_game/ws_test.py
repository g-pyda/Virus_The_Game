import asyncio
import json
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

        test_msg = {
            "sender": "frontend",
            "header": "card_play",
            "data": {"action": "attack", "card_id": 1, "target_id": 2},
            "request_id": "req-1",
        }

        await ws.send(json.dumps(test_msg))
        print("[PLAYER] sent:", json.dumps(test_msg))

        # Read multiple messages; stop once we get the attempt for req-1
        for i in range(10):
            raw = await asyncio.wait_for(ws.recv(), timeout=3)
            print(f"[PLAYER] recv #{i+1}:", raw)

            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            # New protocol attempt
            if msg.get("header") == "attempt" and msg.get("request_id") == "req-1":
                print("[PLAYER] got attempt for req-1:", msg)
                return

        print("[PLAYER] did not receive attempt for req-1 within 10 messages")


async def main():
    host_task = asyncio.create_task(host_listener())
    await asyncio.sleep(0.2)
    await player_sender()
    host_task.cancel()


asyncio.run(main())
