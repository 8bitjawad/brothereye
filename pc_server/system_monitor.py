from .monitors.cpu_monitor import get_cpu_usage
from .monitors.ram_monitor import get_ram_usage
from .monitors.disk_monitor import get_disk_usage
from .monitors.battery_monitor import get_battery_usage

def get_system_stats():
    stats = {
        "cpu":get_cpu_usage(),
        "memory":get_ram_usage(),
        "disk":get_disk_usage(),
        "battery":get_battery_usage()
    }
    return stats
