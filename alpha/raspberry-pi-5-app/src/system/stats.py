def format_cpu_usage(cpu_usage):
    return f"CPU Usage: {cpu_usage:.2f}%"

def format_memory_usage(memory_usage):
    return f"Memory Usage: {memory_usage:.2f} MB"

def format_disk_usage(disk_usage):
    return f"Disk Usage: {disk_usage:.2f} GB"

def format_system_info(system_info):
    formatted_info = []
    for key, value in system_info.items():
        if key == 'cpu':
            formatted_info.append(format_cpu_usage(value))
        elif key == 'memory':
            formatted_info.append(format_memory_usage(value))
        elif key == 'disk':
            formatted_info.append(format_disk_usage(value))
    return "\n".join(formatted_info)