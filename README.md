# Kaizen Model using Edge Computing for Tomato Disease Detection

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Hardware Components](#3-hardware-components)
4. [Hardware Wiring](#4-hardware-wiring)
5. [Software Architecture](#5-software-architecture)
6. [Project File Structure](#6-project-file-structure)
7. [Disease Detection Pipeline](#7-disease-detection-pipeline)
8. [Data Flow](#8-data-flow)
9. [Database Schema](#9-database-schema)
10. [Getting Started](#10-getting-started)
11. [Installation](#11-installation)
12. [Configuration](#12-configuration)
13. [Usage](#13-usage)
14. [API Reference](#14-api-reference)
15. [Web Dashboard](#15-web-dashboard)
16. [Model Training](#16-model-training)
17. [Testing](#17-testing)
18. [Deployment](#18-deployment)
19. [Known Limitations](#19-known-limitations)
20. [License](#20-license)

---

## 1. Project Overview

This project presents the design and ongoing implementation of the **Kaizen Model**, an edge-computing-based tomato disease classification system built for continuous improvement on the Raspberry Pi 5. The target platform uses a **Raspberry Pi AI HAT+** to perform on-device neural network inference without continuous dependency on cloud services. The exact Hailo accelerator variant will be confirmed on the available hardware before the model is compiled and benchmarked.

Tomato leaf imagery is captured using the **Pi Camera Module 3**. Each accepted frame is preprocessed and supplied to a five-class MobileNetV2 image-classification model. Environmental readings, specifically temperature and relative humidity, are collected through a **DHT22 sensor** and correlated with classification events to provide additional context.

Results are persisted in a local SQLite database and made accessible through a REST API and a browser-based monitoring dashboard reachable over the local network. When a high-severity tomato disease is detected, the system triggers automated alerts. The Kaizen idea in the project name reflects the intended operational pattern: the deployed edge model can be reviewed, refined, and improved over time as new field cases become available.

### Objectives

- Classify five selected tomato diseases from leaf images using edge AI inference
- Monitor environmental conditions (temperature and humidity) relevant to tomato disease spread
- Provide farmers with a simple, low-cost, internet-independent tomato monitoring tool
- Log and export timestamped detection history for analysis and reporting
- Support the Kaizen-style improvement cycle through stored detections and reviewable outputs
- Evaluate classification quality and edge-inference performance on the installed AI HAT+

### Target Diseases

The initial model is limited to five tomato disease classes available in the **PlantVillage** tomato subset:

| Tomato Focus | Disease |
|------|---------|
| Tomato | Bacterial Spot, Early Blight, Late Blight, Leaf Mould, Septoria Leaf Spot |

This is a whole-image classification project. It does not predict bounding boxes or perform object detection. A result below the configured confidence threshold is stored as `uncertain`; it is not automatically interpreted as a healthy leaf because a healthy class is not included in the initial model.

### Current Implementation Status

The Python 3.11 environment and dependency groups are managed with `uv`. The repository currently contains the agreed architecture, configuration placeholders, and test placeholders. The application services, model-training scripts, simulation adapters, and executable tests are the next implementation milestones. Commands for components that are still planned are identified as such in this README.

---

## 2. System Architecture

The system is structured in four horizontal layers: hardware, core services, data, and presentation. The installed Hailo accelerator communicates with the Raspberry Pi over PCIe, providing low-latency tensor offloading for tomato disease inference.

```mermaid
graph TB
    subgraph HW ["Hardware Layer"]
        CAM["Pi Camera Module 3\n(12MP, HDR, Autofocus)"]
        DHT["DHT22 Sensor\n(Temp / Humidity)"]
        AIHAT["AI HAT+\n(Hailo accelerator)"]
        RPI["Raspberry Pi 5\n(ARM Cortex-A76 — 8GB RAM)"]

        CAM -->|"CSI-2 FPC"| RPI
        DHT -->|"GPIO4 (1-Wire)"| RPI
        RPI <-->|"PCIe Gen 3"| AIHAT
    end

    subgraph SVC ["Core Services Layer"]
        CS["Camera Service\n(Picamera2)"]
        SS["Sensor Service\n(Adafruit CircuitPython DHT)"]
        IS["Inference Service\n(HailoRT SDK)"]
    end

    subgraph DATA ["Data Layer"]
        PP["Preprocessing Pipeline\n(OpenCV / NumPy)"]
        DB[("SQLite Database\n(Detections / Sensor Readings)")]
        FS["File System\n(Captured & Annotated Images)"]
    end

    subgraph PRES ["Presentation Layer"]
        API["REST API\n(Flask-RESTful)"]
        WS["WebSocket\n(Flask-SocketIO)"]
        DASH["Web Dashboard\n(HTML / Chart.js)"]
        ALERT["Alert System\n(Email / SMS)"]
    end

    RPI --> CS
    RPI --> SS
    CS --> PP
    PP --> IS
    AIHAT -.->|"NPU Acceleration"| IS
    IS --> DB
    IS --> FS
    SS --> DB
    DB --> API
    DB --> WS
    API --> DASH
    WS --> DASH
    DB --> ALERT
```

---

## 3. Hardware Components

| # | Component | Specification | Role in System |
|---|-----------|---------------|----------------|
| 1 | Raspberry Pi 5 | 8GB LPDDR4X RAM, quad-core ARM Cortex-A76 @ 2.4GHz | Central processing unit, runs all software services |
| 2 | Raspberry Pi AI HAT+ | Installed Hailo variant to be confirmed before compilation | Hardware accelerator for neural network inference |
| 3 | Pi Camera Module 3 | Sony IMX708, 12MP, HDR, phase-detect autofocus, 120° FoV | Primary image capture for disease detection |
| 4 | DHT22 Sensor | ±0.5°C temperature, ±2–5% relative humidity, 0.5Hz sampling | Environmental monitoring |
| 5 | MicroSD Card | 64GB, UHS Speed Class 3 (V30), Application Class A2 | Operating system, application storage, image archive |
| 6 | Official 27W USB-C Power Supply | 5V / 5A output | Stable power delivery for Pi 5 + AI HAT+ combined load |
| 7 | Breadboards | 2× 400 tie-point solderless | Sensor circuit prototyping |
| 8 | Jumper Wires | 40-piece assortment (M-M, M-F, F-F) | Component interconnects |

> **Power Budget Note:** The Raspberry Pi 5 alone can draw up to 12W under load. The AI HAT+ adds further demand during inference. The official 27W supply (5V/5A) is the minimum recommended for stable operation of the combined system.

---

## 4. Hardware Wiring

### DHT22 Sensor Circuit

The DHT22 uses a single-wire protocol. A **10 kΩ pull-up resistor** is mandatory between the VCC and DATA lines to ensure reliable communication.

```mermaid
graph LR
    subgraph BREAD ["Breadboard"]
        RES["10kΩ Pull-up Resistor"]
    end

    subgraph DHT22 ["DHT22 Sensor (Left to Right)"]
        P1["Pin 1 — VCC"]
        P2["Pin 2 — DATA"]
        P3["Pin 3 — NC (not connected)"]
        P4["Pin 4 — GND"]
    end

    subgraph RPI5 ["Raspberry Pi 5 GPIO Header"]
        G1["Pin 1 — 3.3V Power"]
        G6["Pin 6 — Ground"]
        G7["Pin 7 — GPIO4"]
        CSI_PORT["CAM0 / CAM1\nCSI-2 Connector"]
    end

    subgraph CAMERA ["Pi Camera Module 3"]
        FPC["FPC Ribbon Cable"]
    end

    G1 -->|"3.3V"| P1
    P1 -->|"Pull-up"| RES
    RES -->|"Signal"| P2
    G7 -->|"GPIO4 Data"| P2
    G6 -->|"GND"| P4
    CSI_PORT -->|"15-pin FPC"| FPC
```

### GPIO Pin Mapping

| GPIO Header Pin | Signal | Connected To |
|-----------------|--------|-------------|
| Pin 1 (3.3V) | Power | DHT22 VCC |
| Pin 6 (GND) | Ground | DHT22 GND |
| Pin 7 (GPIO4) | Data | DHT22 DATA (via 10kΩ pull-up) |
| CAM0 CSI-2 | Camera data | Pi Camera Module 3 FPC |
| Hat connector (40-pin) | PCIe / Power | AI HAT+ bottom connector |

---

## 5. Software Architecture

The software follows a **layered service-oriented** design. Each service is independently runnable, communicates via internal Python interfaces, and can be tested in isolation.

```mermaid
graph TD
    subgraph Entry ["Entry Point"]
        MAIN["main.py\n(Orchestrator / Service Manager)"]
    end

    subgraph Services ["Core Services"]
        CS["CameraService\nsrc/camera/capture.py"]
        SS["SensorService\nsrc/sensors/dht22.py"]
        IS["InferenceService\nsrc/inference/hailo_runner.py"]
    end

    subgraph Processing ["Processing"]
        PRE["Preprocessor\nsrc/inference/preprocessor.py"]
        POST["Postprocessor\nsrc/inference/postprocessor.py"]
    end

    subgraph Persistence ["Persistence"]
        REPO["Repository\nsrc/database/repository.py"]
        ORM["ORM Models\nsrc/database/models.py"]
        DB[("detections.db\nSQLite")]
    end

    subgraph API ["API & Presentation"]
        FLASK["Flask App\nsrc/api/app.py"]
        ROUTES["Route Blueprints\nsrc/api/routes/"]
        SIO["SocketIO\nsrc/api/websocket.py"]
        TMPL["Jinja2 Templates\nsrc/dashboard/templates/"]
    end

    subgraph Alerts ["Notification"]
        EMAIL["EmailAlert\nsrc/alerts/email_alert.py"]
        SMS["SMSAlert\nsrc/alerts/sms_alert.py"]
    end

    MAIN --> CS
    MAIN --> SS
    MAIN --> FLASK
    CS --> PRE
    PRE --> IS
    IS --> POST
    POST --> REPO
    SS --> REPO
    REPO --> ORM
    ORM --> DB
    REPO --> FLASK
    FLASK --> ROUTES
    FLASK --> SIO
    ROUTES --> TMPL
    POST --> EMAIL
    POST --> SMS
```

---

## 6. Planned Project File Structure

The following structure is the implementation target. Some paths do not exist yet.

```
iot-crop-disease-detection/
│
├── src/                                   # All application source code
│   │
│   ├── camera/                            # Camera capture and streaming
│   │   ├── __init__.py
│   │   ├── capture.py                     # Single-shot image capture via Picamera2
│   │   └── stream.py                      # Continuous frame generator for inference loop
│   │
│   ├── sensors/                           # Environmental sensor interfaces
│   │   ├── __init__.py
│   │   └── dht22.py                       # DHT22 driver — temperature & humidity polling
│   │
│   ├── inference/                         # AI inference pipeline
│   │   ├── __init__.py
│   │   ├── hailo_runner.py                # HailoRT SDK wrapper — loads .hef, runs inference
│   │   ├── preprocessor.py                # Frame resize, normalise, tensor conversion
│   │   └── postprocessor.py               # Softmax, confidence filtering, class mapping
│   │
│   ├── database/                          # Data persistence layer
│   │   ├── __init__.py
│   │   ├── models.py                      # SQLAlchemy ORM table definitions
│   │   ├── schema.sql                     # Raw SQL schema (for reference / migration)
│   │   └── repository.py                  # CRUD operations — detections and sensor records
│   │
│   ├── api/                               # REST API and WebSocket server
│   │   ├── __init__.py
│   │   ├── app.py                         # Flask application factory (create_app)
│   │   ├── websocket.py                   # Flask-SocketIO real-time event handlers
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── detections.py              # GET /api/v1/detections endpoints
│   │       ├── sensors.py                 # GET /api/v1/sensors endpoints
│   │       ├── inference.py               # POST /api/v1/inference/trigger endpoint
│   │       └── system.py                  # GET /api/v1/system/health endpoint
│   │
│   ├── dashboard/                         # Browser-based monitoring UI
│   │   ├── static/
│   │   │   ├── css/
│   │   │   │   └── styles.css             # Dashboard stylesheet
│   │   │   └── js/
│   │   │       ├── dashboard.js           # Main UI logic, WebSocket client
│   │   │       └── charts.js              # Chart.js detection and sensor graphs
│   │   └── templates/
│   │       ├── base.html                  # Shared layout template
│   │       ├── index.html                 # Live monitoring dashboard view
│   │       ├── detections.html            # Detection history and image viewer
│   │       └── reports.html               # Data export and reporting view
│   │
│   ├── alerts/                            # Notification services
│   │   ├── __init__.py
│   │   ├── email_alert.py                 # SMTP email notification
│   │   └── sms_alert.py                   # SMS notification (via Twilio or similar)
│   │
│   └── utils/                             # Shared utilities
│       ├── __init__.py
│       ├── config.py                      # YAML configuration loader
│       ├── logger.py                      # Centralised logging setup
│       └── helpers.py                     # Image annotation, timestamp formatting, etc.
│
├── models/                                # AI model files
│   ├── hailo/
│   │   └── tomato_classifier.hef           # Compiled Hailo Executable Format model
│   └── training/
│       ├── dataset_prep.py                # Dataset download, split, and augmentation
│       ├── train.py                       # MobileNetV2 transfer-learning script
│       ├── evaluate.py                    # Accuracy, precision, recall, F1 evaluation
│       └── export_to_hailo.py             # ONNX → Hailo DFC compilation pipeline
│
├── data/                                  # Runtime data storage (git-ignored)
│   ├── captures/                          # Raw images from Pi Camera
│   ├── processed/                         # Preprocessed inference-ready images
│   ├── detections/                        # Labelled classification output images
│   ├── exports/                           # CSV and JSON report exports
│   └── detections.db                      # SQLite database file
│
├── tests/                                 # Full test suite
│   ├── unit/
│   │   ├── test_camera.py                 # Unit tests — CameraService
│   │   ├── test_dht22.py                  # Unit tests — SensorService
│   │   ├── test_preprocessor.py           # Unit tests — image preprocessing
│   │   ├── test_postprocessor.py          # Unit tests — output decoding
│   │   └── test_api.py                    # Unit tests — API endpoints
│   ├── integration/
│   │   ├── test_pipeline.py               # End-to-end capture → inference → store
│   │   └── test_database.py               # Database read/write integration tests
│   └── conftest.py                        # Pytest fixtures and shared test config
│
├── scripts/                               # Operational and setup scripts
│   ├── setup_system.sh                    # One-command system setup (apt, uv, config)
│   ├── install_hailo_sdk.sh               # Hailo PCIe driver + HailoRT installation
│   ├── start_services.sh                  # Launch all services via systemd or directly
│   ├── crop_disease_detection.service     # systemd unit file for auto-start on boot
│   └── run_benchmark.py                   # Inference throughput and latency benchmark
│
├── config/                                # Configuration files
│   ├── config.yaml                        # Main application configuration
│   ├── logging.yaml                       # Logging levels and handlers
│   └── diseases.yaml                      # Disease class labels, severity, and metadata
│
├── docs/                                  # Project documentation
│   ├── hardware_setup.md                  # Step-by-step hardware assembly guide
│   ├── software_setup.md                  # Detailed software installation guide
│   ├── api_reference.md                   # Full API endpoint documentation
│   ├── model_training.md                  # Dataset preparation and training guide
│   └── wiring_diagram.png                 # Exported wiring schematic
│
├── .env.example                           # Environment variable template
├── .gitignore                             # Git ignore rules
├── .python-version                        # Python version selected by uv
├── pyproject.toml                         # Project metadata and dependency groups
├── uv.lock                                # Reproducible dependency lockfile
├── main.py                                # Application entry point
└── README.md                              # This file
```

---

## 7. Disease Detection Pipeline

Each accepted tomato leaf image passes through a whole-image classification pipeline before a result is committed to the database. The same processing contract will be used by the desktop simulator, ONNX Runtime, and the Hailo hardware backend.

```mermaid
flowchart TD
    A(["Image Acquired\nPi Camera or simulation folder"])
    B["Stage 1: Quality Check\nReject unreadable or unsuitable input"]
    C["Stage 2: Preprocessing\nResize to 224 × 224\nConvert to RGB\nApply MobileNetV2 normalisation"]
    D["Stage 3: Classification\nProduce five class logits\nusing mock, ONNX, or Hailo backend"]
    E["Stage 4: Postprocessing\nApply softmax\nSelect highest probability\nMap class index to disease label"]
    F{"Confidence at least 0.70?"}
    G["Accepted Classification\nStore predicted disease and confidence"]
    H["Uncertain Classification\nStore result without claiming healthy"]
    I["Stage 5: Correlation\nJoin with nearest DHT22 reading"]
    P["Stage 6: Persistence\nWrite ClassificationRecord to SQLite"]
    Q{"Severity is High?"}
    J["Alert Dispatcher\nSend Email / SMS notification\nwith tomato and disease details"]
    K["WebSocket Broadcast\nPush update to connected\ndashboard clients in real time"]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F -- "Yes" --> G
    F -- "No" --> H
    G --> I
    H --> I
    I --> P
    P --> Q
    Q -- "Yes" --> J
    Q -- "No" --> K
    J --> K
```

---

## 8. Data Flow

The following sequence diagram shows the interaction between all system components during a standard detection cycle, and a separate dashboard polling cycle.

```mermaid
sequenceDiagram
    participant CAM as Pi Camera Module 3
    participant CS  as Camera Service
    participant PP  as Preprocessor
    participant NPU as AI HAT+ (Hailo NPU)
    participant POST as Postprocessor
    participant SS  as Sensor Service
    participant DB  as SQLite Database
    participant API as REST API
    participant WS  as WebSocket
    participant UI  as Web Dashboard

    loop Detection Cycle (every N seconds)
        CS  ->> CAM  : capture_frame()
        CAM -->> CS  : raw_image (JPEG / numpy array)
        CS  ->>  PP  : preprocess(raw_image)
        PP  -->> CS  : normalised_tensor [1, 3, 224, 224]
        CS  ->>  NPU : infer(tensor)
        NPU -->> POST: five_class_logits
        POST -->> DB : INSERT ClassificationRecord

        SS  ->>  SS  : read_dht22()
        SS  ->>  DB  : INSERT SensorRecord
    end

    UI  ->> API : GET /api/v1/detections/latest
    API ->>  DB : SELECT latest record
    DB  -->> API: ClassificationRecord row
    API -->> UI : JSON response

    POST -->> WS : emit("new_detection", payload)
    WS  -->> UI  : push real-time update
```

---

## 9. Database Schema

```mermaid
erDiagram
    CLASSIFICATION_RECORD {
        INTEGER id PK
        TEXT    image_path
        TEXT    disease_label
        REAL    confidence
        TEXT    prediction_status
        INTEGER severity
        TEXT    model_version
        REAL    processing_time_ms
        DATETIME captured_at
        INTEGER sensor_reading_id FK
    }

    SENSOR_READING {
        INTEGER  id PK
        REAL     temperature_c
        REAL     humidity_pct
        DATETIME recorded_at
    }

    ALERT_LOG {
        INTEGER  id PK
        INTEGER  classification_record_id FK
        TEXT     alert_type
        TEXT     recipient
        TEXT     status
        DATETIME sent_at
    }

    CLASSIFICATION_RECORD ||--o| SENSOR_READING : "correlates with"
    CLASSIFICATION_RECORD ||--o{ ALERT_LOG      : "may trigger"
```

---

## 10. Getting Started

### Prerequisites

| Requirement | Minimum Version |
|-------------|----------------|
| Raspberry Pi OS (64-bit) | Bookworm (Debian 12) |
| Python | 3.11 |
| HailoRT SDK | 4.18.0 |
| Git | 2.x |

The AI HAT+ must be installed on the Raspberry Pi 5 before powering on. Hailo PCIe drivers are installed separately — see [docs/hardware_setup.md](docs/hardware_setup.md).

### Hardware Assembly Order

1. With the Pi powered **off**, attach the AI HAT+ to the 40-pin GPIO header of the Raspberry Pi 5. Secure it using the included standoffs and screws. The AI HAT+ communicates via the PCIe Gen 3 interface routed through the HAT connector.
2. Connect the Pi Camera Module 3 to the **CAM0** CSI-2 connector using the supplied 15-pin FPC ribbon cable. Ensure the cable is seated fully and the locking tab is closed.
3. On the breadboard, insert the DHT22 sensor. Wire the circuit as follows:

    | DHT22 Pin | Connection |
    |-----------|-----------|
    | Pin 1 (VCC) | Raspberry Pi Pin 1 (3.3V) |
    | Pin 2 (DATA) | Raspberry Pi Pin 7 (GPIO4) |
    | Pin 4 (GND) | Raspberry Pi Pin 6 (GND) |

    Place a **10 kΩ resistor** between DHT22 Pin 1 (VCC) and Pin 2 (DATA) on the breadboard.

4. Connect the Official 27W USB-C power supply to the Raspberry Pi 5 USB-C port last, after all components are secured.

---

## 11. Installation

### Step 1 — Clone the Repository

```bash
git clone https://github.com/thetruesammyjay/iot-crop-disease-detection.git
cd iot-crop-disease-detection
```

### Step 2: Create the uv Environment

```bash
# Install uv if it is not already available
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the declared Python version and synchronize dependencies
uv python install 3.11
uv sync --extra simulation
```

`uv` creates and manages `.venv` automatically. Activating the environment is optional because project commands can be executed with `uv run`. The first successful synchronization generates `uv.lock`; commit that file so development and deployment use the same resolved versions.

On the Raspberry Pi, install Picamera2 and HailoRT using the supported Raspberry Pi OS packages first. These hardware libraries are not installed from PyPI. Create the uv environment with access to the operating-system Python packages, then synchronize the project dependencies:

```bash
uv venv --python /usr/bin/python3 --system-site-packages
uv sync --no-dev --extra hardware
```

The `simulation` extra installs ONNX Runtime for hardware-independent inference. Use `uv sync --extra training` on the machine used to prepare and train MobileNetV2.

### Step 3: Verify the Environment

```bash
uv run python --version
uv lock --check
uv run pytest
```

Pytest currently reports no collected tests because the committed test modules are placeholders. This will change when the first simulation-ready pipeline is implemented.

### Raspberry Pi Hardware Environment

On the Raspberry Pi, install Picamera2, the Hailo PCIe driver, HailoRT, and the hardware-specific Python packages from their supported operating-system sources. The hardware setup scripts described in the planned project structure have not been implemented yet.

---

## 12. Configuration

All tunable parameters are in `config/config.yaml`:

```yaml
camera:
  resolution: [1920, 1080]       # Capture resolution (width x height)
  capture_interval_s: 5          # Seconds between detection cycles
  rotation: 0                    # Camera rotation: 0, 90, 180, or 270
  save_raw_frames: false         # Store every raw frame to data/captures/

sensor:
  gpio_pin: 4                    # BCM GPIO pin number for DHT22 DATA line
  read_interval_s: 30            # Seconds between sensor polls
  temperature_unit: "celsius"    # "celsius" or "fahrenheit"

inference:
  backend: "simulation"          # simulation, onnx, or hailo
  onnx_model_path: "models/onnx/tomato_mobilenet_v2.onnx"
  hailo_model_path: "models/hailo/tomato_classifier.hef"
  confidence_threshold: 0.70     # Minimum confidence for an accepted class
  input_size: [224, 224]         # MobileNetV2 input dimensions
  class_count: 5
  device_id: 0                   # Hailo PCIe device index

simulation:
  image_directory: "data/simulation/images"
  temperature_range_c: [20.0, 35.0]
  humidity_range_pct: [45.0, 90.0]

database:
  path: "data/detections.db"
  retention_days: 90             # Auto-delete records older than this

api:
  host: "0.0.0.0"
  port: 5000
  debug: false
  cors_enabled: true

alerts:
  enabled: true
  severity_threshold: "high"     # "low", "medium", or "high"
  cooldown_minutes: 10           # Minimum gap between repeated alerts
  email:
    smtp_host: "smtp.example.com"
    smtp_port: 587
    smtp_user: ""
    recipient: "farmer@example.com"
  sms:
    enabled: false
    provider: "twilio"
    to_number: "+2348000000000"
```

Disease class labels and their severity ratings are defined separately in `config/diseases.yaml`.

---

## 13. Usage

The following command-line interface is the target for the first implementation milestone and is not functional yet:

```bash
uv run python main.py --init-db
uv run python main.py --simulate
uv run python main.py --simulate --image path/to/tomato_leaf.jpg
```

### Available Command-Line Flags

| Flag | Description |
|------|-------------|
| `--init-db` | Initialise or reset the SQLite database |
| `--simulate` | Use local images, generated sensor readings, and a simulated or ONNX inference backend |
| `--image path` | Classify one local tomato leaf image in simulation mode |
| `--config path/to/config.yaml` | Use an alternative config file |
| `--no-alerts` | Disable alert dispatching for this session |
| `--benchmark` | Run inference benchmark and exit |
| `--capture-only` | Run camera capture without inference |

### Access the Dashboard

From any device on the same local network, open a browser and navigate to:

```
http://<raspberry-pi-ip-address>:5000
```

Find the Pi's IP address by running `hostname -I` on the device.

---

## 14. API Reference

The API is planned but not implemented yet. All endpoints will be prefixed with `/api/v1`, responses will use JSON, and timestamps will follow ISO 8601 format.

### Detections

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/detections` | Paginated list of all detection records |
| `GET` | `/detections/latest` | The most recent detection result |
| `GET` | `/detections/<int:id>` | Fetch a single detection record by ID |
| `GET` | `/detections/<int:id>/image` | Serve the annotated detection image |
| `DELETE` | `/detections/<int:id>` | Delete a detection record |

**Query Parameters for `/detections`:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | int | Page number (default: 1) |
| `per_page` | int | Records per page (default: 20, max: 100) |
| `disease` | string | Filter by disease label |
| `from` | ISO date | Filter records from this date |
| `to` | ISO date | Filter records up to this date |

### Sensors

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/sensors/latest` | Most recent DHT22 reading |
| `GET` | `/sensors/history` | Historical readings (supports `from` / `to` params) |

### Inference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/inference/trigger` | Manually trigger a single detection cycle |

### Reports

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/reports/export?format=csv` | Export all detections as CSV |
| `GET` | `/reports/export?format=json` | Export all detections as JSON |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/system/health` | System health: CPU, memory, temperature, disk |
| `GET` | `/system/info` | Software versions, model info, uptime |

---

## 15. Web Dashboard

The dashboard is a server-rendered web interface built with Jinja2 templates, plain JavaScript, and Chart.js. It updates in real time using WebSocket connections.

```mermaid
graph LR
    subgraph Pages ["Dashboard Pages"]
        IDX["/ — Live Monitor\nLatest detection\nLive sensor readings\nReal-time confidence feed"]
        DET["/detections — History\nPaginated detection log\nAnnotated image viewer\nFilter by date / disease"]
        REP["/reports — Reports\nCSV / JSON export\nDetection summary charts\nEnvironmental trend graphs"]
    end

    subgraph Realtime ["Real-Time Channel"]
        SIO["WebSocket (SocketIO)\nnew_detection event\nnew_sensor_reading event\nsystem_status event"]
    end

    IDX <-->|"Live updates"| SIO
```

---

## 16. Model Training

The planned MobileNetV2 classification model will be trained on five tomato disease classes derived from the **PlantVillage** dataset and then compiled to Hailo's `.hef` format using the **Hailo Dataflow Compiler (DFC)**.

```mermaid
flowchart LR
    A["Tomato Disease Dataset\nPlantVillage tomato subset\nLabelled leaf images"] --> B["Data Preparation\nmodels/training/dataset_prep.py\nAugmentation, 80/10/10 split"]
    B --> C["Model Training\nmodels/training/train.py\nMobileNetV2 transfer learning\nPyTorch / Torchvision"]
    C --> D["Evaluation\nmodels/training/evaluate.py\nAccuracy, Precision, Recall, F1"]
    D --> E["ONNX Export\nFive-class MobileNetV2 model"]
    E --> F["Hailo DFC Compilation\nmodels/training/export_to_hailo.py\nQuantisation (INT8)\nTarget installed Hailo variant"]
    F --> G["tomato_classifier.hef\nmodels/hailo/\nDeployed to AI HAT+"]
```

### Training Requirements

Training will be performed on a separate machine, preferably one with a CUDA-capable GPU. The commands below describe the intended workflow; the referenced training scripts have not been implemented yet.

```bash
# Synchronize the training dependency set
uv sync --extra training

# Prepare dataset
uv run python models/training/dataset_prep.py --dataset plantvillage --output data/

# Train the model
uv run python models/training/train.py --architecture mobilenet_v2 --epochs 30 --batch-size 32

# Evaluate
uv run python models/training/evaluate.py --checkpoint models/training/best_model.pth

# Export to ONNX
uv run python models/training/train.py --export-onnx models/training/tomato_mobilenet_v2.onnx

# Compile to Hailo HEF (requires Hailo DFC installed)
uv run python models/training/export_to_hailo.py --onnx models/training/tomato_mobilenet_v2.onnx --output models/hailo/
```

Refer to [docs/model_training.md](docs/model_training.md) for the complete guide, including Hailo DFC installation and quantisation calibration.

---

## 17. Testing

The project uses **pytest** for unit and integration testing. Test files currently exist as placeholders and do not yet contain executable tests. Hardware-dependent tests will use controlled mocks so that camera, GPIO, sensor, and inference behavior can be checked before physical hardware is available.

### Run All Tests

```bash
uv run pytest tests/ -v
```

### Run by Category

```bash
# Unit tests only
uv run pytest tests/unit/ -v

# Integration tests only
uv run pytest tests/integration/ -v

# Single test file
uv run pytest tests/unit/test_inference.py -v
```

### Generate Coverage Report

```bash
uv run pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html in a browser
```

### Test Structure

```mermaid
graph TD
    CONF["conftest.py\nFixtures: mock_camera, mock_dht22,\nmock_classifier, test_db"]
    CONF --> U1["test_camera.py\nframe capture, stream init"]
    CONF --> U2["test_dht22.py\nreading parse, error handling"]
    CONF --> U3["test_preprocessor.py\nresize, normalise, tensor shape"]
    CONF --> U4["test_postprocessor.py\nsoftmax, confidence threshold, label map"]
    CONF --> U5["test_api.py\nendpoint status codes, JSON schema"]
    CONF --> I1["test_pipeline.py\nfull capture → infer → store cycle"]
    CONF --> I2["test_database.py\ninsert, query, pagination, retention"]
```

---

## 18. Deployment

The system is designed for future **standalone edge deployment** on the Raspberry Pi 5 at the point of use, such as a farm, greenhouse, or field station. The deployment scripts and systemd service described below are planned and will only be used after the simulation, ONNX, and hardware integration stages have passed their tests.

### Register as a systemd Service

To start the application automatically on boot:

```bash
sudo cp scripts/crop_disease_detection.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable crop_disease_detection.service
sudo systemctl start crop_disease_detection.service
```

Check status:

```bash
sudo systemctl status crop_disease_detection.service
```

### Deployment Checklist

```mermaid
flowchart TD
    A["Set debug: false in config.yaml"] --> B["Set a strong SECRET_KEY in .env"]
    B --> C["Restrict dashboard to LAN only\n(bind to local interface if needed)"]
    C --> D["Enable log rotation\nsudo logrotate config in /etc/logrotate.d/"]
    D --> E["Register systemd service\nfor auto-start on boot"]
    E --> F["Set database retention_days\nto manage disk space"]
    F --> G["Verify AI HAT+ PCIe link\nhailortcli fw-control identify"]
    G --> H["Run benchmark script\nuv run python scripts/run_benchmark.py"]
    H --> I["System ready for deployment"]
```

---

## 19. Known Limitations

| Limitation | Detail |
|------------|--------|
| Single camera field of view | The Pi Camera Module 3 covers a fixed field of view. Multiple cameras would require a USB hub or second Pi. |
| DHT22 sampling rate | The DHT22 has a maximum sampling rate of 0.5 Hz (one reading every 2 seconds). Rapid environmental changes may not be captured immediately. |
| Model generalisation | The initial tomato model is trained on PlantVillage-style images, which use controlled lab conditions. Performance may degrade on images taken in natural outdoor lighting conditions without re-training or fine-tuning. |
| SQLite concurrency | SQLite is suitable for single-node use. If concurrent write load increases significantly, migration to PostgreSQL should be considered. |
| Alert delivery | Email and SMS alerts require at least periodic network access. They will queue locally and retry if the network is temporarily unavailable. |
| MicroSD card longevity | Continuous high-frequency writes (raw image captures) can wear flash storage. V30/A2 rated cards are recommended, and raw frame saving should be disabled in production unless required. |

---

## 20. License

This project is submitted as a final year project for the degree of Bachelor of Science in Software Engineering.

```
MIT License

Copyright (c) 2026 sammyjayisthename Inc

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```
