# Hardware Wiring Guide

## Waveshare 2.8" LCD (A) Display

> **Note:** This guide is updated for **Raspberry Pi 5** and the **Waveshare 2.8" LCD (A) Rev2.0/Rev2.1**.
> The display plugs directly onto the 26-pin GPIO header (pins 1-26).

### Display Pinout (Official Waveshare Documentation)

The Waveshare 2.8" LCD (A) connects directly to the Raspberry Pi GPIO header using a 26-pin connector.

```
PIN NO.  SYMBOL      GPIO        DESCRIPTION
────────────────────────────────────────────────────────
1        3.3V        -           Power (3.3V input)
2        5V          -           Power (5V input)
3        NC          -           Not connected
4        5V          -           Power (5V input)
5        NC          -           Not connected
6        GND         -           Ground
7        KEY1        GPIO 4      Button 1 (directly usable)
8        NC          -           Not connected
9        GND         -           Ground
10       NC          -           Not connected
11       TP_IRQ      GPIO 17     Touch panel interrupt
12       PWM         GPIO 18     Backlight control (PWM capable, Rev2.1)
13       RST         GPIO 27     LCD Reset - NOTE: Code uses GPIO 13 per Waveshare spec
14       GND         -           Ground
15       LCD_RS      GPIO 22     LCD DC (Data/Command) - NOTE: Code uses GPIO 15
16       KEY2        GPIO 23     Button 2 (directly usable)
17       3.3V        -           Power (3.3V input)
18       KEY3        GPIO 24     Button 3 (directly usable)
19       LCD_SI      GPIO 10     SPI MOSI (LCD + Touch)
20       GND         -           Ground
21       TP_SCL      GPIO 9      SPI MISO (Touch panel only)
22       KEY4        GPIO 25     Button 4 (directly usable)
23       LCD_SCK     GPIO 11     SPI Clock (LCD + Touch)
24       LCD_CS      GPIO 8      LCD Chip Select (CE0)
25       GND         -           Ground
26       TP_CS       GPIO 7      Touch panel Chip Select (CE1)
```

### Physical Connection

The display has a 26-pin header that plugs directly onto pins 1-26 of the Raspberry Pi's 40-pin GPIO header. **Align Pin 1 (3.3V) correctly!**

```
Raspberry Pi GPIO Header
┌─────────────────────────┐
│ (1)  (2)  ... (25) (26) │  ← LCD connects here (pins 1-26)
│ ...                     │
│ (39) (40)               │  ← Pins 27-40 remain free
└─────────────────────────┘
```

### SPI Configuration (Required)

Enable SPI interface before using the display:

```bash
# Enable SPI
sudo raspi-config nonint do_spi 0

# Verify SPI is enabled
ls /dev/spidev*
# Should show: /dev/spidev0.0  /dev/spidev0.1

sudo reboot
```

### Driver Installation (Bookworm/Trixie)

For Raspberry Pi 5 with Bookworm or Trixie OS, install the Waveshare overlay:

```bash
# Download and install driver
sudo wget https://files.waveshare.com/wiki/common/Waveshare28a-v2.zip
sudo unzip Waveshare28a-v2.zip
sudo cp waveshare28a-v2.dtbo /boot/overlays/

# Edit config.txt (location varies by OS version)
sudo nano /boot/firmware/config.txt   # Bookworm/Trixie
# OR
sudo nano /boot/config.txt            # Older OS versions

# Add these lines at the end:
dtparam=spi=on
dtoverlay=waveshare28a-v2
dtoverlay=ads7846,cs=1,penirq=17,penirq_pull=2,speed=50000,keep_vref_on=1,pmax=255,xohms=60
```

---

## GPIO Button Connections (Onboard Buttons)

The Waveshare 2.8" LCD (A) has **4 onboard buttons** (KEY1-KEY4) directly connected to GPIO pins:

### Onboard Button Configuration

```
Button    GPIO Pin    Physical Pin    Function
──────────────────────────────────────────────
KEY1      GPIO 4      Pin 7           Play/Pause
KEY2      GPIO 23     Pin 16          Stop
KEY3      GPIO 24     Pin 18          Next Track
KEY4      GPIO 25     Pin 22          Previous Track
```

### Button Behavior

- **Active-low:** Buttons connect GPIO to GND when pressed
- **Internal pull-ups:** Configured in software via gpiozero
- **Debouncing:** Handled in software (300ms default)

---

## Complete Wiring Diagram

```
Raspberry Pi 5 GPIO Header (40 pins)
════════════════════════════════════════════════════════════════

LCD CONNECTOR (Pins 1-26)                    FREE PINS (27-40)
─────────────────────────────────────        ─────────────────
     3.3V  (1) ──LCD─── (2)  5V                GPIO0 (27) (28) GPIO1
    GPIO2  (3) ──LCD─── (4)  5V                GPIO5 (29) (30) GND
    GPIO3  (5) ──LCD─── (6)  GND               GPIO6 (31) (32) GPIO12
    GPIO4  (7) ──KEY1── (8)  GPIO14           GPIO13 (33) (34) GND
      GND  (9) ──LCD─── (10) GPIO15           GPIO19 (35) (36) GPIO16
   GPIO17 (11) ──TP_IRQ (12) GPIO18 ←PWM/BL   GPIO26 (37) (38) GPIO20
   GPIO27 (13) ──RST─── (14) GND                 GND (39) (40) GPIO21
   GPIO22 (15) ──LCD_RS (16) GPIO23 ←KEY2
     3.3V (17) ──LCD─── (18) GPIO24 ←KEY3
   GPIO10 (19) ──MOSI── (20) GND
    GPIO9 (21) ──MISO── (22) GPIO25 ←KEY4
   GPIO11 (23) ──SCLK── (24) GPIO8 ←LCD_CS
      GND (25) ──LCD─── (26) GPIO7 ←TP_CS
```

---

## Customizing Button Pins

To change button GPIO assignments, edit `config.yaml`:

```yaml
gpio:
  buttons:
    play_pause: 4    # KEY1 - GPIO 4
    stop: 23         # KEY2 - GPIO 23
    next: 24         # KEY3 - GPIO 24
    previous: 25     # KEY4 - GPIO 25
```

### Reserved Pins (Do NOT Use)

These pins are used by the LCD and should not be reassigned:

| Function | GPIO | Physical Pin |
|----------|------|--------------|
| SPI MOSI | 10   | 19 |
| SPI MISO | 9    | 21 |
| SPI SCLK | 11   | 23 |
| LCD CS   | 8    | 24 |
| Touch CS | 7    | 26 |
| LCD DC   | 15   | 10 |
| LCD RST  | 13   | 33 |
| Touch IRQ| 17   | 11 |
| Backlight| 18   | 12 |

---

## Testing

### Test Display

```bash
# Activate virtual environment (if using)
source .venv/bin/activate

# Run test script
python3 test_setup.py
```

### Test Buttons

```bash
python3 src/main.py
```

Press each button and watch the console for messages like:
```
Play/Pause button pressed
Stop button pressed
Next button pressed
Previous button pressed
```

---

## Troubleshooting

### Display Issues

| Problem | Solution |
|---------|----------|
| No display | Check SPI enabled: `ls /dev/spidev*` |
| Garbled display | Verify dtoverlay in config.txt |
| Dim/No backlight | Check GPIO 18 PWM configuration |
| White screen | Reset sequence timing issue |

### Button Issues

| Problem | Solution |
|---------|----------|
| No response | Check GPIO pin numbers in config.yaml |
| Multiple triggers | Increase `debounce_delay` in gpio.py |
| Random triggers | Check for loose connections |

### Raspberry Pi 5 Specific Issues

| Problem | Solution |
|---------|----------|
| `RuntimeError: Cannot determine SOC peripheral base address` | Use `lgpio` or `gpiozero` instead of `RPi.GPIO` |
| GPIO permission denied | Add user to gpio group: `sudo usermod -aG gpio $USER` |
| SPI not working | Check `/boot/firmware/config.txt` has `dtparam=spi=on` |

---

## Safety Notes

⚠️ **Important:**

- Power off Raspberry Pi before connecting/disconnecting the LCD
- The display connects to pins 1-26 only - verify alignment
- Display uses 3.3V logic - never connect to 5V signals
- The LCD header covers some GPIO pins - plan external wiring accordingly
- For Pi 5: Use `gpiozero` with `lgpio` backend (RPi.GPIO not supported)

