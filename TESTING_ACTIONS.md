# Testing Action Control

## Changes Made

### 1. UI Layout Fixed
- Added 60px separator between stats and action controls
- Added "ACTION CONTROL" section header (bold, 24pt font)
- Stats section now clearly separated from action buttons
- Scroll down to see action controls

### 2. Button Connection Fixed
- Removed broken local fallback that tried to import server-side `app_manager`
- Buttons now ONLY work when connected to server via Socket.IO
- Clear error message shown if not connected: "Not connected to server. Actions require server connection."

### 3. Server Debug Logging Added
- Server now prints when it receives `action_command` events
- Server prints when it sends `action_response` back to client
- Check server console to debug action flow

## How to Test

### Step 1: Start the Server
```bash
cd c:\brothereye
# Make sure you're in the venv
uvicorn pc_server.main:sio_app --host 0.0.0.0 --port 8000
```

Watch for:
- "Database Initiated. Beginning Monitoring..."
- "Client connected: <sid>" when client connects
- "SERVER: emitting stats..." every 5 seconds

### Step 2: Start the Client
```bash
cd c:\brothereye
# IMPORTANT: Use correct URL format with //
python pi_client/main.py "http://192.168.1.5:8000"
```

**Note:** You were using `http:192.168.1.5:8000` (missing `//`). Correct format is `http://192.168.1.5:8000`.

### Step 3: Verify Connection
- Client UI should show "✓ Connected" in top-right
- Server console should print "Client connected: <sid>"
- Stats should update (CPU/RAM gauges move, readouts change)

### Step 4: Test Actions
1. Scroll down past the stats section
2. You should see "ACTION CONTROL" header
3. Click any button (e.g., "Open Chrome")
4. Check:
   - **Client log label** (bottom of UI): Should show "Sent open_app..."
   - **Server console**: Should print:
     ```
     SERVER: Received action_command from <sid>: {'action': 'open_app', 'args': {'name': 'chrome'}}
     SERVER: Sending action_response to <sid>: {'status': 'success', 'message': 'Opened app: ...'}
     ```
   - **Client log label**: Should update with server response message

### Step 5: Verify Actions Work
- "Open Chrome" → Chrome should launch
- "Close Chrome" → Chrome windows should close
- "Open VSCode" → VSCode should launch
- "Close VSCode" → VSCode should close
- "Run Demo Script" → Check if `C:\brothereye\demo.py` exists and runs

## Troubleshooting

### Buttons show "Not connected to server"
- Check client URL format: must be `http://192.168.1.5:8000` (with `//`)
- Verify server is running and accessible
- Check firewall/network settings

### Server doesn't receive action_command
- Check server console for "Received action_command" print
- Verify Socket.IO connection is established (look for "Client connected")
- Check client is using correct `sio.emit("action_command", ...)` call

### Actions don't execute
- Check `pc_server/app_manager.py` paths in `APPS` dict
- Verify Chrome/VSCode paths are correct for your system
- Check server console for error messages in action handler

### Stats overlap with actions
- This should be fixed now with separator and header
- If still overlapping, increase separator height in line 207 of `pi_client/main.py`

## File Locations
- Client: `c:\brothereye\pi_client\main.py`
- Server: `c:\brothereye\pc_server\main.py`
- App Manager: `c:\brothereye\pc_server\app_manager.py`
