.

👁️‍🗨️ Brother Eye
Real-Time PC System Monitor with FastAPI + Socket.IO + Python Client

Brother Eye is a real-time system monitoring tool that streams live hardware stats — such as CPU usage, memory, disk, and battery levels — from a PC server to a client device (like a Raspberry Pi display or secondary monitor).

It’s designed to act as an intelligent, always-on “eye” that watches your system health and can eventually support interactive features like system control, notifications, and AI integration.

Currently working on better UI and ML algorithms to run on it. Future updates would be security concerns.

🧠 Project Overview

Brother Eye consists of two main components:

PC Server (FastAPI + Socket.IO)

Runs on your computer and collects system metrics.

Broadcasts real-time data to all connected clients via WebSockets.

Client (Python + Socket.IO)

Connects to the server and displays system stats in real time.

Can run on another computer, Raspberry Pi, or even a small screen interface.

🧩 Features

⚡ Real-Time Monitoring — CPU, Memory, Disk, Battery

🌐 Socket.IO Streaming — Live bi-directional communication

🧱 FastAPI Backend — Lightweight and async-ready server

💻 Python Client — Displays stats in real time (console or GUI)

🔄 Modular Design — Easy to extend for GPU, network, or temperature stats

📡 Scalable — Multiple clients can connect simultaneously

🧰 Future Integration Goals:

Kivy UI with dashboard-style gauges

AI-based system recommendations

Action buttons (restart apps, clear RAM, etc.)
