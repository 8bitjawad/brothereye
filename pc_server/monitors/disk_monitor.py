import psutil

def get_disk_usage():
    usage = psutil.disk_usage("C:\\").percent
    return usage