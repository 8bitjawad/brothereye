import json
import os
import math
import threading
import time

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.graphics import Color, Line, Rectangle, Ellipse
from kivy.core.text import Label as CoreLabel
from kivy.core.window import Window

import socketio

# ----------------------------
# Config Loader
# ----------------------------
def load_config(config_path="config.json"):
    if not os.path.exists(config_path):
        return {
            "server": {"host": "127.0.0.1", "port": 8000, "protocol": "http"},
            "ui": {"theme": "dark", "update_interval": 1, "fullscreen": True}
        }
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except:
        return {
            "server": {"host": "127.0.0.1", "port": 8000, "protocol": "http"},
            "ui": {"theme": "dark", "update_interval": 1, "fullscreen": True}
        }

config = load_config()
server_config = config['server']
server_url = f"{server_config['protocol']}://{server_config['host']}:{server_config['port']}"

# Set window background
Window.clearcolor = (0, 0, 0, 1)

# ----------------------------
# Speedometer Widget
# ----------------------------
class Speedometer(Widget):
    value = NumericProperty(0)
    max_value = NumericProperty(100)
    label = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas, value=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.clear()
        size = min(self.width, self.height)
        radius = size * 0.35
        cx, cy = self.center_x, self.center_y
        start_angle = 220
        end_angle = -40
        total_range = start_angle - end_angle
        progress = min(self.value / self.max_value, 1.0)
        needle_angle = start_angle - (progress * total_range)

        with self.canvas:
            Color(1, 1, 1, 0.3)
            Line(circle=(cx, cy, radius + 5, start_angle, end_angle), width=2)

            Color(1, 1, 1, 0.5)
            for i in range(0, 11):
                tick_progress = i / 10.0
                tick_angle = start_angle - (tick_progress * total_range)
                tick_rad = math.radians(tick_angle)
                x1 = cx + (radius + 10) * math.cos(tick_rad)
                y1 = cy + (radius + 10) * math.sin(tick_rad)
                inner_radius = radius - 5 if i % 2 == 0 else radius
                tick_width = 2 if i % 2 == 0 else 1
                x2 = cx + inner_radius * math.cos(tick_rad)
                y2 = cy + inner_radius * math.sin(tick_rad)
                Line(points=[x1, y1, x2, y2], width=tick_width)

            danger_start = start_angle - (0.8 * total_range)
            Color(1, 0, 0, 0.3)
            Line(circle=(cx, cy, radius, danger_start, end_angle), width=8)
            Color(1, 1, 1, 0.2)
            Line(circle=(cx, cy, radius, start_angle, danger_start), width=8)

            Color(1, 0, 0, 1) if self.value >= 80 else Color(1, 1, 1, 1)
            needle_rad = math.radians(needle_angle)
            needle_length = radius - 10
            x_end = cx + needle_length * math.cos(needle_rad)
            y_end = cy + needle_length * math.sin(needle_rad)
            Line(points=[cx, cy, x_end, y_end], width=3)
            Color(1, 0, 0, 1)
            Ellipse(pos=(cx - 5, cy - 5), size=(10, 10))

        # Add percentage labels at key positions (0, 25, 50, 75, 100)
        from kivy.graphics import PushMatrix, PopMatrix, Rotate, Translate
        label_positions = [(0, "0"), (0.25, "25"), (0.5, "50"), (0.75, "75"), (1.0, "100")]
        for progress, text in label_positions:
            angle = start_angle - (progress * total_range)
            angle_rad = math.radians(angle)
            label_distance = radius + 25
            label_x = cx + label_distance * math.cos(angle_rad)
            label_y = cy + label_distance * math.sin(angle_rad)
            
            label = CoreLabel(text=text, font_size=12)
            label.refresh()
            texture = label.texture
            with self.canvas:
                Color(1, 1, 1, 0.8)
                Rectangle(texture=texture, pos=(label_x - texture.width/2, label_y - texture.height/2), size=texture.size)

        # Center value display
        center_label = CoreLabel(text=f"{int(self.value)}%", font_size=20, bold=True)
        center_label.refresh()
        center_texture = center_label.texture
        with self.canvas:
            Color(1, 1, 1, 1)
            Rectangle(texture=center_texture, pos=(cx - center_texture.width/2, cy - radius/2), size=center_texture.size)

# ----------------------------
# Fuel Gauge Widget
# ----------------------------
class FuelGauge(Widget):
    value = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas, value=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.clear()
        bar_width = self.width * 0.8
        bar_height = 40
        bar_x = self.center_x - bar_width / 2
        bar_y = self.center_y - bar_height / 2

        with self.canvas:
            Color(1, 1, 1, 0.5)
            Line(rectangle=(bar_x, bar_y, bar_width, bar_height), width=2)
            Color(0.1, 0.1, 0.1, 1)
            Rectangle(pos=(bar_x + 2, bar_y + 2), size=(bar_width - 4, bar_height - 4))
            fill_width = (bar_width - 8) * (self.value / 100)
            if self.value < 20:
                Color(1, 0, 0, 1)
            elif self.value < 50:
                Color(1, 1, 0, 1)
            else:
                Color(1, 1, 1, 1)
            Rectangle(pos=(bar_x + 4, bar_y + 4), size=(fill_width, bar_height - 8))

# ----------------------------
# Digital Readout Widget
# ----------------------------
class DigitalReadout(BoxLayout):
    name = StringProperty("")
    value = StringProperty("--")
    unit = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.name_label = Label(text=self.name, font_size=14, color=[0.7,0.7,0.7,1], size_hint_y=0.3)
        self.value_label = Label(text=f"{self.value} {self.unit}", font_size=28, bold=True, color=[1,1,1,1], size_hint_y=0.7)
        self.add_widget(self.name_label)
        self.add_widget(self.value_label)

    def update(self, value, unit=None):
        self.value = f"{value:.1f}" if isinstance(value,(int,float)) else str(value)
        if unit: self.unit = unit
        self.value_label.text = f"{self.value} {self.unit}"

# ----------------------------
# Dashboard Screen (Scrollable)
# ----------------------------
class DashboardScreen(BoxLayout):
    connection_status = StringProperty("Disconnected")
    last_update = StringProperty("Never")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10

        # ScrollView
        scroll = ScrollView(size_hint=(1,1))
        self.scroll_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=20)
        self.scroll_layout.bind(minimum_height=self.scroll_layout.setter('height'))
        scroll.add_widget(self.scroll_layout)
        self.add_widget(scroll)

        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        self.title_label = Label(
            text="[b]BROTHER EYE[/b]",
            markup=True,
            font_size=32,
            size_hint_x=0.7,
            color=[1, 0, 0, 1],  # Red color
            halign='left',
            valign='middle'
        )
        self.title_label.bind(size=self.title_label.setter('text_size'))
        self.status_label = Label(text=self.connection_status, font_size=16, size_hint_x=0.3)
        header.add_widget(self.title_label)
        header.add_widget(self.status_label)
        self.scroll_layout.add_widget(header)

        # Speedometers with labels
        speed_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=280, spacing=40)
        
        # CPU Speedometer
        cpu_box = BoxLayout(orientation='vertical', spacing=5)
        self.cpu_speedometer = Speedometer(label="CPU")
        cpu_label = Label(text="[b]CPU[/b]", markup=True, font_size=18, size_hint_y=None, height=30)
        cpu_box.add_widget(self.cpu_speedometer)
        cpu_box.add_widget(cpu_label)
        speed_container.add_widget(cpu_box)
        
        # RAM Speedometer
        ram_box = BoxLayout(orientation='vertical', spacing=5)
        self.ram_speedometer = Speedometer(label="RAM")
        ram_label = Label(text="[b]RAM[/b]", markup=True, font_size=18, size_hint_y=None, height=30)
        ram_box.add_widget(self.ram_speedometer)
        ram_box.add_widget(ram_label)
        speed_container.add_widget(ram_box)
        
        self.scroll_layout.add_widget(speed_container)

        # Battery Gauge with label
        battery_container = BoxLayout(orientation='vertical', size_hint_y=None, height=100, spacing=5)
        battery_label = Label(text="[b]BATTERY[/b]", markup=True, font_size=16, size_hint_y=None, height=25)
        battery_container.add_widget(battery_label)
        self.fuel_gauge = FuelGauge()
        battery_container.add_widget(self.fuel_gauge)
        self.scroll_layout.add_widget(battery_container)

        # Digital Readouts
        readouts = GridLayout(cols=3, spacing=20, size_hint_y=None, height=100)
        self.gpu_readout = DigitalReadout(name="GPU", unit="%")
        self.disk_readout = DigitalReadout(name="DISK", unit="%")
        self.ram_readout = DigitalReadout(name="MEMORY", unit="%")
        readouts.add_widget(self.gpu_readout)
        readouts.add_widget(self.disk_readout)
        readouts.add_widget(self.ram_readout)
        self.scroll_layout.add_widget(readouts)

        # Separator between stats and actions
        separator = BoxLayout(size_hint_y=None, height=100)
        self.scroll_layout.add_widget(separator)

        # Action Control Section Header
        action_header = Label(
            text="[b]ACTION CONTROL[/b]",
            markup=True,
            font_size=24,
            size_hint_y=None,
            height=60
        )
        self.scroll_layout.add_widget(action_header)

        # Action Buttons Section
        self.action_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=[20, 10, 20, 10])
        self.scroll_layout.add_widget(self.action_layout)

        self.add_action_button("Open Chrome", "open_app", {"name":"chrome"})
        self.add_action_button("Close Chrome", "close_app", {"name":"chrome"})
        self.add_action_button("Open VSCode", "open_app", {"name":"vscode"})
        self.add_action_button("Close VSCode", "close_app", {"name":"Code.exe"})
        self.add_action_button("Run Demo Script", "run_script", {"path": r"C:\brothereye\demo.py"})

        # Log Label
        self.log_label = Label(text="", size_hint_y=None, height=40)
        self.scroll_layout.add_widget(self.log_label)

        # ML Placeholder
        self.ml_placeholder = Label(text="Future ML Models will appear here", size_hint_y=None, height=150)
        self.scroll_layout.add_widget(self.ml_placeholder)

        # Bind properties
        self.bind(connection_status=self.update_status)
        self.bind(last_update=lambda i,v: setattr(self.log_label,'text',f"Last Update: {v}"))

    def add_action_button(self, text, action, args):
        btn = Button(text=text, size_hint_y=None, height=50)
        btn.bind(on_press=lambda x: self.send_action(action,args))
        self.action_layout.add_widget(btn)

    def send_action(self, action, args={}):
        # Send command to server via Socket.IO
        if hasattr(self, 'app') and self.app.sio.connected:
            self.app.sio.emit("action_command", {"action":action,"args":args})
            self.log_label.text = f"Sent {action}..."
        else:
            self.log_label.text = "Not connected to server. Actions require server connection."

    def update_status(self, instance, value):
        self.status_label.text = value
        self.status_label.color = [0,1,0,1] if "Connected" in value else [1,0,0,1]

# ----------------------------
# Main App
# ----------------------------
class BrotherEyeApp(App):
    def __init__(self, server_url="http://localhost:8000", **kwargs):
        super().__init__(**kwargs)
        self.server_url = server_url
        self.sio = socketio.Client()
        self.setup_socketio()

    def build(self):
        self.dashboard = DashboardScreen()
        self.dashboard.app = self  # give dashboard access to self
        return self.dashboard

    def setup_socketio(self):
        @self.sio.event
        def connect():
            Clock.schedule_once(lambda dt: setattr(self.dashboard,'connection_status','✓ Connected'),0)
        @self.sio.event
        def disconnect():
            Clock.schedule_once(lambda dt: setattr(self.dashboard,'connection_status','✗ Disconnected'),0)
        @self.sio.on("stats_update")
        def on_stats(data):
            Clock.schedule_once(lambda dt: self.update_dashboard(data),0)
        @self.sio.on("action_response")
        def on_action_response(data):
            Clock.schedule_once(
                lambda dt: setattr(
                    self.dashboard.log_label,
                    'text',
                    data.get('message', str(data)) if isinstance(data, dict) else str(data)
                ),
                0
            )

    def update_dashboard(self,data):
        self.dashboard.cpu_speedometer.value = data.get('cpu',0)
        ram_percent = data.get('memory',0)
        self.dashboard.ram_speedometer.value = ram_percent
        self.dashboard.ram_readout.update(ram_percent,"%")
        self.dashboard.disk_readout.update(data.get('disk',0),"%")
        self.dashboard.gpu_readout.update(data.get('gpu',0),"%")
        self.dashboard.fuel_gauge.value = data.get('battery',0)
        self.dashboard.last_update = time.strftime("%H:%M:%S")

    def on_start(self):
        threading.Thread(target=self.connect_to_server, daemon=True).start()

    def connect_to_server(self):
        try:
            self.sio.connect(self.server_url)
            self.sio.wait()
        except:
            time.sleep(5)
            self.connect_to_server()

    def on_stop(self):
        if self.sio.connected:
            self.sio.disconnect()

if __name__=="__main__":
    import sys
    server_url = sys.argv[1] if len(sys.argv)>1 else server_url
    BrotherEyeApp(server_url=server_url).run()
