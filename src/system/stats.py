"""
Statistics formatting utilities for system information display.
Provides human-readable formatting for CPU, memory, and disk statistics.

Dependencies: None

Signals emitted: None
Signals received: None
"""


def format_cpu_usage(cpu_usage):
    """
    Format CPU usage as a readable string.

    Args:
        cpu_usage: CPU usage percentage (0-100)

    Returns:
        str: Formatted CPU usage string
    """
    return f"CPU Usage: {cpu_usage:.2f}%"


def format_memory_usage(memory_usage):
    """
    Format memory usage as a readable string.

    Args:
        memory_usage: Memory usage in MB

    Returns:
        str: Formatted memory usage string
    """
    return f"Memory Usage: {memory_usage:.2f} MB"


def format_disk_usage(disk_usage):
    """
    Format disk usage as a readable string.

    Args:
        disk_usage: Disk usage in GB

    Returns:
        str: Formatted disk usage string
    """
    return f"Disk Usage: {disk_usage:.2f} GB"


def format_system_info(system_info):
    """
    Format complete system information for display.

    Args:
        system_info: Dictionary with 'cpu', 'memory', and 'disk' keys

    Returns:
        str: Multi-line formatted system information
    """
    formatted_info = []
    for key, value in system_info.items():
        if key == 'cpu':
            formatted_info.append(format_cpu_usage(value))
        elif key == 'memory':
            formatted_info.append(format_memory_usage(value))
        elif key == 'disk':
            formatted_info.append(format_disk_usage(value))
    return "\n".join(formatted_info)