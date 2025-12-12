#!/bin/bash

# Installation script for Raspberry Pi 5 LCD System Monitor & VLC Controller
# This script sets up the application on a Raspberry Pi 5 with Waveshare 2.8" LCD (A)
# Compatible with Raspberry Pi OS Bookworm and Trixie

set -e  # Exit on error

echo "=========================================="
echo "Raspberry Pi 5 LCD App Installation"
echo "Waveshare 2.8\" LCD (A) Driver Setup"
echo "=========================================="
echo ""

# Detect Raspberry Pi model
detect_pi_model() {
    if [ -f /proc/device-tree/model ]; then
        PI_MODEL=$(cat /proc/device-tree/model)
        echo "Detected: $PI_MODEL"
        if [[ "$PI_MODEL" == *"Raspberry Pi 5"* ]]; then
            IS_PI5=true
        else
            IS_PI5=false
        fi
    else
        echo "Warning: This doesn't appear to be a Raspberry Pi"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        IS_PI5=false
    fi
}

detect_pi_model

# Determine config.txt location (changed in Bookworm)
if [ -f /boot/firmware/config.txt ]; then
    CONFIG_TXT="/boot/firmware/config.txt"
else
    CONFIG_TXT="/boot/config.txt"
fi
echo "Using config file: $CONFIG_TXT"

# Update system
echo ""
echo "Updating system packages..."
sudo apt-get update

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y python3-pip python3-dev python3-pil python3-spidev
sudo apt-get install -y vlc libvlc-dev
sudo apt-get install -y fonts-dejavu-core
sudo apt-get install -y cmake unzip

# Install touch screen dependencies
echo ""
echo "Installing touchscreen dependencies..."
sudo apt-get install -y python3-evdev
sudo apt-get install -y xserver-xorg-input-evdev
sudo apt-get install -y xinput-calibrator

# Install Raspberry Pi 5 specific GPIO libraries
if [ "$IS_PI5" = true ]; then
    echo ""
    echo "Installing Raspberry Pi 5 GPIO libraries..."
    sudo apt-get install -y python3-lgpio python3-gpiozero

    # Remove old RPi.GPIO if present (not compatible with Pi 5)
    pip3 uninstall -y RPi.GPIO 2>/dev/null || true
fi

# Enable SPI interface
echo ""
echo "Enabling SPI interface..."
sudo raspi-config nonint do_spi 0

# Install Waveshare 2.8" LCD driver overlay
echo ""
echo "Installing Waveshare 2.8\" LCD (A) driver..."
cd /tmp
if [ ! -f Waveshare28a-v2.zip ]; then
    sudo wget https://files.waveshare.com/wiki/common/Waveshare28a-v2.zip
fi
sudo unzip -o Waveshare28a-v2.zip
sudo cp waveshare28a-v2.dtbo /boot/overlays/

# Configure config.txt for the display
echo ""
echo "Configuring $CONFIG_TXT for Waveshare display..."

# Backup config.txt
sudo cp "$CONFIG_TXT" "${CONFIG_TXT}.backup.$(date +%Y%m%d%H%M%S)"

# Check if already configured
if ! grep -q "waveshare28a-v2" "$CONFIG_TXT"; then
    # Add Waveshare LCD configuration
    echo "" | sudo tee -a "$CONFIG_TXT"
    echo "# Waveshare 2.8\" LCD (A) Configuration" | sudo tee -a "$CONFIG_TXT"
    echo "dtparam=spi=on" | sudo tee -a "$CONFIG_TXT"
    echo "dtoverlay=waveshare28a-v2" | sudo tee -a "$CONFIG_TXT"
    echo "dtoverlay=ads7846,cs=1,penirq=17,penirq_pull=2,speed=50000,keep_vref_on=1,pmax=255,xohms=60" | sudo tee -a "$CONFIG_TXT"
    echo ""
    echo "Display overlay added to $CONFIG_TXT"
else
    echo "Waveshare display already configured in $CONFIG_TXT"
fi

# Return to script directory
cd "$(dirname "$0")"

# Create virtual environment (recommended for Bookworm)
echo ""
echo "Setting up Python virtual environment..."
python3 -m venv --system-site-packages .venv
source .venv/bin/activate

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Create media directory if it doesn't exist
echo ""
echo "Creating media directory..."
mkdir -p ~/media

# Set permissions
echo "Setting permissions..."
chmod +x src/main.py

echo ""
echo "=========================================="
echo "Installation complete!"
echo "=========================================="
echo ""
echo "IMPORTANT: A reboot is required for changes to take effect!"
echo ""
echo "Next steps:"
echo "1. Reboot: sudo reboot"
echo "2. Place your media files in ~/media/"
echo "3. Edit config.yaml to customize settings"
echo "4. Activate venv: source .venv/bin/activate"
echo "5. Run the application: python3 src/main.py"
echo ""
echo "Waveshare 2.8\" LCD (A) Controls:"
echo ""
echo "  Physical Buttons:"
echo "    KEY1 (GPIO 4)  - Play/Pause"
echo "    KEY2 (GPIO 23) - Stop"
echo "    KEY3 (GPIO 24) - Next"
echo "    KEY4 (GPIO 25) - Previous"
echo ""
echo "  Touch Screen:"
echo "    Tap buttons on screen for playback control"
echo "    Drag volume slider to adjust volume"
echo ""
echo "  Touch Calibration (if needed):"
echo "    Run: DISPLAY=:0 xinput_calibrator"
echo ""
