from .main import sio
from .app_manager import open_app, close_app_by_name, run_script, open_in_vscode

@sio.on("action_command")
async def handle_action_command(sid, data):
    action = data.get("action")
    args = data.get("args", {})
    
    print(f"🎬 Received action: {action} with args: {args}")
    
    try:
        if action == "open_app":
            app_name = args.get("name", "")
            success, msg = open_app(app_name)
            
        elif action == "close_app":
            app_name = args.get("name", "")
            count, msg = close_app_by_name(app_name)
            success = count > 0
            
        elif action == "run_script":
            path = args.get("path", "")
            success, msg = run_script(path)
            
        elif action == "open_in_vscode":
            path = args.get("path", "")
            success, msg = open_in_vscode(path)
            
        else:
            success = False
            msg = f"❌ Unknown action: {action}"
        
        # Send response back to client
        status_icon = "✅" if success else "❌"
        await sio.emit("action_response", {
            "message": f"{status_icon} {msg}",
            "success": success
        }, to=sid)
        
        print(f"📤 Response sent: {msg}")
        
    except Exception as e:
        error_msg = f"❌ Error executing {action}: {str(e)}"
        print(error_msg)
        await sio.emit("action_response", {
            "message": error_msg,
            "success": False
        }, to=sid)