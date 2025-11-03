import socketio

sio = socketio.Client()

@sio.event
def connect():
    print("Connected to server!")

@sio.event
def disconnect():
    print("Disconnected from server!")

@sio.on("stats_update")
def on_stats(data):
    print("Stats from server:", data)

sio.connect("http://localhost:8000")
sio.wait()
