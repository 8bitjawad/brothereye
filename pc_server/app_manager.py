import os
import sys
import subprocess
import shlex
import time
from typing import List, Optional, Tuple
import psutil
import shutil

# ----------------------------
# App paths depending on OS
# ----------------------------
if os.name == 'nt':  # Windows
    APPS = {
        'chrome': r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        'vscode': r"C:\Users\Jawad\AppData\Local\Programs\Microsoft VS Code\Code.exe"
    }
else:  # Linux / Raspberry Pi (if needed)
    APPS = {
        'chrome': 'google-chrome',
        'vscode': 'code'
    }

# ----------------------------
# Helper function to resolve commands
# ----------------------------
def _resolve_command(cmd_or_path: str) -> Optional[List[str]]:
    if os.path.exists(cmd_or_path):
        return [cmd_or_path]
    found = shutil.which(cmd_or_path)
    if found:
        return [found]
    try:
        parts = shlex.split(cmd_or_path)
        return parts
    except Exception:
        return None

# ----------------------------
# Open an app
# ----------------------------
def open_app(app_name: str) -> Tuple[bool, str]:
    cmd = APPS.get(app_name, app_name)
    resolved = _resolve_command(cmd)
    if not resolved:
        return False, f"Could not resolve command: {cmd}"
    try:
        subprocess.Popen(resolved)
        return True, f"Opened app: {cmd}"
    except Exception as e:
        return False, f"Failed to open app {cmd}: {e}"

# ----------------------------
# Close app by process name
# ----------------------------
def close_app_by_name(process_name: str, wait: float = 3.0) -> Tuple[int, str]:
    killed = 0
    matched_pids = []

    for proc in psutil.process_iter(attrs=["pid", "name", "cmdline"]):
        try:
            name = (proc.info.get("name") or "").lower()
            cmdline = " ".join(proc.info.get("cmdline") or []).lower()
            if process_name.lower() in name or process_name.lower() in cmdline:
                pid = proc.info["pid"]
                matched_pids.append(pid)
                try:
                    proc.terminate()
                except Exception:
                    try:
                        proc.kill()
                    except Exception:
                        pass
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    deadline = time.time() + wait
    for pid in matched_pids:
        try:
            p = psutil.Process(pid)
            while p.is_running() and time.time() < deadline:
                time.sleep(0.1)
            if p.is_running():
                try:
                    p.kill()
                except Exception:
                    pass
            if not p.is_running():
                killed += 1
        except psutil.NoSuchProcess:
            killed += 1
        except Exception:
            pass

    if killed:
        return killed, f"Killed {killed} process(es) matching '{process_name}'"
    else:
        return 0, f"No running process matched '{process_name}'"

# ----------------------------
# Run Python script
# ----------------------------
def run_script(file_path: str, detach: bool = True) -> Tuple[bool, str]:
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == ".py":
            python_exe = sys.executable or "python"
            subprocess.Popen([python_exe, file_path])
            return True, f"Started {file_path}"
        else:
            return False, f"Unsupported script type: {ext}"
    except Exception as e:
        return False, f"Error running script: {e}"

# ----------------------------
# Open folder/file in VSCode
# ----------------------------
def open_in_vscode(path: str) -> Tuple[bool, str]:
    cmd = APPS.get("vscode", "code")
    resolved = _resolve_command(cmd)
    if resolved:
        try:
            subprocess.Popen(resolved + [path])
            return True, f"Opened {path} in VSCode"
        except Exception as e:
            return False, f"Error opening in VSCode: {e}"
    code_cmd = shutil.which("code")
    if code_cmd:
        try:
            subprocess.Popen([code_cmd, path])
            return True, f"Opened {path} in VSCode"
        except Exception as e:
            return False, f"Error opening in VSCode: {e}"
    return False, "VSCode command not found. Update APPS mapping or install 'code' CLI."
