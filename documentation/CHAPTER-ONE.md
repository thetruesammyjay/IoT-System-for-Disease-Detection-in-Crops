# CHAPTER ONE

# INTRODUCTION

## 1.1 Background to the Study

Agriculture remains one of the most fundamental pillars of human civilisation, serving as the primary source of food, raw materials, and economic livelihood for billions of people worldwide. In Nigeria and across sub-Saharan Africa, agriculture accounts for a substantial proportion of gross domestic product (GDP) and provides the main source of income for the majority of the rural population. According to the Food and Agriculture Organisation of the United Nations (FAO, 2022), approximately 600 million smallholder farming households worldwide depend on agriculture for their survival, and this sector feeds over 70% of the global population. Despite its central importance, agricultural productivity continues to be severely threatened by a wide range of biotic stressors, chief among them being plant diseases caused by fungal, bacterial, viral, and oomycete pathogens.

Crop diseases are responsible for pre-harvest losses estimated to affect between 20% and 40% of global agricultural production annually, translating to economic losses in excess of $220 billion per year (Savary et al., 2019). In developing nations, where smallholder farmers lack access to diagnostic laboratories, agricultural extension officers, or reliable internet connectivity, these losses are disproportionately severe. By the time a disease is visually identified by a farmer, it has often already progressed beyond the point where treatment is economically viable, leading to partial or total crop loss. Diseases such as Late Blight in tomatoes and potatoes, caused by the pathogen *Phytophthora infestans*, famously triggered the Irish Famine of the 1840s and continue to cause billion-dollar losses worldwide each year (Fry, 2008). In Nigeria, diseases affecting maize, tomatoes, cassava, and peppers are persistently ranked among the top causes of yield reduction by the National Agricultural Extension and Research Liaison Service (NAERLS, 2021).

Traditional methods of crop disease diagnosis rely heavily on human expert observation — agronomists or experienced farmers visually inspecting plants and making judgements based on symptom patterns. This approach suffers from several fundamental limitations. It is inherently subjective, dependent on the knowledge and experience of the individual. It is not scalable across large farm areas. It is slow, as symptoms must reach a visible threshold before detection is possible. And it is unavailable to the majority of smallholder farmers who lack proximity to agricultural specialists. Laboratory-based diagnostic methods such as polymerase chain reaction (PCR) and ELISA testing provide greater accuracy but require expensive equipment, trained laboratory personnel, and days or weeks of turnaround time — entirely incompatible with the time-sensitive nature of farm management decisions.

The convergence of the Internet of Things (IoT), computer vision, and artificial intelligence (AI) over the past decade has opened a new paradigm for precision agriculture. IoT systems integrate physical sensing hardware with software services to collect, transmit, and analyse real-world data in near real time. In the agricultural domain, IoT applications have been explored for soil moisture monitoring, irrigation automation, pest detection, weather station networks, and livestock health monitoring (Elijah et al., 2018). The integration of camera-based computer vision into these systems creates the possibility of automated, continuous, and non-destructive monitoring of crop health from the leaf level.

Deep learning, a subfield of machine learning characterised by the use of multi-layered artificial neural networks, has demonstrated remarkable success in image classification and object detection tasks. Convolutional Neural Networks (CNNs) in particular have been shown to achieve accuracy levels comparable to or exceeding that of human experts in plant disease identification tasks. The landmark work of Mohanty, Hughes, and Salathé (2016), using the PlantVillage dataset of over 54,000 labelled leaf images, demonstrated that a deep learning model could classify 26 diseases across 14 crop species with accuracy approaching 99.35% under controlled conditions. Subsequent research has continuously improved upon these results, with architectures such as ResNet, DenseNet, Inception, EfficientNet, and more recently the YOLO (You Only Look Once) family achieving strong performance even on constrained, edge-deployed hardware.

However, a major barrier to the practical deployment of these systems in real agricultural settings has been the computational cost of running deep neural network inference. Until recently, models capable of high accuracy required either powerful cloud servers with GPU acceleration — introducing latency, cost, and internet-dependency — or were so heavily compressed that their accuracy in real-world conditions was unacceptably low. The emergence of dedicated Neural Processing Units (NPUs) designed for edge inference has fundamentally changed this calculus. The Raspberry Pi AI HAT+, released in 2024, integrates the Hailo-8L NPU capable of 26 Tera Operations Per Second (TOPS) of neural network inference directly into the Raspberry Pi ecosystem via a PCIe Gen 3 interface. This development makes it possible, for the first time at low cost, to run state-of-the-art object detection models at video frame rates entirely on-device, without any cloud dependency.

This project, therefore, seeks to design and implement a fully integrated IoT system for the automated real-time detection of diseases in crops. The system combines the Raspberry Pi 5 single-board computer as its central processing unit with the Raspberry Pi AI HAT+ for hardware-accelerated inference, the Pi Camera Module 3 for high-quality leaf image capture, and a DHT22 environmental sensor for the concurrent collection of temperature and relative humidity data. These two data streams — visual and environmental — are correlated and persisted in a local database, made accessible through a REST API, and presented to users through a browser-based monitoring dashboard. Automated alerts are dispatched when high-severity disease events are detected. The entire system is designed to operate independently of internet connectivity, making it suitable for deployment in rural and off-grid agricultural environments.

---

## 1.2 Statement of Problem

Despite the well-documented economic and humanitarian cost of crop diseases, the vast majority of smallholder farmers — particularly in sub-Saharan Africa and other developing regions — continue to rely on manual, unaided visual inspection as their primary means of plant health monitoring. This practice is not only inadequate but creates a cascade of problems that collectively undermine agricultural productivity and food security.

The specific problems motivating this research are identified as follows:

i. **Late and inaccurate disease diagnosis:** Manual visual inspection of crops requires diseases to reach an advanced, visually obvious stage before a farmer or agronomist can identify them. By this point, the pathogen population within the plant has often already proliferated to a level that makes treatment ineffective and cross-contamination of neighbouring plants probable. Studies have shown that detection delays of as few as five to seven days in diseases like tomato Late Blight can result in the loss of an entire growing season (Fry, 2008).

ii. **Absence of objective and consistent diagnosis:** Human diagnosis of plant disease symptoms is inherently subjective and varies significantly based on the expertise, experience, and even fatigue of the observer. Symptoms of different diseases can share visual similarities — for example, Early Blight and Septoria Leaf Spot on tomato both present as dark lesions on leaves — leading to misdiagnosis and inappropriate treatment with incorrect pesticides, which wastes resources and may accelerate the development of pathogen resistance.

iii. **Inaccessibility of expert knowledge at point of need:** Qualified plant pathologists, agricultural extension officers, and diagnostic laboratory services are concentrated in urban centres and are largely inaccessible to smallholder farmers at the farm level, particularly in rural areas of Nigeria and across Africa. This geographic and economic barrier means that most farmers are forced to make pest management decisions without adequate information.

iv. **Lack of integration with environmental context:** Crop diseases do not develop in isolation from their environment. The spread and severity of many diseases are strongly influenced by environmental conditions, particularly temperature and relative humidity. For instance, Late Blight in tomatoes proliferates most rapidly when relative humidity exceeds 90% and temperatures are between 10°C and 20°C (Fry, 2008). Existing manual inspection approaches do not correlate disease observations with environmental readings, eliminating a critical dimension of diagnostic and predictive information.

v. **Absence of historical disease data:** Without an automated logging and data persistence system, farmers have no mechanism to build a historical record of disease occurrence, progression, or response to treatment on their specific land parcels. This absence of data prevents evidence-based decision making and makes it impossible to identify seasonal patterns, recurring hotspots, or the longitudinal effectiveness of interventions.

vi. **High cost and cloud-dependency of existing smart agriculture solutions:** Commercial precision agriculture platforms that incorporate AI-based disease detection typically require expensive subscription services, reliable broadband connectivity, and specialised hardware out of reach for smallholder farmers. Solutions that depend on cloud inference introduce unacceptable latency, ongoing operating costs, and complete failure modes when connectivity is unavailable.

This study is designed to directly address these six identified problems through the design and implementation of an affordable, offline-capable, automated IoT system that provides real-time, AI-powered crop disease detection at the point of need.

---

## 1.3 Objectives of the Study

The broad aim of this study is to design and implement an Internet of Things system that automates the detection of crop diseases using edge artificial intelligence inference on dedicated NPU hardware, coupled with continuous environmental monitoring, all presented through a local-network web dashboard.

The specific objectives of the study are:

1. To design a hardware architecture integrating the Raspberry Pi 5, Raspberry Pi AI HAT+ (Hailo-8L NPU), Pi Camera Module 3, and DHT22 temperature and humidity sensor into a functional, stable, and low-cost crop disease detection unit.

2. To develop and train a deep learning object detection model on the PlantVillage dataset, capable of identifying diseases across a minimum of five crop species with a target mean Average Precision (mAP) of at least 85% at IoU threshold 0.5.

3. To compile and deploy the trained deep learning model to the Hailo-8L NPU in Hailo Executable Format (HEF) using the Hailo Dataflow Compiler, and to validate its inference performance (throughput and latency) on the AI HAT+ hardware.

4. To implement a software inference pipeline that captures frames from the Pi Camera Module 3, preprocesses them, performs NPU-accelerated inference, and postprocesses the results to generate human-readable disease detection outputs annotated with bounding boxes, disease labels, and confidence scores.

5. To implement a sensor service that concurrently reads temperature and relative humidity from the DHT22 sensor via the GPIO interface and correlates each environmental reading with the nearest contemporaneous detection record.

6. To design and implement a relational database schema and a repository layer that persistently stores all detection records, sensor readings, and alert logs in a local SQLite database with configurable data retention.

7. To develop a RESTful API server and a browser-based monitoring dashboard accessible over the local network, allowing farmers or operators to view live detections, browse detection history with annotated images, and export data as CSV or JSON reports.

8. To implement an automated alert notification system that dispatches email (and optionally SMS) notifications when a crop disease detection event of high severity is logged by the system.

9. To validate the complete end-to-end system through structured unit and integration testing, and to evaluate the system's overall performance in terms of detection accuracy, inference latency, system resource utilisation, and sensor measurement reliability.

---

## 1.4 Research Questions

This study is guided by the following research questions:

1. To what extent can a YOLOv8-based deep learning model, trained on the PlantVillage dataset and compiled for edge deployment on the Hailo-8L NPU, achieve reliable crop disease detection accuracy (mAP ≥ 85% at IoU 0.5) under conditions representative of field use?

2. What is the inference throughput (frames per second) and per-inference latency achieved when running the compiled disease detection model on the Raspberry Pi AI HAT+ (Hailo-8L, 26 TOPS), and does this performance meet the requirements of real-time monitoring at a minimum of 10 frames per second?

3. How effectively does the integration of DHT22 environmental readings (temperature and relative humidity) with visual detection events enrich the diagnostic information available to the farmer, and is there a measurable correlation between environmental conditions and detection frequency in field tests?

4. Can the system's web dashboard and REST API, deployed over a local network without internet connectivity, provide a usable and informative interface for monitoring crop health and reviewing historical detection data?

5. What are the principal sources of error, hardware limitations, and performance bottlenecks in the implemented system, and how do they compare with the known limitations of related work in the literature?

---

## 1.5 Scope of the Study

This study focuses on the design, implementation, testing, and evaluation of a standalone IoT system for real-time crop disease detection deployed on the Raspberry Pi 5 platform with AI HAT+ hardware acceleration. The scope is defined as follows:

**In scope:**

i. Hardware integration of the Raspberry Pi 5, Raspberry Pi AI HAT+ (Hailo-8L NPU), Pi Camera Module 3, and DHT22 sensor on a breadboard prototype circuit.

ii. Software development in Python 3.11 using the Picamera2 library for camera interfacing, Adafruit CircuitPython DHT for sensor interfacing, the HailoRT SDK for NPU inference, Flask and Flask-SocketIO for the API and dashboard, and SQLAlchemy with SQLite for the data persistence layer.

iii. Deep learning model training using the publicly available PlantVillage dataset, limited to the following five crop categories: tomato, potato, maize, pepper, and apple. The total number of disease classes targeted is determined by the subset of PlantVillage labels associated with these five crops, which collectively cover fourteen distinct disease conditions plus healthy-leaf classes for each crop.

iv. Model compilation to the Hailo Executable Format (HEF) using the Hailo Dataflow Compiler on a separate CUDA-capable training machine, with INT8 post-training quantisation applied.

v. End-to-end system testing on the Raspberry Pi 5 hardware platform under controlled laboratory conditions with physical crop leaf specimens and printed test images.

vi. Performance benchmarking covering inference latency, throughput (FPS), model accuracy metrics (mAP, precision, recall, F1), and system resource utilisation (CPU, RAM, temperature).

**Out of scope:**

i. Deployment and field testing in active commercial farming environments. Due to time and resource constraints, field validation is beyond the scope of this study and is identified as future work.

ii. Multi-camera configurations, drone-mounted deployment, or satellite imagery analysis.

iii. Disease detection in crops beyond the five specified (tomato, potato, maize, pepper, apple).

iv. Prediction of disease progression or spread over time — the system provides detection of current disease presence, not forecasting.

v. Integration with external agrochemical recommendation databases or automated irrigation or pesticide dispensing actuators.

vi. Formal clinical or regulatory evaluation of the system's diagnostic outputs.

---

## 1.6 Limitations of the Study

The following limitations are acknowledged and are expected to have an effect on the generalisability and completeness of the study's findings:

i. **Dataset domain gap:** The PlantVillage dataset, while large and widely used, consists predominantly of images captured under controlled laboratory conditions with uniform white or grey backgrounds. Leaf images captured in real agricultural settings have significantly more visual complexity — variable lighting, overlapping leaves, soil and debris in the background, and variations in plant age and growth stage. The trained model may therefore exhibit reduced accuracy when deployed in natural field conditions, a phenomenon known as the domain gap problem (Mohanty et al., 2016). Addressing this would require additional data collection in Nigerian or African field settings, which is beyond the scope of this project.

ii. **DHT22 sensor sampling rate:** The DHT22 sensor has a hardware-imposed maximum sampling rate of 0.5 Hz, meaning it can provide at most one reading every two seconds. This limits the temporal resolution of environmental data and means that rapid microclimatic changes at the leaf surface may not be captured between sampling intervals.

iii. **Fixed single-camera field of view:** The Pi Camera Module 3 covers a fixed field of view determined by its 120° wide-angle lens. A single camera unit can only monitor a limited section of crop canopy at any one time. Comprehensive monitoring of a full-scale farming plot would require multiple units, which introduces cost and complexity not addressed in this study.

iv. **SQLite concurrency constraints:** SQLite, while appropriate for a single-node embedded system, has well-known limitations under concurrent write workloads. Should the system be extended to support multiple simultaneous data-writing services in a future version, migration to a more robust database engine such as PostgreSQL would be necessary.

v. **Prototype-level hardware assembly:** The current hardware implementation uses a solderless breadboard, which, while suitable for a university prototype, introduces susceptibility to vibration-induced connection failures and is not weatherproof. A production-grade deployment would require a custom PCB and an enclosure rated for outdoor conditions.

vi. **Alert delivery network dependency:** While the system is designed to operate without internet connectivity for its core detection and monitoring functions, the alert notification subsystem (email and SMS) requires at minimum periodic network access to deliver messages. In fully off-grid environments without mobile data coverage, this feature would be unavailable.

vii. **Training hardware dependency:** Model training and compilation require a separate machine with a CUDA-capable GPU and the Hailo Dataflow Compiler installed. This represents a barrier to updating or retraining the model without access to appropriate training infrastructure.

---

## 1.7 Significance of the Study

This study makes contributions of practical, academic, and social significance, as outlined below.

**Practical Significance:**

The system developed in this study provides a concrete, low-cost, and deployable tool that directly addresses one of the most damaging threats to agricultural productivity in developing nations. A fully assembled unit using the specified hardware components — Raspberry Pi 5, AI HAT+, Pi Camera Module 3, DHT22 sensor, and supporting peripherals — can be built for a fraction of the cost of commercial precision agriculture platforms, while operating entirely without internet connectivity. This economic and operational accessibility makes the system a viable option for smallholder farmers, agricultural cooperatives, government extension services, and non-governmental organisations working in food security.

By providing real-time, automated disease alerts, the system enables intervention at the earliest detectable stage of disease onset, before spread has rendered treatment ineffective. Even modest improvements in early detection rates can translate to significant reductions in crop losses. Given that Nigeria's agricultural sector supports over 70% of the rural population and contributes approximately 22% of GDP (World Bank, 2023), technology that improves crop disease management carries substantial national economic significance.

**Academic Significance:**

This study contributes to the body of academic literature on edge AI for precision agriculture, an area of active and growing research interest. Specifically, it provides an empirical evaluation of the Raspberry Pi AI HAT+ (Hailo-8L NPU) for agricultural computer vision — one of the first such published evaluations in the Nigerian academic literature. The study documents the full pipeline from dataset preparation and YOLOv8 model training through Hailo DFC compilation, INT8 quantisation, and edge deployment, providing a reproducible workflow that future researchers can build upon.

The integration of visual disease detection with concurrent environmental sensing — correlating detection events with real-time temperature and humidity readings — represents a more holistic approach to automated crop health monitoring than is found in the majority of prior work, which typically treats image classification in isolation from its environmental context.

**Social and Developmental Significance:**

Food insecurity remains one of the most pressing challenges facing Nigeria and the African continent. The FAO (2022) estimates that approximately 257 million people in sub-Saharan Africa face acute food insecurity. Technology that can meaningfully reduce crop losses directly contributes to improving food availability and stability. Furthermore, the development of locally built, open-source agricultural technology by Nigerian software engineering students and researchers contributes to the broader goal of technological self-sufficiency, reduces dependency on imported solutions designed for conditions very different from those of the Nigerian agricultural environment, and builds local capacity and expertise in embedded systems, artificial intelligence, and IoT engineering.

**Educational Significance:**

This project serves as an applied demonstration of the intersection of multiple software engineering disciplines — embedded systems programming, machine learning, API development, database design, real-time systems, and user interface design — within a single, coherent, and practically motivated system. As such, it provides a pedagogical model for project-based learning in software engineering programmes and illustrates how theoretical computer science and software engineering concepts can be applied to solve real-world problems in the Nigerian context.

---

## 1.8 Definition of Terms

The following terms are used throughout this research report and are defined here for clarity:

**Artificial Intelligence (AI):** A field of computer science concerned with the creation of systems that can perform tasks that would normally require human intelligence, including visual perception, decision making, language understanding, and pattern recognition.

**Bounding Box:** A rectangular region drawn around an object of interest within an image, used in object detection models to indicate the position and extent of a detected entity. In this system, bounding boxes are drawn around diseased regions of leaf images.

**Convolutional Neural Network (CNN):** A class of deep learning model specifically designed for processing grid-structured data such as images. CNNs use convolutional layers to automatically learn hierarchical spatial features from raw pixel data and are the dominant architecture for computer vision tasks.

**Deep Learning:** A subfield of machine learning that uses artificial neural networks with multiple hidden layers to learn complex, non-linear representations of data. Deep learning underpins the crop disease detection model used in this system.

**DHT22:** A digital temperature and relative humidity sensor manufactured by Aosong Electronics, capable of measuring temperatures from -40°C to +80°C with ±0.5°C accuracy and relative humidity from 0% to 100% with ±2–5% accuracy, communicating over a single-wire digital protocol at a maximum rate of 0.5 Hz.

**Edge AI (Edge Inference):** The execution of artificial intelligence model inference computations directly on a local device at the point of data collection — as opposed to transmitting data to a remote cloud server for processing. Edge AI reduces latency, eliminates cloud dependency, and preserves data privacy.

**Flask:** A lightweight Python web framework based on the WSGI standard, used in this project to implement the REST API server and web dashboard.

**General Purpose Input/Output (GPIO):** A set of programmable digital pins on a microcontroller or single-board computer that can be configured as either input or output, used in this project to interface the Raspberry Pi 5 with the DHT22 sensor.

**Hailo Dataflow Compiler (DFC):** A software toolchain provided by Hailo Technologies for compiling pre-trained neural network models (typically in ONNX format) to the Hailo Executable Format (HEF), applying quantisation and hardware-specific optimisations for deployment on Hailo NPU devices.

**Hailo Executable Format (HEF):** A proprietary binary file format produced by the Hailo Dataflow Compiler, containing a quantised and hardware-optimised neural network model ready for execution on a Hailo NPU device.

**HailoRT SDK:** The Hailo Runtime software development kit, providing C++ and Python APIs for loading HEF model files onto Hailo NPU hardware and executing inference operations.

**Inference:** The phase of a neural network's use in which the trained model receives new, unseen input data and produces a prediction or output, as opposed to the training phase in which the model's weights are updated based on labelled data.

**Internet of Things (IoT):** A paradigm in which physical devices — sensors, actuators, cameras, and other hardware — are embedded with software, connectivity, and sensing capabilities that allow them to collect data from the physical world and communicate it to other devices or systems, enabling automated monitoring and control.

**Mean Average Precision (mAP):** A standard performance metric for object detection models, computed as the mean of the Average Precision (AP) values across all object classes. mAP@0.5 refers to mAP computed at an Intersection over Union (IoU) threshold of 0.5, meaning a detection is counted as correct only if the predicted bounding box overlaps the ground truth box by at least 50%.

**Neural Processing Unit (NPU):** A type of microprocessor specifically designed and optimised for the matrix multiplication and tensor operations that dominate neural network inference workloads, offering significantly higher efficiency than general-purpose CPUs or GPUs for these tasks.

**Non-Maximum Suppression (NMS):** A post-processing algorithm applied to the raw output of object detection models to eliminate redundant overlapping bounding boxes, retaining only the highest-confidence detection for each distinct object instance.

**ONNX (Open Neural Network Exchange):** An open standard file format and ecosystem for representing machine learning models, enabling interoperability between different deep learning frameworks and deployment toolchains.

**PCIe (Peripheral Component Interconnect Express):** A high-speed serial computer expansion bus standard used in this project as the communication interface between the Raspberry Pi 5 and the AI HAT+ carrying the Hailo-8L NPU.

**Picamera2:** The official open-source Python library for interfacing with the Raspberry Pi Camera Module 3 (and other Pi camera variants) under Raspberry Pi OS Bookworm, based on the libcamera stack.

**PlantVillage Dataset:** A large, publicly available dataset of labelled plant leaf images developed at Pennsylvania State University, containing over 87,000 images spanning 38 disease classes across 14 crop species, widely used as the benchmark dataset for training and evaluating plant disease detection models.

**Raspberry Pi 5:** The fifth generation of the Raspberry Pi single-board computer, featuring a Broadcom BCM2712 quad-core ARM Cortex-A76 processor running at up to 2.4 GHz, up to 8 GB LPDDR4X RAM, and a PCIe 2.0 interface exposed through the 40-pin HAT connector for accessory expansion.

**Raspberry Pi AI HAT+:** An official Raspberry Pi accessory that integrates a Hailo-8L neural processing unit onto a standard Raspberry Pi HAT (Hardware Attached on Top) form factor, communicating with the Raspberry Pi 5 via PCIe Gen 3 to provide 26 TOPS of on-device AI inference acceleration.

**REST API (Representational State Transfer Application Programming Interface):** An architectural style for building networked application interfaces that uses standard HTTP methods (GET, POST, DELETE) and stateless communication, returning data in JSON format. Used in this project to expose detection and sensor data to the web dashboard and external clients.

**SQLite:** A self-contained, serverless, zero-configuration relational database engine stored as a single file on disk. SQLite is used in this project as the local data store for detection records, sensor readings, and alert logs.

**TOPS (Tera Operations Per Second):** A unit of measure for the computational throughput of AI accelerators, representing one trillion (10¹²) arithmetic operations (typically integer multiply-accumulate operations) per second. The Hailo-8L NPU in the AI HAT+ is rated at 26 TOPS.

**WebSocket:** A full-duplex, persistent communication protocol over a single TCP connection, used in this project via Flask-SocketIO to push real-time detection and sensor update events from the server to connected browser clients without requiring client-side polling.

**YOLOv8 (You Only Look Once, version 8):** A state-of-the-art, single-stage real-time object detection neural network architecture developed by Ultralytics, offering a family of models (YOLOv8n, YOLOv8s, YOLOv8m, etc.) that trade off between speed and accuracy. YOLOv8 is selected in this project as the base architecture for the crop disease detection model due to its strong performance, active maintenance, and straightforward ONNX export capability.

---

## References

Elijah, O., Rahman, T. A., Orikumhi, I., Leow, C. Y., & Hindia, M. N. (2018). An overview of Internet of Things (IoT) and data analytics in agriculture: Benefits and challenges. *IEEE Internet of Things Journal*, *5*(5), 3758–3773. https://doi.org/10.1109/JIOT.2018.2844296

Food and Agriculture Organisation of the United Nations (FAO). (2022). *The State of Food and Agriculture 2022: Leveraging Automation in Agriculture*. FAO. https://doi.org/10.4060/cb9479en

Fry, W. E. (2008). *Phytophthora infestans*: The plant (and R gene) destroyer. *Molecular Plant Pathology*, *9*(3), 385–402. https://doi.org/10.1111/j.1364-3703.2007.00465.x

Mohanty, S. P., Hughes, D. P., & Salathé, M. (2016). Using deep learning for image-based plant disease detection. *Frontiers in Plant Science*, *7*, Article 1419. https://doi.org/10.3389/fpls.2016.01419

National Agricultural Extension and Research Liaison Service (NAERLS). (2021). *Agricultural performance survey of 2020 wet season in Nigeria*. Ahmadu Bello University. https://naerls.gov.ng/wp-content/uploads/2022/11/Agricultural-Performance-Survey-of-2020-Wet-Season-in-Nigeria.pdf

Savary, S., Willocquet, L., Pethybridge, S. J., Esker, P., McRoberts, N., & Nelson, A. (2019). The global burden of pathogens and pests on major food crops. *Nature Ecology & Evolution*, *3*(3), 430–439. https://doi.org/10.1038/s41559-018-0793-y

World Bank. (2023). *Agriculture overview: Nigeria*. The World Bank Group. https://www.worldbank.org/en/topic/agriculture/overview
