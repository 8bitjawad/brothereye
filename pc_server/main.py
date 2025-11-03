import time
import asyncio
from fastapi import FastAPI
import socketio
from .system_monitor import get_system_stats
from .database.db_manager import init_db, insert_stats

app = FastAPI()
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
sio_app = socketio.ASGIApp(sio,app)

init_db()
print("Database Initiated. Beginning Monitoring...")

async def monitor_loop():
    while True:
        stats = get_system_stats()
        print("SERVER: emitting stats...", stats)
        
        insert_stats(
            cpu = stats["cpu"],
            memory = stats["memory"],
            disk = stats["disk"],
            battery = stats["battery"]
        )
        await sio.emit("stats_update",stats)
        await asyncio.sleep(5)

@sio.event
async def connect(sid,environ):
    print(f"Client connected: {sid}")
    
@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@app.on_event("startup")
async def start_monitor():
    asyncio.create_task(monitor_loop())

@app.get("/api/usage")
async def status():
    return {"message":"Monitoring"}
