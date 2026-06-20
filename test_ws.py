import asyncio
import websockets

async def main():
    uri = "ws://localhost:8000/api/v1/ws/metrics"

    async with websockets.connect(uri) as ws:
        print("Connected")
        while True:
            msg = await ws.recv()
            print(msg)

asyncio.run(main())
