import asyncio
import websockets
import json


async def listen():
    uri = "ws://localhost:8000/ws/metrics"
    print(f"Connecting to {uri}...\n")

    async with websockets.connect(uri) as ws:
        for i in range(5):  # receive 5 snapshots then stop
            raw = await ws.recv()
            data = json.loads(raw)
            print(f"[{i+1}] CPU: {data['cpu']['usage_percent']}% | "
                  f"RAM: {data['ram']['usage_percent']}% | "
                  f"Health: {data['health_score']}")


asyncio.run(listen())