import time
import asyncio
from fastapi import FastAPI
import socketio
from .system_monitor import get_system_stats
from .database.db_manager import init_db, insert_stats
from .app_manager import open_app, close_app_by_name, run_script, open_in_vscode
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

@sio.on("action_command")
async def handle_command(sid, data):
    print(f"SERVER: Received action_command from {sid}: {data}")
    action = data.get("action")
    args = data.get("args", {})
    response = {"status": "error", "message": "Unknown action"}

    if action == "open_app":
        success, msg = open_app(args.get("name"))
        response = {"status": "success" if success else "error", "message": msg}

    elif action == "close_app":
        killed, msg = close_app_by_name(args.get("name"))
        response = {"status": "success" if killed else "error", "message": msg}

    elif action == "run_script":
        success, msg = run_script(args.get("path"))
        response = {"status": "success" if success else "error", "message": msg}

    elif action == "open_in_vscode":
        success, msg = open_in_vscode(args.get("path"))
        response = {"status": "success" if success else "error", "message": msg}

    print(f"SERVER: Sending action_response to {sid}: {response}")
    await sio.emit("action_response", response, to=sid)
