# CHAPTER THREE

# RESEARCH METHODOLOGY

## 3.1 Introduction

This chapter presents the methodology adopted for the design, implementation, testing, and evaluation of the tomato disease detection system. The project is an applied system-development study that combines computer vision, deep learning, edge computing, environmental sensing, database management, and web-based monitoring. The system is designed to identify selected tomato diseases from leaf images, associate detection events with temperature and relative-humidity readings, preserve the records locally, and present the results through a browser-based dashboard.

The chapter explains the Agile development methodology used to organise the work, the lifecycle phases applied to the project, the system models that describe the proposed solution, and the evaluation procedure used to assess the completed prototype. The methodology is informed by research on tomato disease classification, efficient neural networks, smart farming, image preprocessing, and interpretable plant-disease detection (Brahimi et al., 2017; Howard et al., 2017; Liakos et al., 2018; Pivoto et al., 2018; Saleem et al., 2019).

## 3.2 Research Methodology

The study adopts an applied research and iterative Agile system-development methodology. Applied research is appropriate because the study is directed towards producing and evaluating a working tomato disease detection prototype rather than only describing a theoretical model. The development process combines software engineering activities with machine-learning experimentation and physical hardware integration.

### 3.2.1 Agile Software Development Methodology

Agile Software Development is adopted as the main development methodology for this project. Agile organises development into short and repeatable cycles in which requirements are reviewed, a working increment is implemented, the increment is tested, and feedback is used to guide the next cycle. This approach is appropriate because the final behaviour of an embedded artificial-intelligence system cannot be determined completely before the camera, sensor, NPU, model, database, dashboard, and alert services have been tested together.

Agile is appropriate for the tomato disease detection system for the following reasons:

- The Raspberry Pi, AI HAT+, camera, and DHT22 sensor require physical integration and testing.
- The model pipeline may require repeated changes to image preparation, class labels, confidence thresholds, and post-processing.
- Hailo compilation and NPU execution must be verified on the target hardware rather than assumed to behave like desktop inference.
- The API, database, dashboard, and alert services depend on the outputs of the inference and sensor services.
- Short development cycles make it possible to identify performance bottlenecks before the complete system is assembled.
- Agricultural machine-learning research shows that controlled-dataset performance must be interpreted together with deployment limitations and real-world variation (Brahimi et al., 2017; Raza et al., 2015; Saleem et al., 2019).

### 3.2.2 Comparison with Other Methodologies

The selected methodology was compared with Waterfall, Structured Systems Analysis and Design Methodology (SSADM), Object-Oriented Analysis and Design Methodology (OOADM), and Prototyping. The comparison considers the type of project, the need for hardware experimentation, the need for model training, and the requirement for repeated system testing.

| Methodology | Limitation for This Project | Reason Agile Is Preferred |
|---|---|---|
| Waterfall | Changes to hardware, dataset classes, or model requirements are difficult to introduce after a phase has been completed. | Agile permits requirements and implementation decisions to be refined between cycles. |
| SSADM | Provides detailed structured analysis but can introduce documentation overhead for a small embedded AI prototype. | Agile gives greater emphasis to working hardware and software increments. |
| OOADM | Supports software object modelling but does not by itself address model training, hardware calibration, or experimental evaluation. | Agile covers the interaction between software, hardware, machine learning, and testing. |
| Prototyping | Helps validate an early interface or concept but does not provide a complete lifecycle for model deployment and system validation. | Agile supports repeated prototyping, integration, testing, and review. |
| Agile | Requires disciplined sprint planning, testing, and documentation. | It is selected because it accommodates uncertainty and continuous integration across the project components. |

**Table 3.1: Comparison of Development Methodologies.**

The comparison indicates that Agile is better suited to this study because the project contains both experimental and implementation activities. Hardware behaviour, model accuracy, inference speed, and service integration cannot be confirmed through documentation alone; they must be tested and refined through successive working increments. The comparison also reflects the reviewed research. Classical image-processing methods use segmentation and engineered features, while deep-learning methods learn representations directly from images. Both approaches are useful for comparison, but a lightweight deep-learning workflow is more suitable for the planned edge deployment (Al-Hiary et al., 2011; Bhange and Hingoliwala, 2011; Brahimi et al., 2017; Howard et al., 2017).

#### Tools and Materials

The materials are divided into hardware and software components. They were selected to support tomato leaf image acquisition, environmental monitoring, local inference, data persistence, and local-network reporting.

#### Hardware Components

| Component | Specification | Role in System |
|---|---|---|
| Raspberry Pi 5 | Quad-core ARM Cortex-A76 processor, 8 GB RAM | Host computer for the system services |
| Raspberry Pi AI HAT+ | Hailo accelerator variant to be confirmed before compilation: 13-TOPS Hailo-8L or 26-TOPS Hailo-8 | Hardware-accelerated neural-network inference |
| Pi Camera Module 3 | 12 MP autofocus camera; Wide version used if the 120 degree field of view is required | Tomato leaf image capture |
| DHT22 Sensor | Temperature and relative-humidity sensor | Environmental monitoring |
| Solderless Breadboard | Half-size prototyping board | Sensor circuit assembly |
| Jumper Wires | GPIO connection wires | Electrical connections between the Raspberry Pi and DHT22 |
| MicroSD Card | Class 10 or better | Operating system and local data storage |
| USB-C Power Supply | Raspberry Pi-compatible supply | Stable power delivery |
| Monitor and Keyboard | Initial configuration equipment | System setup and troubleshooting |
| Training Workstation | CUDA-capable computer used for model training and compilation | Model preparation and deployment tooling |

**Table 3.2: Hardware Components and Their Roles.**

The hardware table identifies the physical resources required to construct and operate the prototype. The Raspberry Pi 5 provides the main computing environment, while the camera and DHT22 sensor provide the visual and environmental inputs. The AI HAT+ is included to accelerate model inference, and the remaining components support power delivery, wiring, local storage, setup, and model preparation.

#### Software Components

| Software | Role in System |
|---|---|
| Raspberry Pi OS | Operating system for the Raspberry Pi 5 |
| Python | Primary programming language |
| Picamera2 | Camera interfacing |
| Adafruit CircuitPython DHT | DHT22 sensor interfacing |
| HailoRT SDK | Runtime execution of the compiled model |
| Hailo Dataflow Compiler | Conversion of the trained model to Hailo Executable Format |
| PyTorch and Torchvision | MobileNetV2 transfer learning and classification-model development |
| Flask | REST API and server-side application framework |
| Flask-SocketIO | Real-time dashboard updates |
| SQLAlchemy and SQLite | Local data persistence |
| OpenCV and NumPy | Image processing and numerical operations |
| Pytest | Unit and integration testing |
| Git and GitHub | Version control and source management |

**Table 3.3: Software Components and Their Roles.**

The software components form the processing and service layer of the system. The camera and sensor libraries collect the input data, PyTorch and Torchvision support MobileNetV2 transfer learning, and the Hailo tools prepare and execute the compiled classification model. Flask, SocketIO, SQLAlchemy, and SQLite provide local access, persistence, and live reporting. Testing and version-control tools support verification and reproducibility throughout the development process.

## 3.3 Agile Lifecycle Applied to the Project

The Agile lifecycle used in this study is an adaptation of iterative development to a tomato disease classification prototype. Each phase produces an output that is reviewed before the next phase is expanded. The lifecycle supports the gradual integration of the hardware platform, tomato image dataset, disease classification model, environmental sensor, local storage, dashboard, and alert services.

![Agile methodology lifecycle](<diagrams/agile methodoly.jpg>)

**Figure 3.1: Agile Methodology Lifecycle Applied to the Tomato Disease Detection Project.**  
**Source:** Researcher-provided diagram. The original publication source was not supplied; it should be identified and cited before final academic submission if the diagram was obtained externally.

### 3.3.1 Planning Phase

The planning phase establishes the purpose, boundaries, resources, and expected outputs of the project. The project is limited to tomato disease detection using image data from the selected tomato disease classes. The main physical platform consists of the Raspberry Pi 5, Raspberry Pi AI HAT+, Pi Camera Module 3, and DHT22 temperature and humidity sensor. The software scope includes model training and deployment, local inference, data persistence, API access, dashboard monitoring, and alert notification.

The planning phase also establishes the main development outputs. These outputs include a configured hardware platform, a trained tomato disease model, a Hailo-deployed inference model, a persistent monitoring service, and a complete working prototype. The project requirements are reviewed at the end of each development increment so that changes can be recorded before the next increment is started.

### 3.3.2 Analysis and Requirements Phase

The analysis and requirements phase translates the project objectives into functional and non-functional requirements. Functional requirements include capturing tomato leaf images, reading environmental data, classifying each accepted image, saving labelled results, displaying current and historical predictions, exporting records, and sending high-severity alerts. Non-functional requirements include local operation, acceptable inference speed, reliable data persistence, service availability, and manageable resource utilisation on the Raspberry Pi.

The analysis also identifies the main data relationships required by the system. A classification record must be associated with its image, predicted disease label, confidence score, prediction status, severity, and timestamp. The closest available temperature and humidity readings must be correlated with the classification record. Alert events must preserve the notification type, recipient, status, and time sent. These requirements guide the system models and database design presented in Section 3.4.

### 3.3.3 Design Phase

During the design phase, the system is organised into hardware, local service, database, and client layers. The camera service receives image frames, the sensor service receives DHT22 readings, and the inference pipeline prepares images and submits them to the Hailo NPU. The resulting classifications and sensor readings are stored in SQLite, while the API, WebSocket service, dashboard, and alert service provide access to the stored information.

The design phase also defines the model input dimensions, class order, ImageNet normalisation values, confidence threshold, database entities, service boundaries, and interaction sequence. The architecture, use case, sequence, activity, and entity-relationship models are presented in Section 3.4.

### 3.3.4 Implementation Phase

Implementation proceeds through focused development increments. The sprint plan below connects the Agile lifecycle to the actual tomato disease detection project.

| Sprint | Main Activities | Expected Output |
|---|---|---|
| Sprint 1 | Raspberry Pi operating-system setup, camera installation, DHT22 wiring, and AI HAT+ configuration | Configured hardware platform |
| Sprint 2 | Tomato dataset preparation, image-label review, preprocessing, and MobileNetV2 transfer learning | Initial tomato disease classification model |
| Sprint 3 | ONNX export, Hailo Dataflow Compiler processing, HEF generation, and NPU inference testing | Hailo-deployed inference model |
| Sprint 4 | Sensor service, SQLite schema, repository layer, detection storage, and sensor correlation | Persistent monitoring service |
| Sprint 5 | Flask API, SocketIO dashboard, reporting, alert notification, and end-to-end integration | Complete working prototype |

**Table 3.4: Agile Development Increments for the Tomato Disease Detection Project.**

The sprint plan shows how the project progresses from basic hardware preparation to a complete integrated prototype. Each sprint produces a tangible output that becomes an input to the next sprint. For example, the trained tomato disease model produced during Sprint 2 is required before NPU deployment can be completed in Sprint 3, while the database and sensor services developed in Sprint 4 are required before the dashboard and alert functions can be evaluated in Sprint 5.

### 3.3.5 Testing Phase

Testing is performed continuously during implementation and is expanded after the individual services have been integrated. Unit tests examine individual functions such as image preprocessing, post-processing, sensor reading, database operations, API responses, and alert logic. Integration tests examine communication between the camera, inference pipeline, sensor service, database, API, dashboard, and alert service. System tests examine complete tomato leaf detection cycles on the Raspberry Pi 5 and AI HAT+.

The testing phase records defects, corrections, test inputs, expected outputs, actual outputs, and pass or fail decisions. Hardware-dependent functions may use controlled mocks during unit testing, but the final system test must be performed on the target hardware under the conditions specified in Section 3.5.

### 3.3.6 Deployment and Review Phase

The deployment and review phase places the working increment on the Raspberry Pi 5 target platform and evaluates it against the defined requirements. The review considers detection quality, inference latency, frames per second, sensor-read reliability, CPU and memory usage, database persistence, API response time, dashboard update delay, and alert delivery.

The result of each review is used to decide whether the project should proceed, repeat a development activity, or correct a defect. The project is considered ready for final evaluation when the hardware, model, sensor, database, API, dashboard, and alert services operate together and the acceptance criteria in Section 3.5 are measurable. The final results are reported separately from the methodology so that measured outcomes are not confused with planned targets.

## 3.4 System Models

The system models describe the structure, interactions, processing activities, and data relationships of the tomato disease detection system. The models are based on the project requirements and are informed by smart-farming and agricultural machine-learning research (Liakos et al., 2018; Pivoto et al., 2018; Saleem et al., 2019).

### 3.4.1 Architectural Model

The system follows an edge-first architecture. The camera and DHT22 sensor collect data, the Raspberry Pi coordinates the services, the Hailo NPU accelerates model inference, and the database, API, dashboard, and alert services operate locally. Internet access is required only for optional external alert delivery.

```mermaid
flowchart TB
    subgraph Hardware[Hardware Layer]
        CAM[Pi Camera Module 3]
        DHT[DHT22 Sensor]
        RPI[Raspberry Pi 5]
        HAI[Hailo NPU on AI HAT+]
    end

    subgraph Services[Local Software Services]
        CS[Camera Service]
        SS[Sensor Service]
        INF[Inference Pipeline]
        DB[(SQLite Database)]
        API[Flask REST API]
        WS[SocketIO WebSocket]
        ALERT[Alert Service]
    end

    subgraph Clients[Local Network Clients]
        DASH[Web Dashboard]
        FARMER[Farmer or Operator]
        NOTIFY[Email or SMS Provider]
    end

    CAM --> CS
    DHT --> SS
    RPI --> CS
    RPI --> SS
    CS --> INF
    INF --> HAI
    HAI --> INF
    INF --> DB
    SS --> DB
    DB --> API
    API --> WS
    WS --> DASH
    FARMER --> DASH
    DB --> ALERT
    ALERT --> NOTIFY
```

**Figure 3.2: Architectural Model of the Tomato Disease Detection System.**  
**Source:** Researcher’s design, informed by smart-farming system architecture research (Liakos et al., 2018; Pivoto et al., 2018). Rendered using Mermaid.

The architectural model separates the system into hardware, local services, and client layers. Data enters through the camera and DHT22 sensor, is processed by the Raspberry Pi and Hailo NPU, and is then persisted in the SQLite database. The API and WebSocket service make the stored and live results available to the dashboard, while the alert service handles optional external notifications. This arrangement keeps the core tomato disease detection workflow operational on the local device even when external connectivity is unavailable.

### 3.4.2 Use Case Diagram

The use case diagram presents the functional relationship between the Farmer/Operator, the System Administrator, and the tomato disease detection system. The editable diagram has been created using draw.io.

[Open the editable draw.io use case diagram](diagrams/CHAPTER-THREE-USE-CASE-DIAGRAM.drawio)

**Figure 3.3: Use Case Diagram of the Tomato Disease Detection System.**  
**Source:** Researcher’s design, informed by the system requirements and agricultural monitoring literature. Created using draw.io.

The use case model demonstrates that the Farmer/Operator primarily interacts with the system to monitor tomato disease detections, review historical evidence, inspect environmental readings, export reports, and receive alerts. The System Administrator performs configuration and maintenance activities, including setting alert thresholds, managing data retention, and monitoring system services. The distinction between these actors clarifies the access responsibilities that must be supported by the implemented dashboard and service interfaces.

The principal use cases are:

- View live tomato disease detections.
- View detection history and annotated images.
- View temperature and humidity readings.
- Export detection records as CSV or JSON.
- Receive high-severity disease alerts.
- Configure alert thresholds and data retention.
- Monitor and restart system services.

### 3.4.3 Sequence Diagram

The sequence diagram shows the interaction between the principal components during a tomato detection cycle.

```mermaid
sequenceDiagram
    actor Farmer as Farmer/Operator
    participant CAM as Pi Camera
    participant INF as Inference Pipeline
    participant NPU as Hailo NPU
    participant DHT as DHT22 Sensor
    participant DB as SQLite Database
    participant API as REST API
    participant DASH as Dashboard
    participant ALERT as Alert Service

    loop Detection Cycle
        CAM->>INF: Capture tomato leaf frame
        INF->>INF: Resize and normalize image
        INF->>NPU: Submit input tensor
        NPU-->>INF: Return class scores
        INF->>INF: Calculate probabilities and apply confidence threshold
        DHT->>DB: Store temperature and humidity reading
        INF->>DB: Store disease classification record
    end

    Farmer->>DASH: Open local dashboard
    DASH->>API: Request recent detections
    API->>DB: Query stored records
    DB-->>API: Return detection and sensor data
    API-->>DASH: Return JSON response
    DASH-->>Farmer: Display result and environmental readings
    DB->>ALERT: Send high-severity event
    ALERT-->>Farmer: Deliver optional notification
```

**Figure 3.4: Sequence Diagram for Tomato Disease Detection and Reporting.**  
**Source:** Researcher’s design, informed by the data-flow requirements of smart-farming monitoring systems (Liakos et al., 2018; Pivoto et al., 2018). Rendered using Mermaid.

The sequence model shows that image acquisition and sensor measurement occur during the detection cycle, while dashboard access may occur at any time through the local API. The inference pipeline sends the captured image to the NPU, receives the disease prediction, and stores the result together with the nearest environmental reading. A high-severity detection is subsequently passed to the alert service, while the dashboard receives the stored or live result for monitoring.

### 3.4.4 Activity Diagram

The activity model represents the processing sequence from image capture to persistence and notification.

```mermaid
flowchart TD
    A([Start Detection Cycle]) --> B[Capture Tomato Leaf Frame]
    B --> C{Frame Quality Acceptable?}
    C -- No --> B
    C -- Yes --> D[Resize and Normalize Image]
    D --> E[Submit Tensor to Hailo NPU]
    E --> F[Execute MobileNetV2 Classification]
    F --> G[Calculate Class Probabilities]
    G --> H{Top Confidence Above Threshold?}
    H -- No --> I[Record Uncertain Classification]
    H -- Yes --> J[Assign Predicted Tomato Disease Label]
    J --> K[Correlate with DHT22 Reading]
    I --> L[Write Record to SQLite]
    K --> L
    L --> M{High Severity?}
    M -- Yes --> N[Dispatch Alert]
    M -- No --> O[Push Dashboard Update]
    N --> O
    O --> P([Next Detection Cycle])
```

**Figure 3.5: Activity Diagram for the Tomato Disease Inference Pipeline.**  
**Source:** Researcher’s design, informed by image-processing and deep-learning detection workflows (Al-Hiary et al., 2011; Brahimi et al., 2017; Saleem et al., 2019). Rendered using Mermaid.

The activity model explains the control flow used for each tomato leaf frame. It includes a quality decision before inference, image preparation, NPU execution, class-probability calculation, confidence filtering, disease-label assignment, environmental correlation, database persistence, and severity-based alerting. A low-confidence result is stored as uncertain rather than being interpreted as a healthy leaf. The loop back to the next cycle represents continuous monitoring rather than a single manual diagnosis.

### 3.4.5 Entity-Relationship Diagram

The database model stores tomato disease classifications, environmental readings, and alert events. A classification record is linked to the closest available sensor reading, while an alert log records notifications generated from high-severity classifications.

```mermaid
erDiagram
    CLASSIFICATION_RECORD {
        int id PK
        string image_path
        string disease_label
        float confidence_score
        string prediction_status
        string severity_class
        datetime timestamp
        int sensor_reading_id FK
    }

    SENSOR_READING {
        int id PK
        float temperature_celsius
        float humidity_percent
        datetime timestamp
    }

    ALERT_LOG {
        int id PK
        int classification_record_id FK
        string alert_type
        string recipient
        string status
        datetime sent_at
    }

    SENSOR_READING ||--o{ CLASSIFICATION_RECORD : correlates
    CLASSIFICATION_RECORD ||--o{ ALERT_LOG : triggers
```

**Figure 3.6: Entity-Relationship Diagram for Local Tomato Disease Records.**  
**Source:** Researcher’s database design, informed by the need for persistent and traceable agricultural monitoring data (Liakos et al., 2018; Pivoto et al., 2018). Rendered using Mermaid.

The entity-relationship model provides traceability between a tomato disease classification and the environmental conditions recorded at approximately the same time. The alert log preserves evidence of notification events, including the recipient, delivery status, and time sent. These relationships allow the system to support historical analysis, reporting, and later review of incorrect or uncertain classifications.

## 3.5 System Evaluation Procedure

The system will be evaluated as an integrated tomato disease detection prototype using a controlled engineering evaluation. The evaluation will examine the quality and preparation of the tomato image dataset, the accuracy of the trained model, the effect of model conversion for edge inference, the reliability of the DHT22 sensor, the operation of the local database and API, the dashboard response, and the delivery of alerts.

The evaluation is designed to answer four practical questions. First, can the model distinguish the selected tomato disease classes? Second, can the compiled model operate with acceptable speed on the Raspberry Pi AI HAT+? Third, can the camera, sensor, database, API, dashboard, and alert services operate together without losing or corrupting records? Finally, can the resulting system provide useful evidence for reviewing tomato disease events? This multi-dimensional approach is consistent with research showing that agricultural machine-learning systems must be assessed using accuracy, computational efficiency, interpretability, and deployment conditions rather than accuracy alone (Liakos et al., 2018; Saleem et al., 2019; Toda and Okura, 2019).

### Dataset and Data Preparation

The dataset will contain tomato leaf images belonging to the five disease classes defined for the project: Bacterial Spot, Early Blight, Late Blight, Leaf Mould, and Septoria Leaf Spot. These five classes are available in the PlantVillage tomato subset and can therefore be used to train a model that matches the project scope. When the highest predicted probability is below the selected confidence threshold, the system will record an uncertain classification rather than claiming that the leaf is healthy. Healthy tomato leaves are outside the five-class model unless a separately labelled healthy class is deliberately added and documented before training.

The original PlantVillage class identifiers will be mapped consistently to the project display labels. `Tomato___Bacterial_spot` will map to Bacterial Spot, `Tomato___Early_blight` to Early Blight, `Tomato___Late_blight` to Late Blight, `Tomato___Leaf_Mold` to Leaf Mould, and `Tomato___Septoria_leaf_spot` to Septoria Leaf Spot. This mapping will be saved with the trained model so that desktop, ONNX, and Hailo inference use the same class order.

The repository identifies the PlantVillage tomato subset as the primary image source. The preparation process will use an 80/10/10 split for training, validation, and testing. The final number of images retained in each class and each split will be recorded from the dataset-preparation output and reported with the experimental results. No image from the held-out test set will be used for training, augmentation fitting, threshold selection, or model checkpoint selection.

The preparation procedure will include:

1. Collecting and verifying the tomato images and disease labels.
2. Removing corrupt, duplicated, or incorrectly labelled images.
3. Recording the number of images available in each disease class before and after cleaning.
4. Reviewing class balance and identifying classes that may require controlled augmentation.
5. Organising the verified images into class-labelled directories or an equivalent classification manifest.
6. Dividing images into training, validation, and test subsets using a fixed random seed.
7. Ensuring that related images from the same plant or capture sequence do not appear in more than one subset where such grouping information is available.
8. Resizing input images to 224 x 224 pixels for MobileNetV2 processing.
9. Applying training-only augmentation involving suitable changes in scale, position, orientation, and illumination.
10. Reserving the test subset for the final evaluation only.

| Configuration Item | Project Setting or Required Record |
|---|---|
| Crop scope | Tomato only |
| Target disease classes | Bacterial Spot, Early Blight, Late Blight, Leaf Mould, and Septoria Leaf Spot |
| Primary dataset source | PlantVillage tomato subset |
| Dataset split | 80% training, 10% validation, 10% testing |
| Input size | 224 x 224 pixels |
| Preprocessing | Resize, RGB conversion, normalization, and model-compatible tensor conversion |
| Augmentation | Training-only geometric and illumination variation |
| Class record | Number of images per class before cleaning and after splitting |
| Reproducibility record | Random seed, class order, label-set version, and preparation date |

**Table 3.5: Tomato Dataset and Input Configuration.**

The table defines the information required to reproduce the dataset preparation stage. The class list fixes the scope of the experiment to tomato disease detection, while the split and test-set restrictions protect the evaluation from data leakage. Recording the class counts and preparation settings is particularly important because tomato disease studies have shown that dataset size, class separation, image variation, and symptom visualisation influence reported performance (Brahimi et al., 2017; Saleem et al., 2019; Toda and Okura, 2019). Research using thermal, stereo, and hyperspectral imagery further shows that ordinary visible images may be affected by lighting, canopy structure, and symptom similarity (Raza et al., 2015; Xie et al., 2015).

### Model Training and Validation

The project uses MobileNetV2 as a five-class image classifier because it provides a practical balance between computational efficiency and classification performance for edge deployment. The model will be initialised with ImageNet-pretrained weights and adapted through transfer learning for the selected tomato disease classes. MobileNetV2 is preferred over the reference project’s final 22-class weights because the reference labels do not match this study. Only the reusable architecture, preprocessing pattern, and ONNX deployment approach will be adapted. The training workflow will use the best validation checkpoint rather than the final epoch automatically, thereby reducing the risk of selecting an overfitted model.

The initial training configuration is a maximum of 30 epochs with a batch size of 32 and early stopping based on validation performance. The model will use a 224 x 224 RGB input and ImageNet normalisation. The inference pipeline will accept the highest-probability class when its confidence score is at least 0.70; otherwise, it will store the result as uncertain. Any change to these values during experimentation will be recorded in the experiment log and reported with the results.

| Training or Deployment Item | Configuration or Evidence Required |
|---|---|
| Model architecture | MobileNetV2 image-classification model with transfer learning |
| Training epochs | Maximum of 30 epochs with documented early stopping |
| Batch size | 32, subject to available training memory |
| Input resolution | 224 x 224 pixels |
| Input normalisation | ImageNet channel mean and standard deviation |
| Model-selection rule | Best validation macro F1-score, with validation loss used as supporting evidence |
| Confidence threshold | 0.70 for accepting the predicted class; lower values are marked uncertain |
| Desktop evaluation | Test the selected model on the held-out test subset |
| Export path | PyTorch model to ONNX, then to Hailo Executable Format |
| Edge validation | Compare desktop and Raspberry Pi AI HAT+ outputs on the same test inputs |
| Deployment record | Model version, class order, weights, compiler settings, and calibration information |

**Table 3.6: Model Training and Deployment Configuration.**

The training table distinguishes fixed project settings from evidence that must be recorded during implementation. The desktop evaluation establishes the baseline model behaviour, while the edge validation determines whether export, quantisation, compilation, and NPU execution have changed the model output. The use of a compact architecture for a constrained device is supported by research on efficient convolutional neural networks (Howard et al., 2017), while tomato disease studies support automatic feature learning and visual examination of disease-relevant model responses (Brahimi et al., 2017; Toda and Okura, 2019).

The model-development procedure will be implemented as follows:

1. Prepare the tomato dataset according to the data-preparation procedure.
2. Initialise MobileNetV2 using ImageNet-pretrained weights and replace the final classification layer with a five-class output layer.
3. Train the model for the documented training schedule.
4. Monitor training loss, validation loss, classification accuracy, macro precision, macro recall, and macro F1-score during training.
5. Select and preserve the best validation checkpoint.
6. Evaluate the selected checkpoint on the held-out test subset.
7. Export the selected model to ONNX format.
8. Compile the ONNX model into Hailo Executable Format using the Hailo Dataflow Compiler.
9. Load the HEF model through HailoRT on the Raspberry Pi AI HAT+.
10. Run the same test inputs through the desktop and edge versions of the model.
11. Record any class-label, confidence-score, probability-ranking, or quantisation differences.

### Hardware and Software Testing

Testing will be performed at five levels. Hardware-dependent functions will be tested on the target Raspberry Pi where possible, while unit tests for camera, GPIO, and NPU-dependent code may use controlled mocks so that software logic can be checked independently of physical hardware. The repository defines Pytest as the testing framework and separates unit tests from integration tests.

| Test Level | Main Test Activities | Evidence to Record |
|---|---|---|
| Unit testing | Test camera capture, preprocessing, post-processing, DHT22 reading, database operations, API functions, and alert logic independently. | Test-case result, failure message, and corrected implementation where required |
| Integration testing | Verify that camera frames, inference results, sensor readings, database records, API responses, and dashboard updates are connected correctly. | Input record, output record, timestamp relationship, and pass or fail result |
| System testing | Run complete tomato leaf classification cycles on the Raspberry Pi 5 and AI HAT+. | Test image, predicted label, confidence, prediction status, labelled output, database record, and dashboard result |
| Performance testing | Measure inference latency, end-to-end latency, throughput, resource usage, and service response time. | Mean, median, maximum, and percentile measurements where available |
| Reliability testing | Run the sensor and core services continuously and record read failures, service interruptions, database errors, and recovery behaviour. | Duration, number of cycles, failures, recoveries, and final system state |

**Table 3.7: Hardware and Software Testing Matrix.**

The testing matrix establishes a progression from isolated component verification to complete prototype evaluation. Unit testing identifies defects within individual services, integration testing verifies communication between services, and system testing confirms that the complete tomato classification workflow operates on the target hardware. Performance and reliability testing then determine whether the system can continue operating under sustained use and whether failures are detected and recorded rather than silently lost.

The physical evaluation will use available tomato leaf specimens and printed tomato leaf images under controlled indoor conditions. Because the selected model performs whole-image classification, each accepted frame will be arranged so that one predominant tomato leaf or one prepared test image occupies the classification view. Each test record will include the input image or image identifier, expected label, predicted label, confidence score, prediction status, timestamp, sensor values, processing time, database status, dashboard status, and alert status. For repeatability, the camera position, approximate lighting condition, test-image distance, model version, confidence threshold, and software version will be recorded for each test session.

The sensor reliability run will cover a continuous controlled monitoring period, with the start time, end time, number of scheduled readings, successful readings, failed readings, and reference-instrument readings recorded. The inference benchmark will include a warm-up period before measurements are collected so that startup effects do not distort the reported latency. At least 30 measured inference cycles will be recorded for each benchmark configuration, together with the mean, median, maximum, and 95th-percentile latency where the measurement tooling supports it.

The evaluation will also record limitations caused by controlled datasets, lighting variation, leaf position, background complexity, symptom overlap, and the difference between RGB imaging and more expensive thermal or hyperspectral approaches (Raza et al., 2015; Xie et al., 2015). These conditions will be discussed as limitations of generalisation rather than treated as evidence that the model performs equally well in every agricultural environment.

### Performance Metrics

The following measures will be used to evaluate both the model and the complete system:

| Evaluation Area | Metrics or Evidence | Measurement Approach |
|---|---|---|
| Classification performance | Accuracy, macro and per-class precision, recall, F1-score, and per-class support | Calculate from predictions on the held-out test subset |
| Error analysis | Confusion matrix and examples of false positives and false negatives | Compare predicted labels with the verified test labels |
| Inference performance | Inference latency, end-to-end latency, and frames per second | Measure model execution and the complete capture-to-storage cycle separately |
| Resource usage | CPU utilisation, RAM usage, device temperature, and NPU execution behaviour | Record during inference and sustained-operation tests |
| Sensor reliability | Successful-read rate, temperature error, humidity error, and missing readings | Compare DHT22 readings with the scheduled sample count and reference instruments |
| Persistence | Database-write success rate, timestamp correctness, and sensor-classification correlation | Compare generated events with stored records and linked sensor readings |
| API and dashboard | Endpoint response time, dashboard update delay, and service availability | Repeat local requests and compare returned values with database records |
| Alerting | Alert-trigger correctness and notification delivery time | Compare high-severity records with generated notification logs |
| Reporting | Accuracy and completeness of CSV and JSON exports | Compare exported records with the database query used to generate them |

**Table 3.8: Evaluation Metrics and Evidence.**

The metrics table combines model-quality measures with operational system measures. Classification accuracy measures the proportion of test images assigned to the correct disease class. Precision measures the proportion of predictions for a class that are correct, recall measures the proportion of images belonging to a class that are correctly identified, and the F1-score combines precision and recall. Macro averages give equal importance to each of the five disease classes and reduce the possibility that a large class will dominate the reported result. Latency, resource, sensor, persistence, API, dashboard, alert, and reporting measures determine whether the classifier is useful as part of a complete edge system rather than only as a standalone experiment.

For operational measurements, inference latency will be calculated from the point at which an input tensor is submitted until the model output is available. End-to-end latency will include image capture, preprocessing, NPU inference, post-processing, sensor correlation, and database writing. Throughput will be reported as processed frames divided by the measurement duration. Sensor success rate will be calculated as successful readings divided by scheduled readings, multiplied by 100. Temperature and humidity errors will be reported against the selected reference instruments.

### Confusion Matrix Diagram

A confusion matrix will be used to examine how the model distinguishes between the selected tomato disease classes. Each row represents the actual disease class in the test set, while each column represents the class predicted by the model. Values along the main diagonal represent correct predictions, whereas values outside the diagonal represent confusion between disease classes. The editable draw.io version of the matrix is provided below.

[Open the editable draw.io confusion matrix](diagrams/CHAPTER-THREE-CONFUSION-MATRIX.drawio)

**Figure 3.7: Confusion Matrix Layout for the Tomato Disease Classification Model.**  
**Source:** Researcher’s evaluation design. Created using draw.io.

The diagonal positions in the completed matrix will be used to identify correctly classified tomato disease images. Off-diagonal positions will show the disease pairs that the model confuses most often, such as visually similar leaf symptoms. These counts will be used together with classification accuracy, precision, recall, and F1-score to explain not only how accurate the model is, but also the types of errors it produces. The final matrix will be reported with numerical values in the experimental findings chapter rather than being presented as a completed result in this methodology chapter.

The following table provides a text preview of the same matrix structure for readers viewing the Markdown document. The editable and presentation-ready version remains the draw.io diagram linked above.

| Actual \\ Predicted | Bacterial Spot | Early Blight | Late Blight | Leaf Mould | Septoria Leaf Spot |
|---|---:|---:|---:|---:|---:|
| Bacterial Spot | n11 | n12 | n13 | n14 | n15 |
| Early Blight | n21 | n22 | n23 | n24 | n25 |
| Late Blight | n31 | n32 | n33 | n34 | n35 |
| Leaf Mould | n41 | n42 | n43 | n44 | n45 |
| Septoria Leaf Spot | n51 | n52 | n53 | n54 | n55 |

**Table 3.9: Text Preview of the Tomato Disease Confusion Matrix.**

Each value n_ij represents the number of test images whose actual class is i and whose predicted class is j. The diagonal values n11, n22, n33, n44, and n55 represent correct predictions, while the remaining values represent classification errors. These symbolic values will be replaced with measured counts after the final test-set evaluation.

### Engineering Acceptance Thresholds

The study will use the following acceptance thresholds as engineering targets. These are evaluation criteria, not claims of achieved performance; the measured results will be reported separately after testing.

| Acceptance Area | Target |
|---|---|
| Tomato disease classification | Classification accuracy and macro F1-score of at least 85% on the held-out test subset |
| Edge inference throughput | At least 10 processed frames per second under the defined benchmark conditions |
| End-to-end classification cycle | No more than 500 milliseconds from capture to database write under the defined benchmark conditions |
| Sensor reliability | At least 95% successful DHT22 readings during the controlled monitoring run |
| System resource usage | Peak CPU utilisation below 70% and peak RAM usage below 4 GB during sustained operation |
| API response time | Standard local queries completed within 200 milliseconds under the defined request test |
| Alert delivery | High-severity notification delivered within 60 seconds when network access is available |
| Data export | CSV and JSON exports contain the complete records returned by the corresponding database query |

**Table 3.10: Engineering Acceptance Thresholds.**

The acceptance-threshold table provides a transparent basis for deciding whether the prototype meets its stated engineering objectives. The thresholds cover accuracy, speed, resource consumption, sensor operation, service responsiveness, notification behaviour, and data integrity. If a target is not achieved, the result will be reported with the measured value, test conditions, likely cause, and proposed improvement rather than being omitted.

## 3.6 Benefits and Limitations of the Methodology

The Agile methodology provides benefits for this project because the system contains uncertain and interdependent components. It allows the hardware and software to be integrated gradually, supports repeated testing of the model and sensor services, and makes it possible to improve the system after each review. It also encourages the project team to preserve working increments and evidence of defects rather than waiting until the end of development to discover integration problems.

| Area | Benefits | Limitations |
|---|---|---|
| Development control | Short increments make progress visible and allow defects to be addressed early. | Poorly documented sprint decisions can make the development history difficult to reproduce. |
| Hardware integration | Camera, DHT22, Raspberry Pi, and AI HAT+ components can be tested progressively. | Hardware availability, wiring faults, and device-specific errors can delay a sprint. |
| Machine-learning development | Dataset preparation, training, validation, and deployment can be repeated as evidence is collected. | Model performance may change when the dataset, class balance, or test conditions change. |
| System integration | The API, database, dashboard, and alert services can be connected one service at a time. | Changes in one service may require changes in dependent services. |
| Evaluation | Continuous testing produces evidence about accuracy, latency, resource usage, and reliability. | Repeated testing requires time, consistent test conditions, and careful record keeping. |
| Agricultural deployment | Local edge processing reduces dependence on continuous connectivity for core detection. | Controlled images and indoor tests may not represent all outdoor tomato-growing conditions. |

**Table 3.11: Benefits and Limitations of the Adopted Agile Methodology.**

The table shows that Agile is beneficial because it matches the iterative and experimental nature of the project, but it does not remove the technical limitations of the system. In particular, Agile cannot by itself solve dataset bias, domain shift, sensor accuracy problems, hardware constraints, or network dependency for optional notifications. Research on tomato disease detection and smart farming similarly indicates that model performance must be interpreted in relation to data quality, environmental variation, computational resources, and practical deployment conditions (Brahimi et al., 2017; Liakos et al., 2018; Raza et al., 2015; Saleem et al., 2019; Xie et al., 2015).

## 3.7 Chapter Summary

This chapter presented the methodology for designing and evaluating the tomato disease detection system. Agile was selected to support incremental integration of the hardware, model, sensor, database, API, dashboard, and alert services. The lifecycle was divided into planning, analysis and requirements, design, implementation, testing, and deployment and review phases. The system models described the architecture, use cases, processing sequence, activity flow, and database relationships. The evaluation procedure defined how tomato images will be prepared, how the model will be trained and deployed, how the integrated prototype will be tested, and how detection, performance, sensor, and service metrics will be measured. The benefits and limitations of the methodology were also discussed.

## References

Al-Hiary, H., Bani-Ahmad, S., Reyalat, M., Braik, M., and ALRahamneh, Z. (2011). “Fast and Accurate Detection and Classification of Plant Diseases.” *International Journal of Computer Applications*, 17(1), 31-38.

Bhange, M. and Hingoliwala, H. A. (2011). “Detection and Classification of Leaf Diseases Using K-means Based Segmentation and Neural Networks Based Classification.” *International Journal of Computer Applications*, 17(1), 31-38.

Brahimi, M., Boukhalfa, K., and Moussaoui, A. (2017). “Deep Learning for Tomato Diseases: Classification and Symptoms Visualization.” *Applied Artificial Intelligence*, 31(4), 299-315.

Howard, A. G., Zhu, M., Chen, B., Kalenichenko, D., Wang, W., Weyand, T., Andreetto, M., and Adam, H. (2017). “MobileNets: Efficient Convolutional Neural Networks for Mobile Vision Applications.” *arXiv preprint arXiv:1704.04861*.

Liakos, K. G., Busato, P., Moshou, D., Pearson, S., and Bochtis, D. (2018). “Machine Learning in Agriculture: A Review.” *Sensors*, 18(8), 2674.

Pivoto, D., Waquil, P. D., Talamini, E., Finocchio, C. P. S., Dalla Corte, V. F., and Mores, G. V. (2018). “Scientific Development of Smart Farming Technologies and Their Application in Brazil.” *Information Processing in Agriculture*, 5(1), 21-32.

Raza, S. A., Prince, G., Clarkson, J. P., and Meier, U. (2015). “Automatic Detection of Diseased Tomato Plants Using Thermal and Stereo Visible Light Images.” *PLOS ONE*, 10(4), e0123262.

Saleem, M. H., Potgieter, J., and Arif, K. M. (2019). “Plant Disease Detection and Classification by Deep Learning.” *Plants*, 8(11), 468.

Toda, Y. and Okura, F. (2019). “How Convolutional Neural Networks Diagnose Plant Disease.” *Plant Phenomics*, 2019, Article 9237136.

Xie, C., Shao, Y., Li, X., and He, Y. (2015). “Detection of Early Blight and Late Blight Diseases on Tomato Leaves Using Hyperspectral Imaging.” *Scientific Reports*, 5, Article 16564.
