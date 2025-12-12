class Monitor:
    def __init__(self):
        pass

    def get_system_info(self):
        import psutil

        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')

        system_info = {
            'CPU Usage (%)': cpu_usage,
            'Memory Usage (%)': memory_info.percent,
            'Available Memory (MB)': memory_info.available / (1024 * 1024),
            'Disk Usage (%)': disk_info.percent,
            'Available Disk Space (GB)': disk_info.free / (1024 * 1024 * 1024),
        }

        return system_info