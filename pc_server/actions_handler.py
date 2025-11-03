import socketio
from app_manager import open_app, close_app_by_name, run_script, open_in_vscode

sio = socketio.AsyncServer(async_mode="asgi")

# Map action names to app_manager functions
ACTION_MAP = {
    "open_vscode": lambda: open_app("vscode"),
    "close_vscode": lambda: close_app_by_name("Code.exe"),  # Windows process
    "open_chrome": lambda: open_app("chrome"),
    "close_chrome": lambda: close_app_by_name("chrome.exe"),
    "run_demo_script": lambda: run_script(r"C:\brothereye\demo.py"),
    "open_demo_folder": lambda: open_in_vscode(r"C:\brothereye\demo_folder"),
}

@sio.on("action_command")
async def handle_action_command(sid, data):
    action_name = data.get("action")
    if action_name in ACTION_MAP:
        result = ACTION_MAP[action_name]()
        if isinstance(result, tuple):
            _, msg = result
        else:
            msg = str(result)
    else:
        msg = f"Unknown action: {action_name}"

    await sio.emit("action_response", {"message": msg}, to=sid)
