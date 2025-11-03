import os
import sys
import subprocess
import shlex
import time
from typing import List, Dict, Tuple, Optional
import psutil
import shutil

# Check whether OS is windows or Linux and create a dictionary

if os.name == 'nt':
    APPS={
        'chrome':r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        'vscode': r"C:\Users\Jawad\AppData\Local\Programs\Microsoft VS Code\Code.exe"
    }
else:
    APPS={
        'chrome':'google-chrome',
        'vscode':'code'
    }

def _resolve_command(cmd_or_path:str) -> Optional[List[str]]:

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

# App Opening function

def open_app(app_name:str) -> Tuple[bool,str]:

    if app_name in APPS:
        cmd=APPS[app_name]
    else:
        cmd=app_name

    resolved=_resolve_command(cmd)
    if not resolved:
        return False, f"Could Not Resolve Command {cmd}"

    try:
        subprocess.Popen(resolved)
        return True, f"Opened App :{cmd}"
    except Exception as e:
        return False, f"Failed to open app {cmd}: {str(e)}"

# Closing apps and processes

def close_app_by_name(process_name: str, wait: float = 3.0) -> Tuple[int, str]:
    """
    Attempt to terminate processes whose name contains process_name (case-insensitive).
    Returns (num_killed, message).
    NOTE: Many programs (like Chrome) spawn multiple processes. This kills all matches.
    """
    killed = 0
    matched_pids = []

    # Step 1: Find all matching processes
    for proc in psutil.process_iter(attrs=["pid", "name", "cmdline"]):
        try:
            name = (proc.info.get("name") or "").lower()
            cmdline = " ".join(proc.info.get("cmdline") or []).lower()
            if process_name.lower() in name or process_name.lower() in cmdline:
                pid = proc.info["pid"]
                matched_pids.append(pid)
                try:
                    proc.terminate()  # try graceful termination
                except Exception:
                    try:
                        proc.kill()  # force kill if terminate fails
                    except Exception:
                        pass
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Step 2: Wait for termination, force kill if necessary
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

    # Step 3: Return result
    if killed:
        return killed, f"Killed {killed} process(es) matching '{process_name}'"
    else:
        return 0, f"No running process matched '{process_name}'"

# Running python scripts of choice

def run_script(file_path: str, detach: bool = True) -> Tuple[bool, str]:
    """
    Run a script file. For the presentation we'll support Python scripts (.py).
    Returns (success, message). If detach=True, it won't block the caller.
    """
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"

    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == ".py":
            python_exe = sys.executable or "python"
            proc = subprocess.Popen([python_exe, file_path])
            return True, f"Started {file_path} (pid={proc.pid})"
        else:
            return False, f"Unsupported script type for now: {ext}"
    except Exception as e:
        return False, f"Error running script: {e}"

def open_in_vscode(path: str) -> Tuple[bool, str]:
    """
    Open a file or folder in VSCode. Uses APPS mapping if available or 'code' in PATH.
    """
    if "vscode" in APPS:
        cmd = APPS["vscode"]
        resolved = _resolve_command(cmd)
        if resolved:
            try:
                subprocess.Popen(resolved + [path])
                return True, f"Opened {path} in VSCode"
            except Exception as e:
                return False, f"Error opening in VSCode: {e}"
    # Fallback to 'code' CLI
    code_cmd = shutil.which("code")
    if code_cmd:
        try:
            subprocess.Popen([code_cmd, path])
            return True, f"Opened {path} in VSCode"
        except Exception as e:
            return False, f"Error opening in VSCode: {e}"
    return False, "VSCode command not found. Update APPS mapping or install 'code' CLI."

DEMO_SCRIPT = r"C:\brothereye\demo.py" # Replace with your script path
VS_CODE_FOLDER = r"C:\brothereye\demo_folder"       # Replace with folder you want to open

def print_menu():
    print("\n=== Raspberry Pi Action Button Demo ===")
    print("1. Open VS Code")
    print("2. Close VS Code")
    print("3. Open Chrome")
    print("4. Close Chrome")
    print("5. Run demo Python script")
    print("6. Open project folder in VS Code")
    print("0. Exit")

def main():
    while True:
        print_menu()
        choice = input("Enter choice: ").strip()

        if choice == "1":
            success, msg = open_app("vscode")
        elif choice == "2":
            killed, msg = close_app_by_name("Code.exe")  # Windows process name
            print(msg)
            continue
        elif choice == "3":
            success, msg = open_app("chrome")
        elif choice == "4":
            killed, msg = close_app_by_name("chrome.exe")
            print(msg)
            continue
        elif choice == "5":
            success, msg = run_script(DEMO_SCRIPT)
        elif choice == "6":
            success, msg = open_in_vscode(VS_CODE_FOLDER)
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid choice! Try again.")
            continue

        # Print messages for success/failure
        if "success" in locals():
            print(msg)

if __name__ == "__main__":
    main()