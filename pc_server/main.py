import time
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
import socketio
from .system_monitor import get_system_stats
from .app_manager import open_app, close_app_by_name, run_script, open_in_vscode
from dotenv import load_dotenv
import os
import subprocess

load_dotenv()

SECRET_TOKEN = os.getenv("AUTH_TOKEN")
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs on startup
    asyncio.create_task(monitor_loop())
    print("Monitoring loop started...")
    yield
    # Runs on shutdown
    print("Server shutting down...")

app = FastAPI(lifespan=lifespan)
sio_app = socketio.ASGIApp(sio, app)

async def monitor_loop():
    while True:
        stats = get_system_stats()
        print("SERVER: emitting stats...", stats)
        await sio.emit("stats_update", stats)
        await asyncio.sleep(5)

@sio.event
async def connect(sid, environ):
    query = environ.get("QUERY_STRING", "")
    token = dict(q.split('=') for q in query.split('&') if '=' in q).get('token')
    if token != SECRET_TOKEN:
        print(f"Unauthorized connection attempt from {sid}")
        await sio.disconnect(sid)
        return
    print(f"Client connected: {sid}")


@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@app.get("/api/usage")
async def status():
    return {"message": "Monitoring active (no server-side DB)"}

@sio.on("action_command")
async def handle_action(sid, data):
    action = data.get("action")
    args = data.get("args", {})
    if action == "run_script":
        path = args.get("path")
        try:
            result = subprocess.run(["python", path], capture_output=True, text=True)
            output = result.stdout.strip() or "No output"
            await sio.emit("action_response", {"message": f"✅ Script executed successfully:\n{output}"}, to=sid)
        except Exception as e:
            await sio.emit("action_response", {"message": f"❌ Error running script: {e}"}, to=sid)
