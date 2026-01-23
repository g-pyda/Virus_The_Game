import asyncio
import json
import websockets

ROOM = "ROOM123"
HOST_PORT = 8000

HOST_URL = f"ws://127.0.0.1:{HOST_PORT}/ws/game/{ROOM}/host/"
P1_URL = f"ws://127.0.0.1:{HOST_PORT}/ws/game/{ROOM}/player/1/"
P2_URL = f"ws://127.0.0.1:{HOST_PORT}/ws/game/{ROOM}/player/2/"


async def host_listener():
    async with websockets.connect(HOST_URL) as ws:
        print("[HOST] connected:", HOST_URL)
        while True:
            print("[HOST] recv:", await ws.recv())


async def wait_for_hand(ws, label):
    # wait up to 30 messages for hand_state
    for i in range(30):
        raw = await asyncio.wait_for(ws.recv(), timeout=5)
        print(f"[{label}] recv #{i+1}:", raw)
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if msg.get("header") == "hand_state":
            return msg["data"]["cards"]
    return None


async def main():
    host_task = asyncio.create_task(host_listener())
    await asyncio.sleep(0.2)

    async with websockets.connect(P1_URL) as p1, websockets.connect(P2_URL) as p2:
        print("[P1] connected:", P1_URL)
        print("[P2] connected:", P2_URL)

        # Wait for hand_state for both players (game should auto-start once 2 connect)
        p1_hand = await wait_for_hand(p1, "P1")
        p2_hand = await wait_for_hand(p2, "P2")

        if p1_hand is None or p2_hand is None:
            print("Did not receive hand_state for one of the players")
            return

        print("[P1] hand len:", len(p1_hand))
        print("[P2] hand len:", len(p2_hand))

        # If you want: try a safe action from P1 (organ)
        if len(p1_hand) == 0:
            print("[P1] hand is empty; engine still not dealing cards")
            return

        organ = next((c for c in p1_hand if c.get("value") == 0 and c.get("color") != "special"), None)
        chosen = organ or p1_hand[0]
        card_id = chosen["card_id"]

        msg = {
            "sender": "frontend",
            "header": "card_play",
            "data": {"action": "organ", "card_id": card_id},
            "request_id": "req-organ-1",
        }
        await p1.send(json.dumps(msg))
        print("[P1] sent organ:", msg)

        # wait for attempt reply for req-organ-1
        for i in range(30):
            raw = await asyncio.wait_for(p1.recv(), timeout=5)
            print(f"[P1] recv (post) #{i+1}:", raw)
            m = json.loads(raw)
            if m.get("header") == "attempt" and m.get("request_id") == "req-organ-1":
                print("[P1] got attempt:", m)
                return

    host_task.cancel()


asyncio.run(main())
