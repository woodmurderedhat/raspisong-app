#!/usr/bin/env python3
"""
Test script to verify the Raspberry Pi LCD app setup.
Checks dependencies, hardware, and configuration.
"""

import sys
import os

def test_imports():
    """Test if all required Python modules can be imported."""
    print("Testing Python imports...")
    modules = {
        'psutil': 'System monitoring',
        'PIL': 'Image processing',
        'yaml': 'Configuration parsing',
        'vlc': 'VLC media player',
    }
    
    failed = []
    for module, description in modules.items():
        try:
            __import__(module)
            print(f"  ✓ {module:15} - {description}")
        except ImportError as e:
            print(f"  ✗ {module:15} - {description} - FAILED: {e}")
            failed.append(module)
    
    # Test GPIO modules (may fail on non-RPi systems)
    try:
        import RPi.GPIO
        print(f"  ✓ {'RPi.GPIO':15} - GPIO control")
    except (ImportError, RuntimeError) as e:
        print(f"  ⚠ {'RPi.GPIO':15} - GPIO control - Warning: {e}")
    
    try:
        import gpiozero
        print(f"  ✓ {'gpiozero':15} - GPIO zero library")
    except (ImportError, RuntimeError) as e:
        print(f"  ⚠ {'gpiozero':15} - GPIO zero library - Warning: {e}")
    
    try:
        import spidev
        print(f"  ✓ {'spidev':15} - SPI interface")
    except (ImportError, RuntimeError) as e:
        print(f"  ⚠ {'spidev':15} - SPI interface - Warning: {e}")
    
    return len(failed) == 0


def test_config():
    """Test if configuration file exists and is valid."""
    print("\nTesting configuration...")
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    
    if not os.path.exists(config_path):
        print(f"  ✗ Config file not found: {config_path}")
        return False
    
    print(f"  ✓ Config file exists: {config_path}")
    
    try:
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        required_keys = ['screen', 'vlc', 'system', 'gpio']
        for key in required_keys:
            if key in config:
                print(f"  ✓ Config section '{key}' found")
            else:
                print(f"  ✗ Config section '{key}' missing")
                return False
        
        return True
    except Exception as e:
        print(f"  ✗ Error loading config: {e}")
        return False


def test_spi():
    """Test if SPI interface is available."""
    print("\nTesting SPI interface...")
    
    spi_devices = ['/dev/spidev0.0', '/dev/spidev0.1']
    found = False
    
    for device in spi_devices:
        if os.path.exists(device):
            print(f"  ✓ SPI device found: {device}")
            found = True
    
    if not found:
        print("  ✗ No SPI devices found")
        print("    Run: sudo raspi-config nonint do_spi 0")
        print("    Then reboot")
        return False
    
    return True


def test_system_info():
    """Test system monitoring functionality."""
    print("\nTesting system monitoring...")
    
    try:
        import psutil
        
        cpu = psutil.cpu_percent(interval=0.1)
        print(f"  ✓ CPU usage: {cpu}%")
        
        mem = psutil.virtual_memory()
        print(f"  ✓ Memory usage: {mem.percent}%")
        
        disk = psutil.disk_usage('/')
        print(f"  ✓ Disk usage: {disk.percent}%")
        
        return True
    except Exception as e:
        print(f"  ✗ Error getting system info: {e}")
        return False


def test_vlc():
    """Test VLC availability."""
    print("\nTesting VLC...")
    
    try:
        import vlc
        instance = vlc.Instance('--quiet')
        player = instance.media_player_new()
        print(f"  ✓ VLC instance created successfully")
        player.release()
        instance.release()
        return True
    except Exception as e:
        print(f"  ✗ Error creating VLC instance: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Raspberry Pi LCD App - Setup Test")
    print("=" * 60)
    
    results = {
        'Imports': test_imports(),
        'Configuration': test_config(),
        'SPI Interface': test_spi(),
        'System Monitoring': test_system_info(),
        'VLC': test_vlc(),
    }
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:20} {status}")
    
    all_passed = all(results.values())
    
    print("=" * 60)
    if all_passed:
        print("All tests passed! ✓")
        print("You can now run: python3 src/main.py")
    else:
        print("Some tests failed. Please fix the issues above.")
        print("See README.md for installation instructions.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

