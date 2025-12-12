# Quick Start Guide

Get your Raspberry Pi LCD System Monitor up and running in 5 minutes!

## Prerequisites

- Raspberry Pi 5 with Raspberry Pi OS installed
- Waveshare 2.8" LCD (A) display
- 5 push buttons (optional, for VLC control)
- Internet connection for installation

## Step 1: Hardware Setup (5 minutes)

1. **Power off your Raspberry Pi**
   ```bash
   sudo shutdown -h now
   ```

2. **Connect the Waveshare LCD**
   - Align the display's 26-pin header with the Raspberry Pi GPIO pins
   - Gently press down to seat the connector
   - Ensure Pin 1 is aligned correctly

3. **Connect buttons (optional)**
   - See [WIRING.md](WIRING.md) for detailed wiring
   - Quick reference:
     - Play: GPIO 17 → GND
     - Pause: GPIO 27 → GND
     - Stop: GPIO 22 → GND
     - Next: GPIO 23 → GND
     - Previous: GPIO 24 → GND

4. **Power on your Raspberry Pi**

## Step 2: Software Installation (3 minutes)

1. **Clone or download this repository**
   ```bash
   cd ~
   git clone <repository-url> raspberry-pi-5-app
   cd raspberry-pi-5-app
   ```

2. **Run the installation script**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. **Reboot to enable SPI**
   ```bash
   sudo reboot
   ```

## Step 3: Configuration (2 minutes)

1. **Add your media files**
   ```bash
   cp /path/to/your/music/* ~/media/
   ```

2. **Edit configuration (optional)**
   ```bash
   nano config.yaml
   ```
   
   Key settings:
   - `vlc.default_media_path`: Path to your media files
   - `vlc.volume`: Default volume (0-100)
   - `vlc.autoplay`: Auto-start playback (true/false)
   - `gpio.buttons`: GPIO pin assignments

## Step 4: Test & Run

1. **Test the setup**
   ```bash
   python3 test_setup.py
   ```
   
   All tests should pass ✓

2. **Run the application**
   ```bash
   cd ~/raspberry-pi-5-app
   python3 src/main.py
   ```

3. **You should see:**
   - System info on the LCD display
   - Console output showing status updates
   - Button presses triggering VLC controls

4. **Stop the application**
   - Press `Ctrl+C`

## Step 5: Run as Service (Optional)

To start the app automatically on boot:

```bash
# Copy service file
sudo cp rpi-lcd-monitor.service /etc/systemd/system/

# Edit paths if needed
sudo nano /etc/systemd/system/rpi-lcd-monitor.service

# Enable and start
sudo systemctl enable rpi-lcd-monitor.service
sudo systemctl start rpi-lcd-monitor.service

# Check status
sudo systemctl status rpi-lcd-monitor.service
```

## What You Should See

### On the LCD Display:
```
System Monitor
──────────────
CPU: 15.2%
Memory: 23.5%
Disk: 45.8%
VLC: Playing
Track: song.mp3
```

### In the Console:
```
[12:34:56] CPU: 15.2% | Memory: 23.5% | Disk: 45.8% | VLC: Playing | Track: song.mp3
```

## Button Controls

- **Play**: Start playback
- **Pause**: Pause playback
- **Stop**: Stop playback
- **Next**: Next track
- **Previous**: Previous track

## Troubleshooting

### Display not working?
```bash
# Check SPI is enabled
ls /dev/spidev*

# Should show: /dev/spidev0.0  /dev/spidev0.1

# If not, enable SPI:
sudo raspi-config nonint do_spi 0
sudo reboot
```

### Buttons not responding?
```bash
# Check GPIO permissions
sudo usermod -a -G gpio $USER
sudo usermod -a -G spi $USER
# Logout and login again
```

### VLC not playing?
```bash
# Check VLC is installed
vlc --version

# Check media files exist
ls ~/media/

# Check file permissions
chmod +r ~/media/*
```

### Import errors?
```bash
# Reinstall dependencies
pip3 install -r requirements.txt
```

## Next Steps

- **Customize the display**: Edit `src/display/screen.py`
- **Add more buttons**: Update `config.yaml` and `src/input/gpio.py`
- **Change update interval**: Edit `system.update_interval` in `config.yaml`
- **Add new features**: The modular design makes it easy to extend!

## Getting Help

- Check [README.md](README.md) for detailed documentation
- See [WIRING.md](WIRING.md) for wiring diagrams
- Review logs: `sudo journalctl -u rpi-lcd-monitor.service -f`
- Test setup: `python3 test_setup.py`

## SSH Access

If you need to access your Raspberry Pi remotely:

```bash
# From your computer:
ssh betty@betty-white.local
# Password: 1337
```

---

**Enjoy your new Raspberry Pi LCD System Monitor!** 🎉

