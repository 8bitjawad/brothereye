import psutil

def get_battery_usage():
    usage = psutil.sensors_battery()
    if usage:
        return usage.percent
    else:
        return None