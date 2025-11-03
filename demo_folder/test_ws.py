import asyncio
import socketio
from fastapi import FastAPI

app = FastAPI()
sio = socketio.AsyncServer(async_mode="asgi")
sio_app = socketio.ASGIApp(sio,app)

async def send_hello():
    while True:
        await sio.emit("hello",{"message":"Hi Pi"})
        await asyncio.sleep(1)

@sio.event
async def connect(sid,environ):
    print("Client connected:,{sid}")

@sio.event
async def connect(sid,environ):
    print("Client disconnected:,{sid}")

@app.on_event("startup")
async def start_background():
    asyncio.create_task(send_hello())