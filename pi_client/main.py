from nicegui import ui, app, run
import socketio
import threading, time
import os
from dotenv import load_dotenv
from pi_client.db_manager import init_db, insert_stats
from pi_client.realtime_anomaly import RealtimeAnomalyDetector
app.storage.general['anomaly_flag'] = False


load_dotenv()
SECRET_TOKEN = os.getenv("AUTH_TOKEN")

SERVER_URL = "http://192.168.1.15:8000"  
REFRESH_INTERVAL = 1                     

init_db()

detector = RealtimeAnomalyDetector()

sio = socketio.Client()
stats_data = {"cpu": 0, "memory": 0, "disk": 0, "gpu": 0, "battery": 0}
connection_status = "Disconnected"
latest_action_message = ""
latest_anomaly_data = None 

def connect_socket():
    global connection_status
    try:
        print("Connecting with token")
        print(f"🌐 Server URL: {SERVER_URL}")
        sio.connect(f"{SERVER_URL}?token={SECRET_TOKEN}")
        connection_status = "Connected"
    except Exception as e:
        print("Socket connection failed:", e)
        connection_status = "Disconnected"
        time.sleep(5)
        return

@sio.event
def connect():
    global connection_status
    connection_status = "✓ Connected"

@sio.event
def disconnect():
    global connection_status
    connection_status = "✗ Disconnected"

@sio.on("stats_update")
def on_stats(data):
    for k in stats_data:
        stats_data[k] = data.get(k, 0)

    cpu = data.get("cpu", 0)
    memory = data.get("memory", 0)
    disk = data.get("disk", 0)
    gpu = data.get("gpu", 0)
    battery = data.get("battery", 0)

    insert_stats(cpu=cpu, memory=memory, disk=disk, gpu=gpu, battery=battery)

    # Check for anomaly
    if detector.check(cpu, memory, disk, battery):
        print("⚠️ REAL ANOMALY DETECTED!")
        app.storage.general['anomaly_flag'] = True


        # Store anomaly data in global variable to be displayed by UI timer
        # global latest_anomaly_data
        # latest_anomaly_data = {
        #     "cpu": cpu,
        #     "memory": memory,
        #     "disk": disk,
        #     "battery": battery,
        #     "timestamp": time.strftime('%H:%M:%S')
        # }

@sio.on("action_response")
def on_action_response(data):
    global latest_action_message
    latest_action_message = data.get("message", str(data))
    print(f"Action Response Received: {latest_action_message}")

socket_started = False

def delayed_start():
    global socket_started
    if not socket_started:
        socket_started = True
        print("Starting socket connection (one-shot)")
        threading.Thread(target=connect_socket, daemon=True).start()

ui.timer(0.1, delayed_start, once=True)

# ------------- UI COMPONENTS -------------
from nicegui import app
import os

def show_anomaly_alert():
    ui.notify("⚠️ System anomaly detected!", color="red", position="top", close_button=True)

# Serve ML images folder as static
app.add_static_files('/ml', os.getcwd())

ui.page_title("BrotherEye Dashboard")
ui.colors(primary="#00ffff", secondary="#1a1a1a", accent="#ff0080")

# Enhanced Cyberpunk CSS
ui.add_head_html('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;500;700&display=swap');
    
    body {
        background: #000000 !important;
        color: #e0e0e0 !important;
        font-family: 'Rajdhani', sans-serif !important;
        overflow-x: hidden;
    }
    
    body::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            linear-gradient(135deg, rgba(0,255,255,0.03) 0%, rgba(255,0,128,0.03) 100%),
            repeating-linear-gradient(0deg, rgba(0,255,255,0.03) 0px, transparent 2px, transparent 4px, rgba(0,255,255,0.03) 6px),
            #000000;
        pointer-events: none;
        z-index: 0;
    }
    
    .q-page {
        background: transparent !important;
        position: relative;
        z-index: 1;
    }
    
    /* Speedometer Enhancements */
    .speedometer-container {
        position: relative;
        width: 320px;
        height: 320px;
        margin: 20px;
        filter: drop-shadow(0 0 30px rgba(0,255,255,0.3));
    }
    
    .speedometer {
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background: 
            radial-gradient(circle at 30% 30%, rgba(0,255,255,0.1), transparent),
            radial-gradient(circle at 70% 70%, rgba(255,0,128,0.1), transparent),
            radial-gradient(circle at 50% 50%, #0a0a0a, #000000);
        box-shadow: 
            0 0 40px rgba(0,255,255,0.4) inset,
            0 0 60px rgba(255,0,128,0.2) inset,
            0 8px 32px rgba(0,0,0,0.9),
            0 0 80px rgba(0,255,255,0.15);
        position: relative;
        border: 2px solid rgba(0,255,255,0.3);
        animation: pulse-border 3s ease-in-out infinite;
    }
    
    @keyframes pulse-border {
        0%, 100% { border-color: rgba(0,255,255,0.3); }
        50% { border-color: rgba(0,255,255,0.6); }
    }
    
    .speedometer-ticks {
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
    }
    
    .speedometer-needle {
        position: absolute;
        width: 5px;
        height: 48%;
        background: linear-gradient(to top, #00ffff, #00ffff, rgba(0,255,255,0.5));
        bottom: 50%;
        left: 50%;
        transform-origin: bottom center;
        transform: translateX(-50%) rotate(-135deg);
        transition: transform 0.5s cubic-bezier(0.4, 0.0, 0.2, 1);
        box-shadow: 0 0 20px rgba(0,255,255,1), 0 0 40px rgba(0,255,255,0.5);
        border-radius: 3px 3px 0 0;
        filter: drop-shadow(0 0 10px rgba(0,255,255,0.8));
    }
    
    .speedometer-center {
        position: absolute;
        width: 40px;
        height: 40px;
        background: radial-gradient(circle, #00ffff, #008b8b);
        border-radius: 50%;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        box-shadow: 
            0 0 30px rgba(0,255,255,1),
            0 0 60px rgba(0,255,255,0.5),
            0 0 20px rgba(0,255,255,0.8) inset;
        border: 3px solid rgba(0,255,255,0.5);
        animation: glow-center 2s ease-in-out infinite;
    }
    
    @keyframes glow-center {
        0%, 100% { box-shadow: 0 0 30px rgba(0,255,255,1), 0 0 60px rgba(0,255,255,0.5); }
        50% { box-shadow: 0 0 50px rgba(0,255,255,1), 0 0 100px rgba(0,255,255,0.7); }
    }
    
    .speedometer-value {
        position: absolute;
        bottom: 35%;
        left: 50%;
        transform: translateX(-50%);
        font-size: 42px;
        font-weight: 900;
        color: #00ffff;
        text-shadow: 
            0 0 20px rgba(0,255,255,1),
            0 0 40px rgba(0,255,255,0.5),
            0 2px 4px rgba(0,0,0,0.8);
        font-family: 'Orbitron', monospace;
        letter-spacing: 2px;
    }
    
    .speedometer-label {
        position: absolute;
        bottom: 22%;
        left: 50%;
        transform: translateX(-50%);
        font-size: 18px;
        font-weight: 700;
        color: rgba(0,255,255,0.7);
        text-transform: uppercase;
        letter-spacing: 4px;
        text-shadow: 0 0 10px rgba(0,255,255,0.5);
    }
    
    /* Memory Speedometer - Pink Theme */
    .mem-speedometer-needle {
        background: linear-gradient(to top, #ff0080, #ff0080, rgba(255,0,128,0.5)) !important;
        box-shadow: 0 0 20px rgba(255,0,128,1), 0 0 40px rgba(255,0,128,0.5) !important;
        filter: drop-shadow(0 0 10px rgba(255,0,128,0.8)) !important;
    }
    
    .mem-speedometer-center {
        background: radial-gradient(circle, #ff0080, #8b0045) !important;
        box-shadow: 
            0 0 30px rgba(255,0,128,1),
            0 0 60px rgba(255,0,128,0.5),
            0 0 20px rgba(255,0,128,0.8) inset !important;
        border: 3px solid rgba(255,0,128,0.5) !important;
    }
    
    .mem-speedometer-value {
        color: #ff0080 !important;
        text-shadow: 
            0 0 20px rgba(255,0,128,1),
            0 0 40px rgba(255,0,128,0.5),
            0 2px 4px rgba(0,0,0,0.8) !important;
    }
    
    .mem-speedometer-label {
        color: rgba(255,0,128,0.7) !important;
        text-shadow: 0 0 10px rgba(255,0,128,0.5) !important;
    }
    
    /* Card Styling */
    .cyber-card {
        background: linear-gradient(145deg, rgba(10,10,10,0.95), rgba(5,5,5,0.98)) !important;
        border: 1px solid rgba(0,255,255,0.3) !important;
        box-shadow: 
            0 8px 32px rgba(0,0,0,0.8),
            0 0 20px rgba(0,255,255,0.1) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(10px) !important;
        position: relative;
        overflow: hidden;
    }
    
    .cyber-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0,255,255,0.1), transparent);
        animation: scan 3s infinite;
    }
    
    @keyframes scan {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    /* Fuel Gauge Enhancement - Horizontal Bar */
    .fuel-container {
        background: #041014 !important;
        border: 2px solid rgba(0,255,255,0.4) !important;
        width: 100%;
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    
.fuel-gauge {
    background: #041014 !important;
    width: 100%;
    height: 60px;
    border-radius: 30px;
    position: relative;
    overflow: hidden;
    box-shadow:
        0 0 20px rgba(0,255,255,0.3),
        inset 0 0 20px rgba(0,255,255,0.4);
}

/* The fill bar */
.fuel-fill {
    position: absolute;
    top: 0;
    left: 0;                      /* <<— IMPORTANT: Make it fill left → right */
    height: 100%;
    width: 100%;                  /* JS will adjust this */
    
    background: linear-gradient(
        90deg,
        #ff0044 0%,
        #ff0080 20%,
        #ffaa00 45%,
        #00ffff 70%,
        #00ff88 100%
    );

    border-radius: 30px;
    box-shadow:
        0 0 25px rgba(0,255,255,0.6),
        0 0 40px rgba(0,255,255,0.3);

    transition: width 0.6s cubic-bezier(0.4,0.0,0.2,1);
}   
    @keyframes flow {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }
    
    .fuel-fill::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(to bottom, rgba(255,255,255,0.2), transparent);
        border-radius: 28px;
    }
    
    /* Digital Display */
    .digital-display {
        background: rgba(0,0,0,0.9) !important;
        border: 2px solid rgba(0,255,255,0.4) !important;
        box-shadow: 
            0 0 30px rgba(0,255,255,0.2) inset,
            0 0 20px rgba(0,255,255,0.1) !important;
        font-family: 'Orbitron', monospace !important;
        color: #00ffff !important;
        text-shadow: 0 0 15px rgba(0,255,255,0.8) !important;
        position: relative;
    }
    
    .digital-display::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(0,255,255,0.5), transparent);
        animation: scan-line 2s linear infinite;
    }
    
    @keyframes scan-line {
        0% { transform: translateY(0); opacity: 0; }
        50% { opacity: 1; }
        100% { transform: translateY(50px); opacity: 0; }
    }
    
    /* Action Buttons */
    .action-btn {
        background: rgba(0,0,0,0.8) !important;
        border: 2px solid rgba(0,255,255,0.4) !important;
        transition: all 0.3s ease !important;
        position: relative;
        overflow: hidden;
    }
    
    .action-btn:hover {
        border-color: rgba(0,255,255,0.8) !important;
        box-shadow: 
            0 0 20px rgba(0,255,255,0.4),
            0 0 40px rgba(0,255,255,0.2) !important;
        transform: translateY(-2px) scale(1.05);
    }
    
    .action-btn::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(0,255,255,0.2);
        transform: translate(-50%, -50%);
        transition: width 0.3s, height 0.3s;
    }
    
    .action-btn:hover::before {
        width: 200%;
        height: 200%;
    }
    
    /* ML Analysis Box */
    .ml-output {
        background: rgba(0,0,0,0.95) !important;
        border: 2px solid rgba(255,0,128,0.4) !important;
        box-shadow: 
            0 0 30px rgba(255,0,128,0.2) inset,
            0 8px 32px rgba(0,0,0,0.8) !important;
        font-family: 'Rajdhani', monospace !important;
        color: #00ffff !important;
        min-height: 200px;
        position: relative;
        overflow: auto;
    }
    
    .ml-output::before {
        content: '>';
        position: absolute;
        left: 10px;
        top: 10px;
        color: #ff0080;
        font-weight: bold;
        animation: blink 1s infinite;
    }
    
    @keyframes blink {
        0%, 49% { opacity: 1; }
        50%, 100% { opacity: 0; }
    }
    
    /* Header Enhancements */
    .cyber-header {
        background: rgba(0,0,0,0.95) !important;
        border-bottom: 2px solid rgba(0,255,255,0.4) !important;
        box-shadow: 0 4px 30px rgba(0,255,255,0.2) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .glitch {
        animation: glitch 3s infinite;
    }
    
    @keyframes glitch {
        0%, 90%, 100% { transform: translate(0); }
        91% { transform: translate(-2px, 2px); }
        92% { transform: translate(2px, -2px); }
        93% { transform: translate(-2px, 2px); }
        94% { transform: translate(2px, -2px); }
    }
    
    /* Metric Labels */
    .metric-label {
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 3px;
        color: rgba(0,255,255,0.6);
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    
    /* Button Icons */
    .btn-icon {
        width: 32px;
        height: 32px;
        filter: drop-shadow(0 0 8px currentColor);
    }
</style>
''')

# Header with cyberpunk styling
with ui.header().classes("cyber-header"):
    with ui.row().classes("w-full justify-between items-center p-4"):
        ui.label("🧿 BROTHEREYE").classes("text-4xl font-bold tracking-widest glitch").style(
            "color: #00ffff; text-shadow: 0 0 20px rgba(0,255,255,0.8), 2px 2px 0 #ff0080; font-family: 'Orbitron', monospace;"
        )
        status_label = ui.label(connection_status).classes("text-lg font-semibold px-6 py-2 rounded-lg").style(
            "background: rgba(0,0,0,0.8); border: 2px solid rgba(0,255,255,0.4);"
        )

# Main speedometers section
with ui.row().classes("justify-center items-center w-full mt-8 mb-4"):
    # CPU Speedometer
    with ui.column().classes("items-center"):
        cpu_speedometer = ui.html(content='''
            <div class="speedometer-container">
                <div class="speedometer">
                    <svg class="speedometer-ticks" viewBox="0 0 320 320">
                        <circle cx="160" cy="160" r="130" fill="none" stroke="rgba(0,255,255,0.2)" stroke-width="1"/>
                        <circle cx="160" cy="160" r="120" fill="none" stroke="#00ffff" stroke-width="1" opacity="0.3" 
                                stroke-dasharray="5 10"/>
                        <circle cx="160" cy="160" r="110" fill="none" stroke="rgba(0,255,255,0.1)" stroke-width="1"/>
                    </svg>
                    <div class="speedometer-needle" id="cpu-needle"></div>
                    <div class="speedometer-center"></div>
                    <div class="speedometer-value" id="cpu-value">0%</div>
                    <div class="speedometer-label">CPU</div>
                </div>
            </div>
        ''', sanitize=False)
    
    # Memory Speedometer
    with ui.column().classes("items-center"):
        mem_speedometer = ui.html(content='''
            <div class="speedometer-container">
                <div class="speedometer" style="border-color: rgba(255,0,128,0.3);">
                    <svg class="speedometer-ticks" viewBox="0 0 320 320">
                        <circle cx="160" cy="160" r="130" fill="none" stroke="rgba(255,0,128,0.2)" stroke-width="1"/>
                        <circle cx="160" cy="160" r="120" fill="none" stroke="#ff0080" stroke-width="1" opacity="0.3" 
                                stroke-dasharray="5 10"/>
                        <circle cx="160" cy="160" r="110" fill="none" stroke="rgba(255,0,128,0.1)" stroke-width="1"/>
                    </svg>
                    <div class="speedometer-needle mem-speedometer-needle" id="mem-needle"></div>
                    <div class="speedometer-center mem-speedometer-center"></div>
                    <div class="speedometer-value mem-speedometer-value" id="mem-value">0%</div>
                    <div class="speedometer-label mem-speedometer-label">MEMORY</div>
                </div>
            </div>
        ''', sanitize=False)

# Battery Fuel Gauge - Full Width Horizontal Bar
with ui.column().classes("w-full items-center mt-8"):
    with ui.card().classes("cyber-card p-8 w-full").style("max-width: 1400px;"):
        ui.label("Power").classes("text-2xl font-bold text-center mb-2").style(
            "color: #00ffff; font-family: 'Orbitron', monospace; text-shadow: 0 0 10px rgba(0,255,255,0.8);"
        )
        battery_label = ui.label("---%").classes("text-4xl font-bold text-center mb-4").style(
            "color: #00ffff; font-family: 'Orbitron', monospace; text-shadow: 0 0 20px rgba(0,255,255,0.8);"
        )
        with ui.row().classes("fuel-container"):
            battery_gauge = ui.html(content='<div class="fuel-gauge"><div class="fuel-fill" id="battery-fill" style="width: 0%"></div></div>', sanitize=False)

# Digital displays for other metrics - Centered beneath fuel gauge
with ui.row().classes("justify-center gap-8 mt-4 px-8 w-full"):
    with ui.card().classes("cyber-card p-6 text-center").style("min-width: 250px;"):
        ui.label("DISK USAGE").classes("metric-label")
        disk_label = ui.label("---%").classes("text-4xl font-bold digital-display p-4 rounded")
    
    with ui.card().classes("cyber-card p-6 text-center").style("min-width: 250px;"):
        ui.label("GPU LOAD").classes("metric-label")
        gpu_label = ui.label("---%").classes("text-4xl font-bold digital-display p-4 rounded")

ui.separator().classes("my-12").style("background: linear-gradient(90deg, transparent, rgba(0,255,255,0.4), transparent); height: 2px;")

# ------------- ACTION BUTTONS - CENTERED -------------
with ui.column().classes("w-full items-center"):
    with ui.card().classes("cyber-card p-8 mt-4").style("max-width: 1400px; width: 100%;"):
        ui.label("Action Control").classes("text-3xl font-bold text-center mb-8").style(
            "color: #00ffff; font-family: 'Orbitron', monospace; text-shadow: 0 0 15px rgba(0,255,255,0.8);"
        )
        
        def send_action(action, args={}):
            if sio.connected:
                sio.emit("action_command", {"action": action, "args": args})
                ui.notify(f"Sent {action}", color="green")
            else:
                ui.notify("Not connected to server", color="red")
        
        with ui.row().classes("justify-center items-center gap-10 flex-wrap w-full text-center"):
            # Chrome Open
            with ui.column().classes("items-center text-center"):

                ui.button(on_click=lambda: send_action("open_app", {"name": "chrome"})) \
                    .props('flat size="xl"').classes("action-btn").style("width: 100px; height: 100px;")
                ui.html('''
                    <svg class="btn-icon" style="color: #4285f4; margin-top: -90px; pointer-events: none;" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm0 2c5.523 0 10 4.477 10 10s-4.477 10-10 10S2 17.523 2 12 6.477 2 12 2zm0 3a7 7 0 1 0 0 14 7 7 0 0 0 0-14zm0 2a5 5 0 1 1 0 10 5 5 0 0 1 0-10z"/>
                    </svg>
                ''', sanitize=False)
                ui.label("Open Chrome").classes("text-sm mt-2").style("color: rgba(0,255,255,0.7);")
            
            # Chrome Close
            with ui.column().classes("items-center text-center"):
                ui.button(on_click=lambda: send_action("close_app", {"name": "chrome"})) \
                    .props('flat size="xl"').classes("action-btn").style("width: 100px; height: 100px;")
                ui.html('''
                    <svg class="btn-icon" style="color: #ff0080; margin-top: -90px; pointer-events: none;" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                    </svg>
                ''', sanitize=False)
                ui.label("Close Chrome").classes("text-sm mt-2").style("color: rgba(255,0,128,0.7);")
            
            # VSCode Open
            with ui.column().classes("items-center text-center"):
                ui.button(on_click=lambda: send_action("open_app", {"name": "vscode"})) \
                    .props('flat size="xl"').classes("action-btn").style("width: 100px; height: 100px;")
                ui.html('''
                    <svg class="btn-icon" style="color: #007acc; margin-top: -90px; pointer-events: none;" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M17.5 0l-12.5 8.5L0 6v12l5 -2.5L17.5 24l6.5-3V3L17.5 0zM17.5 4.5v15L7.5 12L17.5 4.5z"/>
                    </svg>
                ''', sanitize=False)
                ui.label("Open VSCode").classes("text-sm mt-2").style("color: rgba(0,255,255,0.7);")
            
            # VSCode Close
            with ui.column().classes("items-center text-center"):
                ui.button(on_click=lambda: send_action("close_app", {"name": "Code.exe"})) \
                    .props('flat size="xl"').classes("action-btn").style("width: 100px; height: 100px;")
                ui.html('''
                    <svg class="btn-icon" style="color: #ff0080; margin-top: -90px; pointer-events: none;" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                    </svg>
                ''', sanitize=False)
                ui.label("Close VSCode").classes("text-sm mt-2").style("color: rgba(255,0,128,0.7);")
            
            # Run Python Script
            with ui.column().classes("items-center text-center"):
                ui.button(on_click=lambda: send_action("run_script", {"path": r"C:\brothereye\demo.py"})) \
                    .props('flat size="xl"').classes("action-btn").style("width: 100px; height: 100px;")
                ui.html('''
                    <svg class="btn-icon" style="color: #00ff88; margin-top: -90px; pointer-events: none;" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M8 5v14l11-7z"/>
                    </svg>
                ''', sanitize=False)
                ui.label("Run Demo.py").classes("text-sm mt-2").style("color: rgba(0,255,136,0.7);")

ui.separator().classes("my-12").style("background: linear-gradient(90deg, transparent, rgba(255,0,128,0.4), transparent); height: 2px;")

# ------------- ML SECTION - CENTERED -------------
import time

with ui.column().classes("w-full items-center text-center"):
    with ui.card().classes("cyber-card p-8").style("max-width: 1400px; width: 100%;"):
        ui.label("Analysis and Prediction").classes("text-3xl font-bold text-center mb-6").style(
            "color: #ff0080; font-family: 'Orbitron', monospace; text-shadow: 0 0 15px rgba(255,0,128,0.8);"
        )
        
        ml_result_label = ui.label("█ SYSTEM READY FOR ANALYSIS...\n█ Awaiting command execution...").classes("text-lg p-6 rounded ml-output").style(
            "white-space: pre-wrap; line-height: 1.8; font-size: 18px; padding-left: 40px;"
        )
        
        from pi_client.ml_analysis import run_local_ml
        
        def run_ml_local():
            ml_result_label.text = "█ INITIALIZING ML...\n█ Running analysis..."
            summary, plots = run_local_ml()
            ml_result_label.text = summary

            for plot in plots:
                if os.path.exists(plot):
                    cache_buster = int(time.time())
                    ui.image(f"/ml/{plot}?v={cache_buster}")

        ui.button("▶ RUN ML ANALYSIS", on_click=run_ml_local) \
            .props('outline size="xl"') \
            .classes("block mx-auto mt-6 font-bold action-btn") \
            .style(
                "font-family: 'Orbitron', monospace; letter-spacing: 3px; padding: 16px 48px; "
                "font-size: 18px; border-color: rgba(255,0,128,0.6); color: #ff0080;"
            )
    
# ------------- AUTO-UPDATES -------------
def check_anomaly_flag():
    if app.storage.general.get('anomaly_flag'):
        ui.notify("⚠️ System anomaly detected!",
                  color="red",
                  position="top",
                  close_button=True)
        app.storage.general['anomaly_flag'] = False  # reset flag

ui.timer(0.2, check_anomaly_flag)

def refresh_ui():
    status_label.text = connection_status
    status_color = "#00ff88" if "Connected" in connection_status else "#ff0080"
    status_label.style(f"background: rgba(0,0,0,0.8); border: 2px solid {status_color}; color: {status_color}; box-shadow: 0 0 20px {status_color}40;")
    
    cpu_percent = stats_data["cpu"]
    mem_percent = stats_data["memory"]
    
    cpu_rotation = -135 + (cpu_percent * 2.7) 
    mem_rotation = -135 + (mem_percent * 2.7)
    
    ui.run_javascript(f'''
        const cpuNeedle = document.getElementById('cpu-needle');
        const cpuValue = document.getElementById('cpu-value');
        if (cpuNeedle) cpuNeedle.style.transform = 'translateX(-50%) rotate({cpu_rotation}deg)';
        if (cpuValue) cpuValue.textContent = '{cpu_percent:.0f}%';
    ''')
    
    ui.run_javascript(f'''
        const memNeedle = document.getElementById('mem-needle');
        const memValue = document.getElementById('mem-value');
        if (memNeedle) memNeedle.style.transform = 'translateX(-50%) rotate({mem_rotation}deg)';
        if (memValue) memValue.textContent = '{mem_percent:.0f}%';
    ''')
    
    disk_label.text = f"{stats_data['disk']:.1f}%"
    gpu_label.text = f"{stats_data['gpu']:.1f}%"
    battery_percent = stats_data['battery']
    battery_label.text = f"{battery_percent}%"

    ui.run_javascript(f'''
        const batteryFill = document.getElementById('battery-fill');
        if (batteryFill) batteryFill.style.width = '{battery_percent}%';
    ''')
def update_anomaly_notifications():
    global latest_anomaly_data
    if latest_anomaly_data:
        # Show UI notification
        ui.notify(
            f"⚠️ ANOMALY: CPU={latest_anomaly_data['cpu']:.0f}% MEM={latest_anomaly_data['memory']:.0f}%",
            color="negative",
            position="top",
            timeout=10000,
            type="negative"
        )
        
        # Update ML output box
        ml_result_label.text = (
            f"█ ⚠️ ANOMALY DETECTED!\n"
            f"█ CPU: {latest_anomaly_data['cpu']:.1f}% | Memory: {latest_anomaly_data['memory']:.1f}%\n"
            f"█ Disk: {latest_anomaly_data['disk']:.1f}% | Battery: {latest_anomaly_data['battery']:.1f}%\n"
            f"█ Time: {latest_anomaly_data['timestamp']}"
        )
        
        latest_anomaly_data = None


def update_action_notifications():
    global latest_action_message
    if latest_action_message:
        ui.notify(latest_action_message, color="blue")
        latest_action_message = ""

ui.timer(REFRESH_INTERVAL, refresh_ui)
ui.timer(0.5, update_action_notifications)
ui.timer(0.5, update_anomaly_notifications)

ui.run(reload=False, port=8080)
