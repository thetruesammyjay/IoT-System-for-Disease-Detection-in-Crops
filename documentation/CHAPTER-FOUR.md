# CHAPTER FOUR

# SYSTEM DESIGN AND IMPLEMENTATION

## 4.1 Introduction

Chapter Three explained how the study would be carried out. This chapter moves from that plan to the system that was actually designed and implemented. The work brings together the software components, data structures, interfaces, model artefacts, and operating procedures needed to classify five tomato leaf diseases. It also covers the collection of temperature and humidity readings, local storage of each result, and access to the records through a browser dashboard and REST application programming interface.

A practical concern throughout development was the absence of the physical components during part of the work. For that reason, the system was built in modules. Desktop simulation and Raspberry Pi operation use the same classification pipeline, but they obtain their inputs from different adapters. Simulation uses generated images and repeatable environmental readings, whereas the physical system will use the Pi Camera Module 3 and DHT22. The inference layer follows the same approach: the trained MobileNetV2 model already runs through ONNX Runtime, while Hailo deployment remains a separate task to be completed after the exact AI HAT+ variant is confirmed.

The discussion begins with the architectural, use case, sequence, activity, deployment, and database designs. It then follows the implementation from image acquisition and preprocessing to classification, environmental sensing, storage, continuous monitoring, the REST API, and the dashboard. The final sections present the completed model and software tests before setting out the physical tests that are still required. Keeping these results separate is important because a simulated or mocked hardware test is useful evidence of software readiness, but it is not the same as a test conducted on the completed physical prototype.

## 4.2 System Design

The system was designed to carry out disease classification and environmental monitoring on a local edge device. Hardware access, inference, post-processing, storage, monitoring, and presentation were therefore given separate responsibilities. This arrangement made development easier to manage: each part could be tested on its own, and a simulated input could later be replaced by a physical adapter without rewriting the rest of the application.

### 4.2.1 Architectural Design

The architectural model from Chapter Three provided the starting point for implementation. It divides the system into a hardware layer, a local software-services layer, and a local-network client layer. Within this arrangement, the Raspberry Pi 5 hosts and coordinates the application. The Pi Camera Module 3 supplies tomato leaf images, the DHT22 provides environmental measurements, and the optional AI HAT+ is reserved for accelerated inference.

[Open the editable draw.io architectural diagram](diagrams/CHAPTER-FOUR-ARCHITECTURAL-DIAGRAM.drawio)

![Architectural design of the tomato disease detection system](figures/FIGURE-4.1-ARCHITECTURAL-DESIGN.png)

**Figure 4.1: Architectural Design of the Tomato Disease Detection System.**  
**Source:** Researcher's design, rebuilt in draw.io from the architectural model presented in Chapter Three.

As illustrated in Figure 4.1, the main workflow remains on the local device. The monitoring service requests an image and hands it to the inference pipeline. After preprocessing and classification, the pipeline reads the environmental sensor and saves both parts of the result in SQLite. The REST API makes those stored records and the monitoring controls available to the dashboard. Consequently, classification, sensing, storage, and local reporting can continue without a permanent internet connection.

At present, the application supports simulated inference and the trained ONNX model. The Hailo NPU remains in the diagram because it is part of the intended deployment, although the Hailo executable model and runtime adapter are not yet complete. This staged approach allows the camera and DHT22 to be connected and checked before accelerator-specific work begins. Initial hardware tests can therefore use simulated inference or run the ONNX model on the Raspberry Pi CPU.

### 4.2.2 Use Case Design

The use case model describes what the main users expect to do with the system. A Farmer or Operator needs to view current classifications, check earlier records, observe environmental readings, and export reports. Administrative work includes controlling the monitoring service, changing configuration, and checking whether the application is available. The editable diagram prepared in Chapter Three is reused here because these responsibilities still define the system boundary.

[Open the editable draw.io use case diagram](diagrams/CHAPTER-THREE-USE-CASE-DIAGRAM.drawio)

![Use case diagram of the tomato disease detection system](figures/FIGURE-4.2-USE-CASE-DIAGRAM.png)

**Figure 4.2: Use Case Diagram of the Tomato Disease Detection System.**  
**Source:** Reused from the researcher's draw.io use case model in Chapter Three.

The diagram separates the functions that are already available from those that belong to the complete target system. The dashboard currently provides service status, recent detection history, environmental trends, manual inference, and monitoring controls, while the API supports CSV and JSON export. Alert delivery and advanced administrative configuration are still planned. Their presence in the use case model records the intended scope; it does not imply that those functions have already been deployed.

### 4.2.3 Processing Sequence

The sequence model follows one result from capture to display. A cycle may begin automatically through continuous monitoring or manually through the REST API. In either case, the service prevents overlapping runs so that two classifications cannot compete for the same camera, sensor, or pipeline at the same time.

[Open the editable draw.io sequence diagram](diagrams/CHAPTER-FOUR-SEQUENCE-DIAGRAM.drawio)

![Sequence diagram for classification and reporting](figures/FIGURE-4.3-SEQUENCE-DIAGRAM.png)

**Figure 4.3: Sequence Diagram for Classification and Reporting.**  
**Source:** Researcher's implementation design. Created using draw.io and informed by the sequence model in Chapter Three.

One important detail in Figure 4.3 is that storage is part of the cycle, not an afterthought. The service does not report a classification as complete until the prediction and its sensor reading have been committed to the database. The dashboard never communicates directly with the camera, model, or DHT22; it reads validated records through the API. This keeps the user interface independent of the hardware-facing code.

### 4.2.4 Activity and Control Flow

The activity model focuses on the decisions made during a monitoring cycle. Before a result is stored, the service checks its current state, prepares the image, runs inference, evaluates confidence, reads the sensor, and handles any error that occurs. A prediction is accepted only when its highest softmax probability reaches the configured threshold of 0.70. Lower-confidence predictions are kept as uncertain, which is safer than discarding them or presenting them as reliable diagnoses.

[Open the editable draw.io activity diagram](diagrams/CHAPTER-FOUR-ACTIVITY-DIAGRAM.drawio)

![Activity diagram for a monitoring cycle](figures/FIGURE-4.4-ACTIVITY-DIAGRAM.png)

**Figure 4.4: Activity Diagram for a Monitoring Cycle.**  
**Source:** Researcher's implementation design. Created using draw.io and informed by the activity model in Chapter Three.

Several safeguards are visible in Figure 4.4. An image must be available and large enough to process, the classifier must return five finite values, and the sensor reading must be complete and physically plausible. The database transaction must also succeed before the cycle is counted as complete. If any of these steps fails, the monitoring status retains the error so that the operator can see it on the dashboard.

### 4.2.5 Deployment Design

The deployment model places each software responsibility on its intended physical node. The model deliberately separates the working application services from the Hailo acceleration path that is still pending.

[Open the editable draw.io deployment diagram](diagrams/CHAPTER-FOUR-DEPLOYMENT-DIAGRAM.drawio)

![Deployment diagram of the tomato disease detection system](figures/FIGURE-4.5-DEPLOYMENT-DIAGRAM.png)

**Figure 4.5: Deployment Diagram of the Tomato Disease Detection System.**  
**Source:** Researcher's design. Created using draw.io.

In the intended installation, the Python application, Flask API, dashboard, and SQLite database all run on the Raspberry Pi 5. The Camera Module 3 connects through CSI, while the DHT22 data line uses BCM GPIO4. A farmer can open the dashboard from a phone or computer on the same trusted local network. The dashed line to the AI HAT+ marks the proposed PCIe and HailoRT path. Until that path is ready, ONNX Runtime provides a workable CPU-based inference option on the Pi.

## 4.3 Database Design

Each classification needs to remain connected to the environmental conditions observed during the same cycle. The database was designed around that requirement. SQLite is a good fit for the prototype because it is lightweight, file-based, supports transactions, and runs comfortably on a single edge device. SQLAlchemy creates the schema and handles database operations, which avoids scattering raw SQL statements across the application.

### 4.3.1 Entity-Relationship Design

The working schema contains two tables, `sensor_readings` and `classification_records`. Every classification record carries a required foreign key to one sensor reading. Chapter Three proposed an additional alert log, but that table has not been created because notification delivery is still future work. The entity-relationship diagram below therefore represents the database that exists now, not every entity proposed for the final system.

[Open the editable draw.io entity-relationship diagram](diagrams/CHAPTER-FOUR-ERD.drawio)

![Entity-relationship diagram of the implemented SQLite database](figures/FIGURE-4.6-DATABASE-ERD.png)

**Figure 4.6: Entity-Relationship Diagram of the Implemented SQLite Database.**  
**Source:** Researcher's design, rebuilt in draw.io from the database model in Chapter Three and aligned with the implemented schema.

The relationship in Figure 4.6 is intentionally simple: one classification is stored with one contextual sensor reading. All five class probabilities are retained as JSON text, allowing a prediction to be examined later rather than preserving only the winning label. The `model_version` field makes records traceable when the classifier changes, and `processing_time_ms` supports later performance analysis. Separate timestamps record when the image was processed and when the environmental reading was taken.

### 4.3.2 Data Dictionary

The fields used by both tables are listed in Table 4.1. Primary keys are generated automatically, and the sensor foreign key is indexed to make joined retrieval more efficient. Reporting values are stored at the time of classification, so opening an old record does not require the model to run again.

| Table | Field | Type | Purpose |
|---|---|---|---|
| `sensor_readings` | `id` | Integer, primary key | Uniquely identifies the environmental reading |
| `sensor_readings` | `temperature_c` | Float | Stores temperature in degrees Celsius |
| `sensor_readings` | `humidity_pct` | Float | Stores relative humidity as a percentage |
| `sensor_readings` | `recorded_at` | DateTime | Records when the sensor measurement was obtained |
| `classification_records` | `id` | Integer, primary key | Uniquely identifies the classification |
| `classification_records` | `image_path` | Text | Stores the physical, local, camera, or simulation image identifier |
| `classification_records` | `disease_label` | String | Stores the selected tomato disease label |
| `classification_records` | `confidence` | Float | Stores the highest predicted probability |
| `classification_records` | `prediction_status` | String | Distinguishes accepted and uncertain predictions |
| `classification_records` | `severity` | String | Stores the configured alert priority or `unassigned` |
| `classification_records` | `probabilities_json` | Text | Stores probabilities for all five classes |
| `classification_records` | `model_version` | String | Identifies the classifier version used |
| `classification_records` | `processing_time_ms` | Float | Stores end-to-end pipeline processing time |
| `classification_records` | `captured_at` | DateTime | Records the classification-cycle timestamp |
| `classification_records` | `sensor_reading_id` | Integer, foreign key | Links the classification to its sensor reading |

**Table 4.1: Data Dictionary for the Implemented Database.**

Together, these fields preserve information for both the user and the researcher. The disease label and confidence are immediately understandable on the dashboard, while the full probability output, model version, processing time, and timestamps are useful during evaluation. Both rows are written in one transaction. If either write fails, the operation is not treated as a complete classification, which avoids leaving a record without its environmental context.

## 4.4 System Implementation

The application was implemented in Python 3.11 and organised into packages for the API, camera, database, inference, monitoring, sensors, and configuration. The same domain objects are shared between these packages to maintain a consistent representation of captured images, sensor measurements, classification outcomes, and stored records. Dependencies and development commands are managed using `uv` through `pyproject.toml` and `uv.lock`.

### 4.4.1 Image Acquisition Implementation

Two interchangeable image sources were implemented. `GeneratedImageSource` creates repeatable synthetic leaf-like images for automated tests and continuous desktop simulation. The local-image loader reads a supplied image fully into memory and closes its file handle, making it suitable for testing the actual ONNX model with PlantVillage images.

`PiCameraSource` implements physical image capture through Picamera2. During initialisation, it creates a still-image configuration using the configured resolution and RGB888 format, starts the camera, and waits for the configured warm-up period. Each capture is converted to an RGB PIL image and may be rotated by 0, 90, 180, or 270 degrees. Captures can either be saved as timestamped JPEG files or represented by a unique `camera://picamera2/` identifier. The adapter also releases the camera safely when monitoring stops.

| Image source | Input | Output | Intended use |
|---|---|---|---|
| Generated source | Configured width, height, and sequence | Synthetic RGB image and simulation identifier | Automated and desktop simulation testing |
| Local-image loader | JPEG or other PIL-supported file | Fully loaded RGB-compatible image | Testing the trained ONNX model with labelled images |
| Pi Camera adapter | Camera Module 3 through Picamera2 | RGB image and camera identifier or saved JPEG path | Physical Raspberry Pi monitoring |

**Table 4.2: Implemented Image Acquisition Sources.**

These three sources supported a gradual move from software-only testing to physical integration. The generated image checks that the application is wired together correctly without requiring a camera or dataset. A local labelled image exercises the real model, and the Pi Camera adapter takes over when the physical camera is available. Because all three return the same captured-image object, the rest of the pipeline does not need to know which source was used.

### 4.4.2 Environmental Sensor Implementation

Environmental sensing was also implemented through interchangeable adapters. `SimulatedDHT22` generates repeatable temperature and relative-humidity values within configured ranges. This makes repeated tests deterministic and enables the complete persistence and dashboard paths to operate on a computer without GPIO hardware.

`DHT22Sensor` resolves the configured BCM pin through the Adafruit `board` library and uses `adafruit_dht.DHT22` to obtain physical values. Because DHT22 sensors may produce temporary checksum or timing errors, the adapter performs a bounded number of retries with a configurable delay. It rejects missing, non-finite, or out-of-range values and rounds valid readings to two decimal places. The GPIO device is released when the service is closed.

| Sensor feature | Implemented behaviour |
|---|---|
| Default pin | BCM GPIO4, represented as `board.D4` |
| Retry policy | Three attempts with a two-second delay by default |
| Temperature validation | From -40 to 80 degrees Celsius |
| Humidity validation | From 0 to 100 percent relative humidity |
| Simulation range | 20 to 35 degrees Celsius and 45 to 90 percent humidity |
| Resource handling | Idempotent close operation releases the GPIO device |

**Table 4.3: DHT22 Sensor Implementation Rules.**

The rules in Table 4.3 keep raw driver values from entering the rest of the application unchecked. The monitoring cycle receives a validated `SensorMeasurement`, and incomplete or implausible readings produce an error instead of being stored beside a disease prediction. The remaining question is measurement accuracy, which can only be assessed after the physical DHT22 is compared with a reference thermometer and hygrometer.

### 4.4.3 Image Preprocessing and Classification

The preprocessing service converts each input into the format expected by MobileNetV2. Images smaller than 32 pixels in either dimension are rejected. Valid images are converted to RGB, resized to 224 by 224 pixels using bilinear interpolation, scaled to the range from zero to one, and normalised using the ImageNet channel means and standard deviations. The image array is transposed from height-width-channel order to a contiguous float32 tensor with shape `1 x 3 x 224 x 224`.

The ONNX classifier validates the exported model against its metadata before inference. The metadata records the architecture, model version, class names, class-to-index mapping, input dimensions, normalisation values, ONNX input and output names, opset version, and file hash. This contract prevents an incompatible or modified model from being loaded unnoticed. ONNX Runtime returns five logits, one for each configured disease class.

Post-processing applies a numerically stable softmax function to the logits and selects the class with the highest probability. If the selected probability is at least 0.70, the result is marked `accepted` and receives the severity configured for that disease. Otherwise, the result is marked `uncertain`, and severity becomes `unassigned`. The five retained classes are Bacterial Spot, Early Blight, Late Blight, Leaf Mould, and Septoria Leaf Spot.

### 4.4.4 Continuous Monitoring Implementation

`ContinuousMonitoringService` performs repeated classification cycles at a configurable interval. The default interval is five seconds, which is suitable for initial simulation and respects the DHT22's comparatively slow sampling behaviour. A background thread controls repeated execution, while thread locks protect status updates and prevent overlapping cycles.

The service records whether monitoring is running, whether a cycle is active, the number of completed, failed, and skipped cycles, the start and completion times of the latest cycle, the latest stored record identifier, and the latest error message. Start and stop operations are idempotent, meaning that repeated requests do not create duplicate monitoring threads or produce invalid states. Manual inference uses the same `run_once` operation and therefore follows the same capture, classification, sensing, and storage workflow as automatic monitoring.

### 4.4.5 Persistence Implementation

The classification pipeline measures processing time from preprocessing through sensor acquisition and passes the completed outcome to `ClassificationRepository`. The repository creates the SQLite schema if it does not exist and uses a transaction to save the sensor reading followed by its classification record. It provides methods for retrieving the latest result, retrieving a record by identifier, filtering and paginating classifications, querying sensor history, counting records, and checking database availability.

Filtering supports disease label, prediction status, start time, and end time. Classification pages are limited to 100 records per request, sensor pages are limited to 500 records, and report export is capped at 10,000 records. These limits protect the local service from accidentally loading an unrestricted history into memory.

### 4.4.6 REST API Implementation

The Flask application provides local programmatic access to system state, monitoring controls, detections, sensor readings, and report exports. Query parameters are validated before repository access, and empty resources return appropriate HTTP responses. Table 4.4 lists the implemented endpoints.

| Method | Endpoint | Function |
|---|---|---|
| GET | `/` | Serves the monitoring dashboard |
| GET | `/api/v1/system/health` | Reports service and database health |
| GET | `/api/v1/system/info` | Reports record count and monitoring availability |
| GET | `/api/v1/detections/latest` | Returns the latest stored classification |
| GET | `/api/v1/detections/{id}` | Returns one classification by identifier |
| GET | `/api/v1/detections` | Lists filtered and paginated classifications |
| GET | `/api/v1/sensors/latest` | Returns the latest sensor reading |
| GET | `/api/v1/sensors/history` | Lists paginated sensor history |
| POST | `/api/v1/inference/trigger` | Runs one monitoring and inference cycle |
| POST | `/api/v1/inference/upload` | Validates and classifies a user-selected leaf image |
| GET | `/api/v1/monitoring/status` | Returns monitoring counters and state |
| POST | `/api/v1/monitoring/start` | Starts continuous monitoring |
| POST | `/api/v1/monitoring/stop` | Stops continuous monitoring |
| GET | `/api/v1/reports/export` | Exports matching records as CSV or JSON |

**Table 4.4: Implemented REST API Endpoints.**

The endpoint set serves two purposes. Read requests expose stored evidence, while the inference and monitoring requests allow an operator to upload a leaf image, start or stop monitoring, or trigger local acquisition. Uploaded content is limited to JPEG, PNG, and WebP images. The server checks the actual image content, applies a size limit, converts valid input to RGB, and sends it through the same locked pipeline used by camera captures. At this stage, the application has no authentication and is intended only for a trusted local network. Public exposure would require authentication, encrypted transport, and a more carefully hardened deployment.

### 4.4.7 Dashboard Implementation

The dashboard provides a browser-based view of system health, monitoring status, the latest disease classification, recent detection history, and temperature and humidity trends. It also includes a leaf-inspection area where an operator can select or drag a tomato leaf photograph, preview it, and request disease analysis. The resulting disease label and confidence are shown beside the image, while the complete result is added to the latest-classification panel and detection history. Controls for starting or stopping monitoring and triggering one immediate camera cycle remain available. JavaScript requests the relevant REST endpoints every three seconds and updates the page without requiring a full reload.

The current implementation uses REST polling rather than Flask-SocketIO. This decision keeps the deployed interface simple and makes the dashboard compatible with the same API used by tests and external clients. If real-time push events become necessary, WebSocket support can be introduced later without changing the database or classification pipeline.

| Dashboard area | Information or control provided |
|---|---|
| Connection indicator | Displays whether the REST service responds successfully |
| Monitoring status | Shows running state, cycle counters, and the latest error |
| Latest result | Shows disease label, confidence, status, severity, and model version |
| Detection table | Shows recent timestamps, predictions, sensor values, and status |
| Environmental trends | Displays recent temperature and humidity ranges and line plots |
| Leaf inspection | Previews and classifies an uploaded JPEG, PNG, or WebP leaf image |
| Monitoring controls | Starts, stops, or manually triggers the monitoring service |

**Table 4.5: Dashboard Components and Functions.**

The interface deliberately concentrates on the information needed to operate and verify the prototype. Every displayed value comes from either the monitoring service or the database through the API. During testing, this makes it possible to compare what the user sees with the API response and the underlying stored record.

### 4.4.8 Configuration and Command-Line Operation

The YAML configuration controls model selection, model paths, confidence threshold, database location, simulation ranges, camera settings, sensor settings, API binding, and monitoring behaviour. This avoids hard-coding deployment-specific settings into individual modules. Disease metadata is stored separately in `config/diseases.yaml`, where each class has a stable index, dataset label, display label, and severity priority.

The command-line application supports database initialisation, one-cycle simulation, classification of a local image, API serving, and physical hardware diagnostics. The `--backend` option selects simulation, ONNX, or the future Hailo backend. The `--check-hardware` option captures one camera frame and reads the DHT22 before releasing both devices. This diagnostic isolates peripheral access from model deployment and dashboard behaviour.

## 4.5 Model Implementation and Evaluation

The disease classifier was implemented using MobileNetV2 transfer learning because it offers a compact architecture suitable for eventual edge deployment. The final classification layer was adapted to the five selected PlantVillage tomato disease classes. Dataset preparation, training, evaluation, and ONNX export were implemented as reproducible command-line modules under `models/training`.

### 4.5.1 Dataset Preparation

The five PlantVillage folders were discovered by their configured dataset labels and split using seed 42. The preparation process checked file readability and dimensions, calculated a SHA-256 content hash for each image, and removed eight duplicate Late Blight files before splitting. No invalid image was reported. The procedure then created stratified training, validation, and test manifests so that each disease remained represented in each subset. Images assigned to one subset were not reused in another subset.

| Disease class | Training | Validation | Test | Total |
|---|---:|---:|---:|---:|
| Bacterial Spot | 1,703 | 212 | 212 | 2,127 |
| Early Blight | 800 | 100 | 100 | 1,000 |
| Late Blight | 1,521 | 190 | 190 | 1,901 |
| Leaf Mould | 762 | 95 | 95 | 952 |
| Septoria Leaf Spot | 1,417 | 177 | 177 | 1,771 |
| **Total** | **6,203** | **774** | **774** | **7,751** |

**Table 4.6: Reproducible Five-Class Dataset Split.**

Of the 7,751 valid unique images, roughly 80 percent were used for training, with about 10 percent each reserved for validation and testing. The split preserved the class proportions even though some diseases had more examples than others. Most importantly, the 774 test images were not used to choose model parameters. Removing duplicate images before the split also reduced the chance that an identical leaf image could appear in two subsets and make performance look better than it really was.

### 4.5.2 Training and Export Implementation

Training was performed on the available CPU using Python 3.11, PyTorch, Torchvision, MobileNetV2 pretrained weights, a batch size of eight, zero worker subprocesses, and random seed 42. Validation metrics were calculated after each epoch, and the checkpoint with the strongest validation evidence was retained. The selected baseline checkpoint was produced at epoch 5 and identified as `tomato-mobilenetv2-v1`.

The checkpoint was evaluated on the reserved test manifest and then exported to ONNX using opset 17. Export produced `tomato_mobilenet_v2.onnx` and an accompanying metadata file. The exported model was subsequently executed through ONNX Runtime against a PlantVillage Bacterial Spot image, producing a Bacterial Spot prediction with confidence 0.999988 and a recorded desktop pipeline time of 17.398 milliseconds. This single-image result confirms end-to-end ONNX compatibility but is not presented as Raspberry Pi or Hailo latency evidence.

### 4.5.3 Classification Results

The final test-set results are presented in Table 4.7. Macro averaging was used so that each disease class contributed equally to the reported precision, recall, and F1-score irrespective of class size.

| Measure | Result |
|---|---:|
| Test images | 774 |
| Accuracy | 97.93% |
| Macro precision | 98.09% |
| Macro recall | 97.90% |
| Macro F1-score | 97.97% |

**Table 4.7: Overall MobileNetV2 Test Results.**

The classifier exceeded the 85 percent acceptance targets set in Chapter Three for both accuracy and macro F1-score. Macro precision, recall, and F1-score are also close to one another, suggesting that the overall result was not driven only by the larger classes. Even so, these figures come from held-out PlantVillage images. They should not be taken as evidence that the model will perform identically on leaves photographed in the field under changing light and cluttered backgrounds.

| Disease class | Precision | Recall | F1-score | Support |
|---|---:|---:|---:|---:|
| Bacterial Spot | 100.00% | 97.17% | 98.56% | 212 |
| Early Blight | 98.96% | 95.00% | 96.94% | 100 |
| Late Blight | 97.89% | 97.89% | 97.89% | 190 |
| Leaf Mould | 98.96% | 100.00% | 99.48% | 95 |
| Septoria Leaf Spot | 94.62% | 99.44% | 96.97% | 177 |

**Table 4.8: Per-Class Classification Results.**

Performance remained strong across all five diseases, with every F1-score above 96 percent. Leaf Mould achieved complete recall on its 95 test images, whereas Early Blight recorded the lowest recall at 95 percent. Septoria Leaf Spot had the lowest precision. In practical terms, this means that a small number of leaves belonging to other diseases were incorrectly labelled as Septoria Leaf Spot.

### 4.5.4 Confusion Matrix

The confusion-matrix design introduced in Chapter Three was completed using the predictions generated from the reserved test set. The editable symbolic layout remains available in draw.io, while the numerical evaluation output is presented below.

[Open the reused editable draw.io confusion-matrix layout](diagrams/CHAPTER-THREE-CONFUSION-MATRIX.drawio)

![Numerical confusion matrix for the five-class tomato model](figures/FIGURE-4.7-CONFUSION-MATRIX.png)

**Figure 4.7: Confusion Matrix for the Five-Class MobileNetV2 Test Set.**  
**Source:** Researcher's model-evaluation output generated from the 774-image held-out test set.

Most values in Figure 4.7 fall on the main diagonal, where correct predictions appear. The model correctly identified 206 Bacterial Spot, 95 Early Blight, 186 Late Blight, 95 Leaf Mould, and 176 Septoria Leaf Spot images. Misclassifications affected six Bacterial Spot images, five Early Blight images, four Late Blight images, and one Septoria Leaf Spot image. Every Leaf Mould test image was classified correctly.

| Actual class / Predicted class | Bacterial Spot | Early Blight | Late Blight | Leaf Mould | Septoria Leaf Spot |
|---|---:|---:|---:|---:|---:|
| Bacterial Spot | 206 | 1 | 1 | 0 | 4 |
| Early Blight | 0 | 95 | 2 | 0 | 3 |
| Late Blight | 0 | 0 | 186 | 1 | 3 |
| Leaf Mould | 0 | 0 | 0 | 95 | 0 |
| Septoria Leaf Spot | 0 | 0 | 1 | 0 | 176 |

**Table 4.9: Numerical Confusion Matrix.**

The numerical matrix makes the remaining error pattern easier to see. Septoria Leaf Spot attracted the highest number of false-positive assignments: four Bacterial Spot images, three Early Blight images, and three Late Blight images were assigned to that class. This pattern suggests that visual similarity with Septoria symptoms deserves particular attention when field images are collected and the model is refined.

## 4.6 System Testing

Testing was performed at unit, integration, simulation, model-evaluation, and manual API levels. Hardware adapters were tested with fake driver objects so that configuration, retry behaviour, rotation, and resource release could be verified on the development computer. These tests establish software readiness but do not replace testing with the physical Camera Module 3 and DHT22.

### 4.6.1 Automated Test Results

The recorded project test run collected 36 tests and completed with all 36 passing. The tests cover preprocessing, post-processing, camera sources, DHT22 behaviour, model metadata, ONNX inference contracts, monitoring concurrency, uploaded-image validation and classification, API responses, database persistence, dataset splitting, metrics, and integrated simulated pipeline execution.

| Test area | Evidence verified | Result |
|---|---|---|
| Dataset preparation | Stratified and reproducible train, validation, and test manifests | Passed |
| Image preprocessing | MobileNetV2 tensor shape, normalisation path, and small-image rejection | Passed |
| Classification post-processing | Confidence acceptance, uncertainty handling, and output-size validation | Passed |
| ONNX runtime | Five-logit output and invalid-input rejection | Passed |
| Model metadata | Round-trip loading, class contract, and modified-model rejection | Passed |
| Simulated camera | Generated image dimensions and local-image loading | Passed |
| Pi Camera adapter | Configuration, capture, rotation, and release using a fake camera | Passed |
| Simulated DHT22 | Repeatability and configured value ranges | Passed |
| DHT22 adapter | Retry behaviour, exhausted retries, rounding, and GPIO release using a fake device | Passed |
| Database integration | Classification and sensor reading saved together | Passed |
| Monitoring service | One-cycle status, idempotent start and stop, and overlap prevention | Passed |
| REST API and dashboard | Health, static assets, filters, pagination, export, controls, and validation | Passed |
| Pipeline integration | Simulated image classification and database storage | Passed |
| Metrics | Accuracy, precision, recall, F1-score, and confusion-matrix calculation | Passed |
| **Complete suite** | **36 collected tests** | **36 passed** |

**Table 4.10: Automated Software Test Summary.**

The 36 passing tests cover more than successful or ideal inputs. They also exercise missing records, invalid query parameters, invalid and oversized uploads, low-confidence predictions, incorrect classifier shapes, undersized images, repeated monitoring commands, overlapping cycles, and exhausted sensor retries. Passing these checks gives reasonable confidence that the components behave consistently in the development environment, including when something goes wrong.

### 4.6.2 Simulation and Manual Functional Testing

The application was exercised without hardware using generated images, simulated environmental measurements, SQLite storage, the REST API, and the web dashboard. A simulated classification produced an accepted Leaf Mould result with confidence approximately 84.96 percent and stored the accompanying temperature and humidity values. The monitoring API was then used to trigger inference and start the repeated monitoring service.

The actual ONNX model was also tested using a labelled Bacterial Spot image from the downloaded PlantVillage dataset. The complete command-line pipeline loaded the image, preprocessed it, ran the ONNX model, applied post-processing, obtained simulated sensor values, and stored the combined record. The output class matched the source folder label.

| Functional test | Input or action | Observed outcome |
|---|---|---|
| Database initialisation | `main.py --init-db` | SQLite database and missing tables created successfully |
| One-cycle simulation | Generated leaf image and simulated sensor | Classification and sensor values returned and stored |
| Manual API inference | POST to `/api/v1/inference/trigger` | New stored classification returned by the API |
| Continuous monitoring start | POST to `/api/v1/monitoring/start` | Monitoring state changed to running |
| ONNX local-image classification | PlantVillage Bacterial Spot image | Correct Bacterial Spot label with 99.9988% confidence |
| Report retrieval | CSV and JSON export requests | Stored records returned in both formats |
| Dashboard refresh | Browser REST polling | Health, status, detections, and sensor history updated |

**Table 4.11: Completed Functional and Simulation Tests.**

Taken together, the functional tests confirm that the modules can operate as one system on the development computer. Data travelled from image acquisition through inference and sensing to database storage, API retrieval, and dashboard presentation. The single-image ONNX processing time is useful as a desktop check, but it is not a substitute for the final latency measurement on the Raspberry Pi.

### 4.6.3 Physical Hardware Test Status

The physical adapters and diagnostic command are implemented, but physical acceptance testing has not yet been recorded. Table 4.12 separates completed software preparation from the evidence that must be collected after the components are connected to the Raspberry Pi.

| Hardware area | Current status | Evidence still required |
|---|---|---|
| Pi Camera Module 3 | Adapter implemented and unit-tested with a fake camera | Camera enumeration, physical capture, focus, orientation, lighting, and sustained capture results |
| DHT22 | Adapter implemented and unit-tested with a fake device | Wiring verification, success rate, retry count, and comparison with reference instruments |
| Raspberry Pi 5 | Deployment instructions and configuration prepared | Installation, service operation, CPU usage, memory usage, and temperature measurements |
| ONNX on Raspberry Pi CPU | Model and metadata available | Output agreement, inference latency, end-to-end latency, and sustained monitoring test |
| AI HAT+ | Configuration path reserved | Exact accelerator identification, ONNX-to-HEF compilation, Hailo runtime adapter, and NPU benchmark |
| Local-network dashboard | Desktop implementation tested | Access from a second device, refresh delay, stability, and trusted-LAN configuration |
| Alert delivery | Not implemented | Notification channel, cooldown rules, delivery logs, and failure recovery |

**Table 4.12: Physical Integration and Acceptance Test Status.**

The status summary makes clear where software readiness ends and physical evidence must begin. During the first hardware session, inference should remain simulated while `main.py --check-hardware` is used to check the camera and DHT22 independently. Once both peripherals behave reliably, the ONNX backend can be enabled for a complete CPU-based run on the Pi. Hailo deployment should follow only after the accelerator variant and its supporting software have been confirmed.

## 4.7 System Operating Procedure

Moving from development to hardware is intended to happen in stages. On the development computer, `uv sync --extra simulation --extra training` prepares the environment and `uv run pytest -v` checks the software. A single simulated cycle can be run with `uv run python main.py --simulate`, while a labelled local image can be passed through the ONNX backend. The REST API and dashboard are started with `uv run python main.py --serve`.

On the Raspberry Pi, Picamera2 should be installed through Raspberry Pi OS, and the `uv` environment should inherit system packages. The hardware extra provides the DHT22 library. For the first physical test, the configuration should use `monitoring.source: picamera2`, `sensor.backend: dht22`, and `inference.backend: simulation`. The command `uv run python main.py --check-hardware` then captures one image, reads one sensor measurement, prints a diagnostic result, and releases both devices.

After the diagnostic succeeds, `inference.backend` can be changed to `onnx` and the server started. Setting the API host to `0.0.0.0` allows another device on the same trusted network to open the dashboard using the Raspberry Pi's local address. Because authentication has not been implemented, this service must remain inside a trusted network during prototype testing.

## 4.8 Implementation Limitations and Outstanding Work

The model's strongest evidence still comes from controlled PlantVillage images. Its performance on the held-out test set is encouraging, but real leaves will introduce harder conditions, including uneven lighting, complex backgrounds, changing camera distances, and more than one visible symptom. Physical evaluation should deliberately vary these conditions. Incorrect and uncertain field predictions should also be kept, since they are likely to be the most useful examples for later improvement.

The current application performs whole-image classification rather than object detection. It assigns one predominant disease class to each image and does not produce bounding boxes, lesion counts, or percentage lesion coverage. The configured severity is an alert priority associated with the disease class and is not a measurement of symptom area or biological disease stage.

Hailo acceleration remains unfinished. The model has been exported to ONNX, but it has not yet been quantised, compiled into Hailo Executable Format, or executed through a Hailo runtime adapter. Until those tasks are completed, physical integration can proceed with simulated inference or ONNX Runtime on the Raspberry Pi CPU. Final edge performance results must report the actual backend and hardware used.

The dashboard uses periodic REST polling rather than WebSocket events, and automated email or SMS alert delivery has not been implemented. The database also does not yet include the proposed alert log. These items should be completed only if they remain within the approved project scope. Authentication, HTTPS, service supervision, backup, retention control, and secure remote access would also be required before deployment beyond a controlled prototype environment.

## 4.9 Chapter Summary

This chapter has shown how the proposed tomato disease detection system was turned into a working software prototype. The design work from Chapter Three was carried forward and refined into editable draw.io architecture, use case, sequence, activity, deployment, and database diagrams. The resulting application includes interchangeable camera and sensor adapters, MobileNetV2 preprocessing and ONNX inference, confidence-aware post-processing, transactional SQLite storage, continuous monitoring, a REST API, CSV and JSON reporting, and a browser dashboard.

Using reproducible PlantVillage splits, the five-class MobileNetV2 model achieved 97.93 percent accuracy and a 97.97 percent macro F1-score on 774 held-out images. The recorded automated test run passed all 36 tests, and desktop simulation confirmed the complete route from a camera capture or uploaded image to a stored result that can be viewed on the dashboard. What remains is physical evidence from the Pi Camera, DHT22, Raspberry Pi CPU, local network, and AI HAT+. The next sensible step is therefore a staged hardware integration: first check the peripherals, then run ONNX inference on the Pi, and finally introduce Hailo acceleration.
