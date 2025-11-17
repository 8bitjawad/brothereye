# import time
# import asyncio
# from contextlib import asynccontextmanager
# from fastapi import FastAPI
# import socketio
# from .system_monitor import get_system_stats
# from dotenv import load_dotenv
# import os

# # Load env from pc_server/.env
# BASE_DIR = os.path.dirname(__file__)
# ENV_PATH = os.path.join(BASE_DIR, ".env")
# load_dotenv(ENV_PATH)

# SECRET_TOKEN = os.getenv("AUTH_TOKEN")

# # Create single socket instance
# sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# # Import handlers (AFTER sio is created)
# from . import actions_handler

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     asyncio.create_task(monitor_loop())
#     print("Monitoring loop started...")
#     yield
#     print("Server shutting down...")

# app = FastAPI(lifespan=lifespan)
# sio_app = socketio.ASGIApp(sio, app)

# async def monitor_loop():
#     while True:
#         stats = get_system_stats()
#         print("SERVER: emitting stats...", stats)
#         await sio.emit("stats_update", stats)
#         await asyncio.sleep(5)

# @sio.event
# async def connect(sid, environ):
#     query = environ.get("QUERY_STRING", "")
#     params = dict(q.split("=") for q in query.split("&") if "=" in q)
#     token = params.get("token")

#     if token != SECRET_TOKEN:
#         print(f"❌ Unauthorized connection {sid}")
#         await sio.disconnect(sid)
#         return False

#     print(f"✓ Client {sid} authorized")
#     return True

# @sio.event
# async def disconnect(sid):
#     print(f"Client disconnected: {sid}")

# @app.get("/api/usage")
# async def status():
#     return {"message": "Monitoring active (no server-side DB)"}

# @sio.on("action_command")
# async def handle_action(sid, data):
#     action = data.get("action")
#     args = data.get("args", {})
#     if action == "run_script":
#         path = args.get("path")
#         try:
#             result = subprocess.run(["python", path], capture_output=True, text=True)
#             output = result.stdout.strip() or "No output"
#             await sio.emit("action_response", {"message": f"✅ Script executed successfully:\n{output}"}, to=sid)
#         except Exception as e:
#             await sio.emit("action_response", {"message": f"❌ Error running script: {e}"}, to=sid)

import time
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
import socketio
from .system_monitor import get_system_stats
from dotenv import load_dotenv
import os

# Load env from pc_server/.env
BASE_DIR = os.path.dirname(__file__)
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

SECRET_TOKEN = os.getenv("AUTH_TOKEN")

# Create single socket instance
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# Import handlers (AFTER sio is created)
from . import actions_handler

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(monitor_loop())
    print("Monitoring loop started...")
    yield
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
    params = dict(q.split("=") for q in query.split("&") if "=" in q)
    token = params.get("token")

    if token != SECRET_TOKEN:
        print(f"❌ Unauthorized connection {sid}")
        await sio.disconnect(sid)
        return False

    print(f"✓ Client {sid} authorized")
    return True

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@app.get("/api/usage")
async def status():
    return {"message": "Monitoring active"}

# ❌ REMOVE THIS - duplicate handler
# @sio.on("action_command")
# async def handle_action(sid, data):
#     ...