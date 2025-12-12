# Raspberry Pi 5 App

This project is a minimalistic application designed for the Raspberry Pi 5 that utilizes a Waveshare 2.8-inch LCD screen to display useful system information and act as a remote control for VLC media player. The application is modular, allowing for easy expansion and customization.

## Features

- Display system information such as CPU usage, memory usage, and disk space.
- Control VLC media player with play, pause, and stop functionalities.
- Exclusively use the Waveshare screen for displaying information and controls.
- Maintain HDMI and other functionalities of the Raspberry Pi.

## Project Structure

```
raspberry-pi-5-app
├── src
│   ├── main.py               # Entry point of the application
│   ├── display               # Module for managing the display
│   │   ├── __init__.py
│   │   ├── screen.py         # Screen management
│   │   └── renderer.py       # Rendering text and graphics
│   ├── system                # Module for system monitoring
│   │   ├── __init__.py
│   │   ├── monitor.py        # Gathers system information
│   │   └── stats.py          # Utility functions for stats
│   ├── vlc                   # Module for VLC control
│   │   ├── __init__.py
│   │   ├── controller.py     # Manages VLC commands
│   │   └── player.py         # Interfaces with VLC media player
│   ├── input                 # Module for handling input
│   │   ├── __init__.py
│   │   └── gpio.py           # GPIO input handling
│   └── config                # Module for configuration settings
│       ├── __init__.py
│       └── settings.py       # Configuration settings
├── requirements.txt          # Python dependencies
├── config.yaml               # Configuration settings in YAML format
└── README.md                 # Project documentation
```

## Hardware Requirements

- Raspberry Pi 5 (8GB RAM recommended)
- Waveshare 2.8" LCD (A) display
- GPIO buttons (5 buttons for full control)
- Jumper wires for connections

## Hardware Setup

### Waveshare 2.8" LCD Connection

The display connects via SPI interface. The pins are pre-configured in the code:
- RST: GPIO 27
- DC: GPIO 25
- BL (Backlight): GPIO 24
- CS: GPIO 8 (CE0)
- MOSI: GPIO 10
- SCLK: GPIO 11

### GPIO Button Connections

Default button configuration (can be changed in `config.yaml`):
- **Play**: GPIO 17
- **Pause**: GPIO 27
- **Stop**: GPIO 22
- **Next**: GPIO 23
- **Previous**: GPIO 24

Connect each button between the GPIO pin and GND.

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
   git clone <repository-url>
   cd raspberry-pi-5-app
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

vlc:
  default_media_path: "/home/pi/media"  # Path to media files
  volume: 50          # Default volume (0-100)
  autoplay: false     # Auto-start playback on launch

system:
  update_interval: 1  # Display update interval in seconds
  display_info:
    cpu_usage: true
    memory_usage: true
    disk_space: true

gpio:
  buttons:
    play: 17          # GPIO pin numbers
    pause: 27
    stop: 22
    next: 23
    previous: 24
```

## Usage

### Running Manually

```bash
cd raspberry-pi-5-app
python3 src/main.py
```

### Running as a System Service

1. Copy the service file:
   ```bash
   sudo cp rpi-lcd-monitor.service /etc/systemd/system/
   ```

2. Update the paths in the service file if needed:
   ```bash
   sudo nano /etc/systemd/system/rpi-lcd-monitor.service
   ```

3. Enable and start the service:
   ```bash
   sudo systemctl enable rpi-lcd-monitor.service
   sudo systemctl start rpi-lcd-monitor.service
   ```

4. Check service status:
   ```bash
   sudo systemctl status rpi-lcd-monitor.service
   ```

5. View logs:
   ```bash
   sudo journalctl -u rpi-lcd-monitor.service -f
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
- Ensure SPI is enabled: `sudo raspi-config`
- Check wiring connections
- Verify display is detected: `ls /dev/spidev*`
- Check logs for initialization errors

### GPIO buttons not responding
- Verify correct GPIO pin numbers in config
- Check button wiring (button between GPIO and GND)
- Ensure pull-up resistors are configured (handled in code)
- Test with `gpio readall` command

### VLC not playing
- Ensure VLC is installed: `vlc --version`
- Check media path in config.yaml
- Verify media files exist and are readable
- Check VLC logs for errors

### Permission errors
- Run with appropriate permissions
- Add user to gpio group: `sudo usermod -a -G gpio $USER`
- Add user to spi group: `sudo usermod -a -G spi $USER`
- Logout and login for group changes to take effect

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for details.