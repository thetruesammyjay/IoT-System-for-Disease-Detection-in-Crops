# Raspberry Pi Hardware Setup

The physical adapters target Raspberry Pi OS 64-bit on a Raspberry Pi 5 with a Camera Module 3 and a DHT22. Keep `inference.backend: simulation` during the first hardware test so camera and sensor failures are isolated from model-deployment failures.

## Wiring

Power off the Raspberry Pi before changing any connection.

| Component | Raspberry Pi connection |
|---|---|
| Camera Module 3 | CAM/DISP CSI connector with the correct Pi 5 camera cable |
| DHT22 VCC, pin 1 | 3.3 V, physical pin 1 |
| DHT22 DATA, pin 2 | GPIO4, physical pin 7 |
| DHT22 GND, pin 4 | Ground, physical pin 6 |

Place the required pull-up resistor between DHT22 VCC and DATA. The configured `gpio_pin` is a BCM GPIO number, so the default value `4` resolves to `board.D4` in Adafruit Blinka.

## Operating-system packages

Picamera2 is distributed as a Raspberry Pi OS package and should not be installed from PyPI. The official Raspberry Pi camera documentation provides the supported installation command.

```bash
sudo apt update
sudo apt install -y python3-picamera2 libgpiod2
rpicam-hello --list-cameras
```

If the camera is absent from the list, power down and check the cable orientation and CSI connector before testing Python code.

## uv environment

Create the project environment from the operating-system Python and expose the system Picamera2 package to it. The hardware extra installs the Adafruit DHT driver and its Python dependencies.

```bash
uv venv --python /usr/bin/python3 --system-site-packages
source .venv/bin/activate
uv sync --extra hardware --extra simulation
```

## Configuration

Use this configuration for the first physical capture while retaining simulated inference:

```yaml
inference:
  backend: simulation

camera:
  resolution: [1920, 1080]
  rotation: 0
  warmup_seconds: 2.0
  save_captures: false
  capture_dir: data/captures

sensor:
  backend: dht22
  gpio_pin: 4
  use_pulseio: false
  retries: 3
  retry_delay_s: 2.0

monitoring:
  enabled: true
  source: picamera2
  capture_interval_s: 5.0
  auto_start: false
```

The five-second monitoring interval respects the DHT22's slow sampling behavior. `use_pulseio: false` selects the Linux bit-banging path documented by Adafruit for systems where PulseIn is unavailable or unreliable.

## Hardware diagnostic

Run the diagnostic before starting the web application. It starts Picamera2, waits for automatic exposure and white balance, captures one RGB frame, reads the DHT22 with bounded retries, prints JSON, and releases both devices.

```bash
uv run python main.py --check-hardware
```

Then start the local application:

```bash
uv run python main.py --serve
```

Open `http://127.0.0.1:5000/` on the Pi. To reach the dashboard from another device on the same trusted LAN, set `api.host` to `0.0.0.0`, restart the application, and open `http://<raspberry-pi-address>:5000/`. Do not expose this unauthenticated development service to the public internet.

## Common failures

- `Picamera2 is unavailable`: recreate the uv environment with `--system-site-packages` after installing `python3-picamera2`.
- No camera detected: shut down and reseat the CSI cable in the camera connector, not a display connector.
- DHT checksum or timeout errors: verify the pull-up resistor and wiring. Transient failures are retried automatically.
- Permission errors: ensure the service account can access the camera and GPIO devices on Raspberry Pi OS.
- Frequent DHT failures: keep captures at least two seconds apart and avoid long unshielded DATA wiring.

Primary implementation references are the [Raspberry Pi camera software documentation](https://www.raspberrypi.com/documentation/computers/camera_software.html), the [Picamera2 manual](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf), and the [Adafruit CircuitPython DHT documentation](https://docs.circuitpython.org/projects/dht/en/latest/).
