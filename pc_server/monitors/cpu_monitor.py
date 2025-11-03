import psutil

def get_cpu_usage():
    usage = psutil.cpu_percent(interval=1)
    return usage