"""
System Monitor module for gathering Raspberry Pi system information.
Collects CPU usage, memory usage, and disk space statistics.

Compatible with Raspberry Pi 5.

Dependencies:
- psutil for system statistics

Signals emitted: None
Signals received: None
"""

import psutil


class Monitor:
    """
    System monitor for gathering CPU, memory, and disk usage statistics.

    Used to display system health information on the LCD screen.
    """

    def __init__(self):
        """Initialize the system monitor."""
        pass

    def get_system_info(self):
        """
        Gather current system statistics.

        Returns:
            dict: Dictionary containing system statistics:
                - 'CPU Usage (%)': Current CPU utilization percentage
                - 'Memory Usage (%)': Current memory utilization percentage
                - 'Available Memory (MB)': Available memory in megabytes
                - 'Disk Usage (%)': Root partition usage percentage
                - 'Available Disk Space (GB)': Free disk space in gigabytes
        """
        cpu_usage = psutil.cpu_percent(interval=0.1)
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