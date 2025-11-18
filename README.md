
# **👁️‍🗨️ Brother Eye : Real-Time PC System Monitor with FastAPI + Socket.IO + Python Client**

Brother Eye is a real-time system monitoring tool that streams live hardware stats — such as CPU usage, memory, disk, and battery levels — from a PC server to a client device (like a Raspberry Pi display or secondary monitor).

It’s designed to act as an intelligent, always-on “eye” that watches your system health and can eventually support interactive features like system control, notifications, and AI integration.

Currently working on better UI and ML algorithms to run on it. Future updates would be security concerns.

## 🧠 Project Overview

Brother Eye consists of two main components:

## PC Server (FastAPI + Socket.IO)

Runs on your computer and collects system metrics.

Broadcasts real-time data to all connected clients via WebSockets.

## Client (Python + Socket.IO)

Connects to the server and displays system stats in real time.

Can run on another computer, Raspberry Pi, or even a small screen interface.

## Machine Learning Features
### KMeans Clustering (Behavior Profiling)

Used to learn “normal behavior patterns” of your system.

Offline or periodic training on collected stats

Groups system behavior into clusters (e.g., idle, normal load, heavy load)

Detects anomalies when a reading falls far from its assigned cluster centroid

Useful for:

Detecting unusual process activity

Predicting abnormal CPU usage patterns

Understanding long-term behavior trends

### Isolation Forest (Advanced Anomaly Detection)

Suitable for non-linear, complex anomaly patterns.

Learns normal and abnormal patterns automatically

Flags anomalies based on how easily a point gets isolated in a random forest

Works well even when data has multiple dimensions (CPU, RAM, Disk, Net, GPU)

Use cases:

Detect malicious processes consuming resources

Identify sudden memory leaks

Catch low-frequency but high-impact anomalies

## 🧩 Features

⚡ Real-Time Monitoring — CPU, Memory, Disk, Battery

🌐 Socket.IO Streaming — Live bi-directional communication

🧱 FastAPI Backend — Lightweight and async-ready server

💻 Python Client — Displays stats in real time (console or GUI)

🔄 Modular Design — Easy to extend for GPU, network, or temperature stats

📡 Scalable — Multiple clients can connect simultaneously

🧰 Future Integration Goals:

-NiceGUI with dashboard-style gauges

-AI-based system recommendations

-Action buttons (open and close apps, run a python script)

## Working Screenshots:

<img width="1860" height="629" alt="Screenshot 2025-11-18 181320" src="https://github.com/user-attachments/assets/c7626f42-1ac5-4dbc-9727-abc9367fda5b" />
<img width="1867" height="700" alt="Screenshot 2025-11-18 181308" src="https://github.com/user-attachments/assets/5760665c-7634-445d-a0e7-bb4709f1afda" />
<img width="1880" height="845" alt="Screenshot 2025-11-18 181212" src="https://github.com/user-attachments/assets/1fe65aec-c29a-43ab-8216-a1d43acec99c" />
<img width="1880" height="682" alt="Screenshot 2025-11-18 181330" src="https://github.com/user-attachments/assets/35a8f3a8-b9b5-4487-a412-92e3296c3b4e" />

