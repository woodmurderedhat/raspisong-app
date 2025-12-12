# Raspisong App

A minimalistic media player application designed for the Raspberry Pi 5 that utilizes a Waveshare 2.8-inch LCD screen to display a touch-friendly media player interface. Control VLC media player with both touchscreen and physical GPIO buttons. The application is modular, allowing for easy expansion and customization.

## Features

- Touch-friendly media player UI with large buttons
- Control VLC media player with play/pause, stop, next, and previous
- Resistive touchscreen support with touch regions and sliders
- 4 onboard GPIO buttons for physical control
- System monitoring (CPU, memory, disk usage)
- Exclusively use the Waveshare screen for displaying information and controls
- Maintain HDMI and other functionalities of the Raspberry Pi

## Project Structure

```
raspisong-app
├── src
│   ├── main.py               # Entry point of the application
│   ├── display               # Module for managing the display
│   │   ├── __init__.py
│   │   ├── screen.py         # Screen management (ILI9341 driver)
│   │   ├── renderer.py       # MediaPlayerUI and legacy Renderer
│   │   └── ui_components.py  # Button, Slider, ProgressBar components
│   ├── system                # Module for system monitoring
│   │   ├── __init__.py
│   │   ├── monitor.py        # Gathers system information
│   │   └── stats.py          # Utility functions for stats
│   ├── vlc                   # Module for VLC control
│   │   ├── __init__.py
│   │   ├── controller.py     # Manages VLC commands and playlists
│   │   └── player.py         # Simple VLC media player wrapper
│   ├── input                 # Module for handling input
│   │   ├── __init__.py
│   │   ├── gpio.py           # GPIO button input handling
│   │   └── touch.py          # Touchscreen input handling (ADS7846)
│   └── config                # Module for configuration settings
│       ├── __init__.py
│       └── settings.py       # Configuration settings
├── requirements.txt          # Python dependencies
├── config.yaml               # Configuration settings in YAML format
├── install.sh                # Automated installation script
├── test_setup.py             # Setup verification script
├── rpi-lcd-monitor.service   # Systemd service file
├── WIRING.md                 # Detailed hardware wiring guide
└── README.md                 # Project documentation
```

## Hardware Requirements

- Raspberry Pi 5 (8GB RAM recommended)
- Waveshare 2.8" LCD (A) display (Rev2.0 or Rev2.1)
- No additional wiring needed - the LCD has 4 onboard buttons

## Hardware Setup

### Waveshare 2.8" LCD Connection

The display connects directly via a 26-pin header to pins 1-26 of the Raspberry Pi GPIO. The pins are pre-configured in the code:

- **RST**: GPIO 13 (Physical Pin 33)
- **DC/RS**: GPIO 15 (Physical Pin 10)
- **BL (Backlight)**: GPIO 18 (Physical Pin 12) - PWM capable
- **LCD CS**: GPIO 8 (Physical Pin 24) - CE0
- **Touch CS**: GPIO 7 (Physical Pin 26) - CE1
- **MOSI**: GPIO 10 (Physical Pin 19)
- **MISO**: GPIO 9 (Physical Pin 21)
- **SCLK**: GPIO 11 (Physical Pin 23)

See [WIRING.md](WIRING.md) for detailed pinout and wiring diagrams.

### GPIO Button Configuration (Onboard Buttons)

The Waveshare 2.8" LCD (A) has 4 onboard buttons. Default configuration (can be changed in `config.yaml`):

| Button | GPIO Pin | Physical Pin | Function    |
|--------|----------|--------------|-------------|
| KEY1   | GPIO 4   | Pin 7        | Play/Pause  |
| KEY2   | GPIO 23  | Pin 16       | Stop        |
| KEY3   | GPIO 24  | Pin 18       | Next Track  |
| KEY4   | GPIO 25  | Pin 22       | Previous    |

The buttons are active-low with internal pull-ups configured in software.

## Installation

### Quick Installation

Run the automated installation script:
```bash
chmod +x install.sh
./install.sh
```

### Manual Installation

1. Clone the repository:
   ```bash
   git clone <repository-url> raspisong-app
   cd raspisong-app
   ```

2. Update system and install dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-pip python3-dev python3-pil python3-spidev
   sudo apt-get install -y vlc libvlc-dev fonts-dejavu-core
   ```

3. Enable SPI interface:
   ```bash
   sudo raspi-config nonint do_spi 0
   ```

4. Install Python dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

5. Create media directory:
   ```bash
   mkdir -p ~/media
   ```

6. Reboot to apply SPI changes:
   ```bash
   sudo reboot
   ```

## Configuration

Edit `config.yaml` to customize the application:

```yaml
screen:
  width: 240          # Display width
  height: 320         # Display height
  rotation: 0         # Rotation (0, 90, 180, 270)
  spi_bus: 0          # SPI bus number
  spi_device: 0       # SPI device (CE0)
  spi_speed_hz: 32000000  # SPI clock speed

vlc:
  default_media_path: "~/media"  # Path to media files (~ expands to user home)
  volume: 50          # Default volume (0-100)
  autoplay: false     # Auto-start playback on launch

system:
  update_interval: 1  # Status logging interval in seconds
  display_info:
    cpu_usage: true
    memory_usage: true
    disk_space: true

gpio:
  # Waveshare 2.8" LCD (A) onboard button configuration
  buttons:
    play_pause: 4     # KEY1 - GPIO 4, Pin 7 (combined play/pause)
    stop: 23          # KEY2 - GPIO 23, Pin 16
    next: 24          # KEY3 - GPIO 24, Pin 18
    previous: 25      # KEY4 - GPIO 25, Pin 22
```

## Usage

### Running Manually

```bash
cd raspisong-app
source .venv/bin/activate
python3 src/main.py
```

### Running as a System Service

The install script automatically sets up the systemd service with the correct user and paths.

Control the service with:
```bash
sudo systemctl start rpi-lcd-monitor    # Start now
sudo systemctl stop rpi-lcd-monitor     # Stop
sudo systemctl restart rpi-lcd-monitor  # Restart
sudo systemctl status rpi-lcd-monitor   # Check status
journalctl -u rpi-lcd-monitor -f        # View live logs
```

### Adding Media Files

Place your media files (MP3, MP4, AVI, MKV, WAV, FLAC, OGG) in the configured media directory:
```bash
cp /path/to/your/media/* ~/media/
```

## Features

### System Monitoring
- Real-time CPU usage percentage
- Memory usage percentage and available memory
- Disk usage percentage and available space
- Updates every second (configurable)

### VLC Media Control
- Play/Pause/Stop controls
- Next/Previous track navigation
- Volume control
- Playlist support
- Current track display
- Playback status indicator

### Display
- 240x320 pixel color LCD
- Clear, readable system information
- VLC playback status
- Current track name display
- Dedicated display (HDMI remains available)

## Troubleshooting

### Display not working
- Ensure SPI is enabled: `sudo raspi-config nonint do_spi 0`
- Verify display overlay is installed: check `/boot/firmware/config.txt` for `dtoverlay=waveshare28a-v2`
- Verify display is detected: `ls /dev/spidev*` should show `/dev/spidev0.0` and `/dev/spidev0.1`
- Check logs for initialization errors: `journalctl -u rpi-lcd-monitor -f`

### GPIO buttons not responding
- Verify correct GPIO pin numbers in config.yaml
- The onboard buttons use GPIO 4, 23, 24, 25
- Ensure you're using gpiozero (not RPi.GPIO) for Pi 5 compatibility
- Check button status: run `python3 src/input/gpio.py` to test buttons

### Touchscreen not working
- Check touch panel overlay in config.txt: `dtoverlay=ads7846,cs=1,penirq=17,...`
- Verify touch device exists: `ls /dev/input/event*`
- Run calibration: `DISPLAY=:0 xinput_calibrator`
- Check evdev permissions: user must have access to /dev/input/event*

### VLC not playing
- Ensure VLC is installed: `vlc --version`
- Check media path in config.yaml (supports `~` for home directory)
- Verify media files exist: `ls ~/media/`
- Check VLC logs for errors

### Raspberry Pi 5 specific issues
- `RuntimeError: Cannot determine SOC peripheral base address`: Use `gpiozero` with `lgpio` backend (this is the default in this project)
- GPIO permission denied: `sudo usermod -aG gpio $USER`, then logout/login
- SPI not working: Check `/boot/firmware/config.txt` has `dtparam=spi=on`
- RPi.GPIO not working: Use gpiozero instead (RPi.GPIO is not compatible with Pi 5)

### Permission errors
- Add user to gpio group: `sudo usermod -aG gpio $USER`
- Add user to spi group: `sudo usermod -aG spi $USER`
- Add user to input group (for touch): `sudo usermod -aG input $USER`
- Logout and login for group changes to take effect

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for details.