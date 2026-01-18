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

        # 1) Wait for hand_state so we can pick a real card_id from the engine
        hand = None
        for i in range(20):
            raw = await asyncio.wait_for(ws.recv(), timeout=3)
            print(f"[PLAYER] recv (pre) #{i+1}:", raw)
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if msg.get("header") == "hand_state":
                hand = msg["data"]["cards"]
                break

        if not hand:
            print("[PLAYER] did not receive hand_state; cannot run engine-valid test")
            return

        # choose an organ card if possible (value == 0). fallback to first card
        organ = next((c for c in hand if c.get("value") == 0 and c.get("color") != "special"), None)
        chosen = organ or hand[0]
        card_id = chosen["card_id"]

        # 2) Send an organ play (valid without other players)
        test_msg = {
            "sender": "frontend",
            "header": "card_play",
            "data": {"action": "organ", "card_id": card_id},
            "request_id": "req-1",
        }

        await ws.send(json.dumps(test_msg))
        print("[PLAYER] sent:", json.dumps(test_msg))

        # 3) Wait for attempt with req-1
        for i in range(20):
            raw = await asyncio.wait_for(ws.recv(), timeout=3)
            print(f"[PLAYER] recv #{i+1}:", raw)
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if msg.get("header") == "attempt" and msg.get("request_id") == "req-1":
                print("[PLAYER] got attempt for req-1:", msg)
                return

        print("[PLAYER] did not receive attempt for req-1 within 20 messages")



async def main():
    host_task = asyncio.create_task(host_listener())
    await asyncio.sleep(0.2)
    await player_sender()
    host_task.cancel()


asyncio.run(main())
