# CHAPTER ONE

# INTRODUCTION

## 1.1 Background to the Study

Agriculture remains one of the most fundamental pillars of human civilisation, serving as the primary source of food, raw materials, and economic livelihood for billions of people worldwide. In Nigeria and across sub-Saharan Africa, agriculture accounts for a substantial proportion of gross domestic product (GDP) and provides the main source of income for the majority of the rural population. According to the Food and Agriculture Organisation of the United Nations, approximately 600 million smallholder farming households worldwide depend on agriculture for their survival, and this sector feeds over 70% of the global population (FAO, 2022). Despite its central importance, agricultural productivity continues to be severely threatened by a wide range of biotic stressors, chief among them being plant diseases caused by fungal, bacterial, viral, and oomycete pathogens.

Plant diseases are responsible for pre-harvest losses estimated to affect between 20% and 40% of global agricultural production annually, translating to economic losses in excess of $220 billion per year (Savary et al., 2019). In developing nations, where smallholder farmers lack access to diagnostic laboratories, agricultural extension officers, or reliable internet connectivity, these losses are disproportionately severe. Tomato production is particularly vulnerable because diseases such as Bacterial Spot, Early Blight, Late Blight, Leaf Mould, and Septoria Leaf Spot can reduce leaf health, fruit quality, and final yield when they are not recognised and managed promptly. Late Blight, caused by *Phytophthora infestans*, remains one of the most destructive tomato diseases and continues to cause substantial agricultural losses (Fry, 2008).

Traditional methods of crop disease diagnosis rely heavily on human expert observation — agronomists or experienced farmers visually inspecting plants and making judgements based on symptom patterns. This approach suffers from several fundamental limitations. It is inherently subjective, dependent on the knowledge and experience of the individual. It is not scalable across large farm areas. It is slow, as symptoms must reach a visible threshold before detection is possible. And it is unavailable to the majority of smallholder farmers who lack proximity to agricultural specialists. Laboratory-based diagnostic methods such as polymerase chain reaction (PCR) and ELISA testing provide greater accuracy but require expensive equipment, trained laboratory personnel, and days or weeks of turnaround time — entirely incompatible with the time-sensitive nature of farm management decisions.

The convergence of the Internet of Things (IoT), computer vision, and artificial intelligence (AI) over the past decade has opened a new paradigm for precision agriculture. IoT systems integrate physical sensing hardware with software services to collect, transmit, and analyse real-world data in near real time. In the agricultural domain, IoT applications have been explored for soil moisture monitoring, irrigation automation, pest detection, weather station networks, and livestock health monitoring (Elijah et al., 2018). The integration of camera-based computer vision into these systems creates the possibility of automated, continuous, and non-destructive monitoring of crop health from the leaf level.

Deep learning, a subfield of machine learning characterised by the use of multi-layered artificial neural networks, has demonstrated remarkable success in image classification tasks. Convolutional Neural Networks (CNNs) in particular have been shown to achieve accuracy levels comparable to or exceeding that of human experts in plant disease identification tasks. The landmark work of Mohanty, Hughes, and Salathé, using the PlantVillage dataset of over 54,000 labelled leaf images, demonstrated that a deep learning model could classify 26 diseases across 14 crop species with accuracy approaching 99.35% under controlled conditions (Mohanty et al., 2016). Lightweight architectures such as MobileNetV2 reduce computational cost through efficient convolutional operations and are therefore suitable candidates for tomato disease classification on constrained edge hardware (Howard et al., 2017).

However, a major barrier to the practical deployment of these systems in real agricultural settings has been the computational cost of running deep neural network inference. Models capable of high accuracy may require cloud servers or GPU acceleration, thereby introducing latency, cost, and internet dependency. The emergence of dedicated Neural Processing Units (NPUs) makes it possible to execute compact classification models locally. The Raspberry Pi AI HAT+ integrates a Hailo accelerator with the Raspberry Pi 5 through PCIe. The available AI HAT+ variants use either the 13-TOPS Hailo-8L or the 26-TOPS Hailo-8; the exact installed variant will be recorded before model compilation and hardware benchmarking. This platform provides a practical path for running a lightweight tomato disease classifier without continuous cloud access.

This project, therefore, seeks to design and implement a fully integrated IoT system for the automated classification of selected tomato diseases. The system combines the Raspberry Pi 5 single-board computer as its central processing unit with the Raspberry Pi AI HAT+ for hardware-accelerated inference, the Pi Camera Module 3 for tomato leaf image capture, and a DHT22 environmental sensor for the concurrent collection of temperature and relative humidity data. These two data streams, visual and environmental, are correlated and persisted in a local database, made accessible through a REST API, and presented to users through a browser-based monitoring dashboard. Automated alerts are dispatched when high-severity tomato disease events are classified with sufficient confidence. The core system is designed to operate independently of internet connectivity, making it suitable for deployment in rural and off-grid agricultural environments.

---

## 1.2 Statement of Problem

Despite the well-documented economic and humanitarian cost of crop diseases, the vast majority of smallholder farmers — particularly in sub-Saharan Africa and other developing regions — continue to rely on manual, unaided visual inspection as their primary means of plant health monitoring. This practice is not only inadequate but creates a cascade of problems that collectively undermine agricultural productivity and food security.

The specific problems motivating this research are identified as follows:

**1. Late and inaccurate disease diagnosis:** Manual visual inspection of crops requires diseases to reach an advanced, visually obvious stage before a farmer or agronomist can identify them. By this point, the pathogen population within the plant has often already proliferated to a level that makes treatment ineffective and cross-contamination of neighbouring plants probable. Studies have shown that detection delays of as few as five to seven days in diseases like tomato Late Blight can result in the loss of an entire growing season (Fry, 2008).

**2. Absence of objective and consistent diagnosis:** Human diagnosis of plant disease symptoms is inherently subjective and varies significantly based on the expertise, experience, and even fatigue of the observer. Symptoms of different diseases can share visual similarities — for example, Early Blight and Septoria Leaf Spot on tomato both present as dark lesions on leaves — leading to misdiagnosis and inappropriate treatment with incorrect pesticides, which wastes resources and may accelerate the development of pathogen resistance.

**3. Inaccessibility of expert knowledge at point of need:** Qualified plant pathologists, agricultural extension officers, and diagnostic laboratory services are concentrated in urban centres and are largely inaccessible to smallholder farmers at the farm level, particularly in rural areas of Nigeria and across Africa. This geographic and economic barrier means that most farmers are forced to make pest management decisions without adequate information.

**4. Lack of integration with environmental context:** Crop diseases do not develop in isolation from their environment. The spread and severity of many diseases are strongly influenced by environmental conditions, particularly temperature and relative humidity. For instance, Late Blight in tomatoes proliferates most rapidly when relative humidity exceeds 90% and temperatures are between 10°C and 20°C (Fry, 2008). Existing manual inspection approaches do not correlate disease observations with environmental readings, eliminating a critical dimension of diagnostic and predictive information.

**5. Absence of historical disease data:** Without an automated logging and data persistence system, farmers have no mechanism to build a historical record of disease occurrence, progression, or response to treatment on their specific land parcels. This absence of data prevents evidence-based decision making and makes it impossible to identify seasonal patterns, recurring hotspots, or the longitudinal effectiveness of interventions.

**6. High cost and cloud-dependency of existing smart agriculture solutions:** Commercial precision agriculture platforms that incorporate AI-based disease detection typically require expensive subscription services, reliable broadband connectivity, and specialised hardware out of reach for smallholder farmers. Solutions that depend on cloud inference introduce unacceptable latency, ongoing operating costs, and complete failure modes when connectivity is unavailable (Elijah et al., 2018).

This study is designed to directly address these six identified problems through the design and implementation of an affordable, offline-capable IoT system that provides timely, AI-powered classification of selected tomato diseases at the point of need.

---

## 1.3 Objectives of the Study

The broad aim of this study is to design and implement an Internet of Things system that classifies selected tomato diseases using edge artificial intelligence inference on dedicated NPU hardware, coupled with continuous environmental monitoring and presented through a local-network web dashboard.

The specific objectives of the study are:

1. To design a hardware architecture integrating the Raspberry Pi 5, Raspberry Pi AI HAT+, Pi Camera Module 3, and DHT22 temperature and humidity sensor into a functional, stable, and low-cost tomato disease classification unit, directly addressing Problem 6 (cost and hardware accessibility).

2. To develop and train a tomato-only MobileNetV2 image-classification model using the PlantVillage tomato subset to distinguish Bacterial Spot, Early Blight, Late Blight, Leaf Mould, and Septoria Leaf Spot, with target classification accuracy and macro F1-score of at least 85% on the held-out test subset, directly addressing Problem 2 (absence of objective diagnosis) (Mohanty et al., 2016; Howard et al., 2017).

3. To export the trained classification model to ONNX, compile it to Hailo Executable Format (HEF) using the Hailo Dataflow Compiler for the installed AI HAT+ variant, and validate its inference throughput and latency on the target hardware, directly addressing Problem 1 (late diagnosis) by enabling timely local classification.

4. To implement a software inference pipeline that captures tomato leaf frames from the Pi Camera Module 3, resizes and normalises them, performs NPU-accelerated classification, and produces human-readable outputs containing the predicted disease label, confidence score, and prediction status, directly addressing Problem 2 (inconsistent diagnosis).

5. To implement a sensor service that concurrently reads temperature and relative humidity from the DHT22 sensor via the GPIO interface and correlates each environmental reading with the nearest contemporaneous tomato classification record, directly addressing Problem 4 (lack of environmental context).

6. To design and implement a relational database schema and a repository layer that persistently stores all classification records, sensor readings, and alert logs in a local SQLite database with configurable data retention, directly addressing Problem 5 (absence of historical disease data).

7. To develop a RESTful API server and a browser-based monitoring dashboard accessible over the local network, allowing farmers or operators to view live tomato disease predictions, browse classification history with labelled images, and export data as CSV or JSON reports, directly addressing Problem 3 (inaccessibility of expert knowledge).

8. To implement an automated alert notification system that dispatches email and, optionally, SMS notifications when a high-severity tomato disease is classified with sufficient confidence.

9. To validate the complete end-to-end system through structured unit and integration testing, and to evaluate the system's overall performance in terms of classification accuracy, macro F1-score, inference latency, system resource utilisation, and sensor measurement reliability.

---

## 1.4 Research Questions

This study is guided by the following research questions:

1. To what extent can a MobileNetV2 model, trained on the selected PlantVillage tomato disease classes and compiled for deployment on the Raspberry Pi AI HAT+, achieve classification accuracy and macro F1-score of at least 85% under the defined controlled test conditions?

2. What inference throughput and per-image latency are achieved when the compiled tomato disease classifier runs on the installed Raspberry Pi AI HAT+ variant, and does the performance meet the requirement of processing at least 10 frames per second under the defined benchmark conditions?

3. How effectively does the integration of DHT22 environmental readings with tomato disease classification events enrich the information available to the farmer, and what relationship is observed between environmental conditions and classification frequency during controlled prototype tests?

4. Can the system's web dashboard and REST API, deployed over a local network without internet connectivity, provide a usable and informative interface for monitoring tomato leaf classifications and reviewing historical records?

5. What are the principal sources of error, hardware limitations, and performance bottlenecks in the implemented system, and how do they compare with the known limitations of related work in the literature?

---

## 1.5 Scope of the Study

This study focuses on the design, implementation, testing, and evaluation of a standalone IoT system for tomato disease classification deployed on the Raspberry Pi 5 platform with AI HAT+ hardware acceleration. The scope is defined as follows:

**In scope:**

i. Hardware integration of the Raspberry Pi 5, Raspberry Pi AI HAT+, Pi Camera Module 3, and DHT22 sensor on a breadboard prototype circuit. The installed Hailo accelerator variant and rated TOPS will be recorded during hardware setup.

ii. Software development in Python 3.11 using the Picamera2 library for camera interfacing, Adafruit CircuitPython DHT for sensor interfacing, the HailoRT SDK for NPU inference, Flask and Flask-SocketIO for the API and dashboard, and SQLAlchemy with SQLite for the data persistence layer.

iii. Deep learning model training using the publicly available PlantVillage tomato subset, limited to Bacterial Spot, Early Blight, Late Blight, Leaf Mould, and Septoria Leaf Spot. The model performs one image-level classification for each accepted tomato leaf input.

iv. Model compilation to the Hailo Executable Format (HEF) using the Hailo Dataflow Compiler on a separate CUDA-capable training machine, with INT8 post-training quantisation applied.

v. End-to-end system testing on the Raspberry Pi 5 hardware platform under controlled laboratory conditions with physical tomato leaf specimens and printed tomato disease test images.

vi. Performance benchmarking covering inference latency, throughput, classification accuracy, macro and per-class precision, recall, F1-score, confusion-matrix analysis, and system resource utilisation (CPU, RAM, and device temperature).

**Out of scope:**

i. Deployment and field testing in active commercial farming environments. Due to time and resource constraints, field validation is beyond the scope of this study and is identified as future work.

ii. Multi-camera configurations, drone-mounted deployment, or satellite imagery analysis.

iii. Classification of crops other than tomato and classification of tomato conditions outside the five selected disease classes.

iv. Prediction of disease progression or spread over time. The system classifies the current image and does not perform disease forecasting.

v. Localisation of multiple diseased regions with bounding boxes or simultaneous classification of several leaves within one frame.

vi. Integration with external agrochemical recommendation databases or automated irrigation or pesticide dispensing actuators.

vii. Formal clinical or regulatory evaluation of the system's diagnostic outputs.

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

By providing real-time, automated disease alerts, the system enables intervention at the earliest detectable stage of disease onset, before spread has rendered treatment ineffective. Even modest improvements in early detection rates can translate to significant reductions in crop losses. Given that Nigeria's agricultural sector supports over 70% of the rural population and contributes approximately 22% of GDP, technology that improves crop disease management carries substantial national economic significance (World Bank, 2023).

**Academic Significance:**

This study contributes to the body of academic literature on edge AI for precision agriculture, an area of active and growing research interest. Specifically, it provides an empirical evaluation of a lightweight MobileNetV2 tomato disease classifier deployed on the Raspberry Pi AI HAT+. The study documents the full pipeline from tomato dataset preparation and transfer learning through ONNX export, Hailo DFC compilation, INT8 quantisation, and edge deployment, providing a reproducible workflow that future researchers can build upon.

The integration of tomato disease classification with concurrent environmental sensing, correlating classification events with real-time temperature and humidity readings, represents a more holistic approach to automated tomato health monitoring than is found in prior work that treats image classification in isolation from its environmental context.

**Social and Developmental Significance:**

Food insecurity remains one of the most pressing challenges facing Nigeria and the African continent. The FAO estimates that approximately 257 million people in sub-Saharan Africa face acute food insecurity (FAO, 2022). Technology that can meaningfully reduce crop losses directly contributes to improving food availability and stability. Furthermore, the development of locally built, open-source agricultural technology by Nigerian software engineering students and researchers contributes to the broader goal of technological self-sufficiency, reduces dependency on imported solutions designed for conditions very different from those of the Nigerian agricultural environment, and builds local capacity and expertise in embedded systems, artificial intelligence, and IoT engineering.

**Educational Significance:**

This project serves as an applied demonstration of the intersection of multiple software engineering disciplines — embedded systems programming, machine learning, API development, database design, real-time systems, and user interface design — within a single, coherent, and practically motivated system. As such, it provides a pedagogical model for project-based learning in software engineering programmes and illustrates how theoretical computer science and software engineering concepts can be applied to solve real-world problems in the Nigerian context.

---

## 1.8 Definition of Terms

The following terms are used throughout this research report and are defined here for clarity:

**Artificial Intelligence (AI):** A field of computer science concerned with the creation of systems that can perform tasks that would normally require human intelligence, including visual perception, decision making, language understanding, and pattern recognition.

**Classification Accuracy:** The proportion of test images for which the model predicts the correct tomato disease class.

**Convolutional Neural Network (CNN):** A class of deep learning model specifically designed for processing grid-structured data such as images. CNNs use convolutional layers to automatically learn hierarchical spatial features from raw pixel data and are the dominant architecture for computer vision tasks.

**Deep Learning:** A subfield of machine learning that uses artificial neural networks with multiple hidden layers to learn complex, non-linear representations of data. Deep learning underpins the tomato disease classification model used in this system.

**DHT22:** A digital temperature and relative humidity sensor manufactured by Aosong Electronics, capable of measuring temperatures from -40°C to +80°C with ±0.5°C accuracy and relative humidity from 0% to 100% with ±2–5% accuracy, communicating over a single-wire digital protocol at a maximum rate of 0.5 Hz.

**Edge AI (Edge Inference):** The execution of artificial intelligence model inference computations directly on a local device at the point of data collection — as opposed to transmitting data to a remote cloud server for processing. Edge AI reduces latency, eliminates cloud dependency, and preserves data privacy.

**Flask:** A lightweight Python web framework based on the WSGI standard, used in this project to implement the REST API server and web dashboard.

**General Purpose Input/Output (GPIO):** A set of programmable digital pins on a microcontroller or single-board computer that can be configured as either input or output, used in this project to interface the Raspberry Pi 5 with the DHT22 sensor.

**Hailo Dataflow Compiler (DFC):** A software toolchain provided by Hailo Technologies for compiling pre-trained neural network models (typically in ONNX format) to the Hailo Executable Format (HEF), applying quantisation and hardware-specific optimisations for deployment on Hailo NPU devices.

**Hailo Executable Format (HEF):** A proprietary binary file format produced by the Hailo Dataflow Compiler, containing a quantised and hardware-optimised neural network model ready for execution on a Hailo NPU device.

**HailoRT SDK:** The Hailo Runtime software development kit, providing C++ and Python APIs for loading HEF model files onto Hailo NPU hardware and executing inference operations.

**Inference:** The phase of a neural network's use in which the trained model receives new, unseen input data and produces a prediction or output, as opposed to the training phase in which the model's weights are updated based on labelled data.

**Internet of Things (IoT):** A paradigm in which physical devices — sensors, actuators, cameras, and other hardware — are embedded with software, connectivity, and sensing capabilities that allow them to collect data from the physical world and communicate it to other devices or systems, enabling automated monitoring and control.

**Image Classification:** A computer-vision task in which a model assigns one class label to an input image. In this study, the label represents one of the five selected tomato diseases.

**Macro F1-Score:** The arithmetic mean of the class-specific F1-scores, giving equal importance to each disease class regardless of the number of test images in that class.

**Neural Processing Unit (NPU):** A type of microprocessor specifically designed and optimised for the matrix multiplication and tensor operations that dominate neural network inference workloads, offering significantly higher efficiency than general-purpose CPUs or GPUs for these tasks.

**MobileNetV2:** A lightweight convolutional neural-network architecture that uses efficient inverted residual and depthwise separable convolution operations. It is used as the base architecture for tomato disease classification in this study.

**ONNX (Open Neural Network Exchange):** An open standard file format and ecosystem for representing machine learning models, enabling interoperability between different deep learning frameworks and deployment toolchains.

**PCIe (Peripheral Component Interconnect Express):** A high-speed serial computer expansion bus standard used in this project as the communication interface between the Raspberry Pi 5 and the AI HAT+ carrying the Hailo accelerator.

**Picamera2:** The official open-source Python library for interfacing with the Raspberry Pi Camera Module 3 (and other Pi camera variants) under Raspberry Pi OS Bookworm, based on the libcamera stack.

**PlantVillage Dataset:** A large, publicly available dataset of labelled plant leaf images spanning several crops and disease classes. This study uses only the tomato images belonging to the five selected disease classes for training and evaluating the classifier.

**Raspberry Pi 5:** The fifth generation of the Raspberry Pi single-board computer, featuring a Broadcom BCM2712 quad-core ARM Cortex-A76 processor running at up to 2.4 GHz, up to 8 GB LPDDR4X RAM, and a PCIe 2.0 interface exposed through the 40-pin HAT connector for accessory expansion.

**Raspberry Pi AI HAT+:** An official Raspberry Pi accessory that integrates a Hailo neural processing unit with the Raspberry Pi 5 through PCIe. AI HAT+ variants are available with a 13-TOPS Hailo-8L or a 26-TOPS Hailo-8 accelerator; the installed variant determines the compilation target used in this study.

**REST API (Representational State Transfer Application Programming Interface):** An architectural style for building networked application interfaces that uses standard HTTP methods and stateless communication, returning data in JSON format. It is used in this project to expose classification and sensor data to the web dashboard and external clients.

**SQLite:** A self-contained, serverless, zero-configuration relational database engine stored as a single file on disk. SQLite is used in this project as the local data store for classification records, sensor readings, and alert logs.

**TOPS (Tera Operations Per Second):** A unit of measure for the computational throughput of AI accelerators, representing one trillion (10¹²) arithmetic operations per second. The AI HAT+ is available in 13-TOPS Hailo-8L and 26-TOPS Hailo-8 variants.

**WebSocket:** A full-duplex, persistent communication protocol over a single TCP connection, used in this project via Flask-SocketIO to push real-time classification and sensor update events from the server to connected browser clients without requiring client-side polling.

---

## References

Food and Agriculture Organisation of the United Nations (FAO) (2022): "The State of Food and Agriculture 2022: Leveraging Automation in Agriculture," in: *FAO*, Rome. https://doi.org/10.4060/cb9479en

Savary, S., Willocquet, L., Pethybridge, S. J., Esker, P., McRoberts, N., and Nelson, A. (2019): "The global burden of pathogens and pests on major food crops," in: *Nature Ecology & Evolution*, Vol. 3, No. 3, pp. 430–439. https://doi.org/10.1038/s41559-018-0793-y

Fry, W. E. (2008): "*Phytophthora infestans*: The plant (and R gene) destroyer," in: *Molecular Plant Pathology*, Vol. 9, No. 3, pp. 385–402. https://doi.org/10.1111/j.1364-3703.2007.00465.x

Elijah, O., Rahman, T. A., Orikumhi, I., Leow, C. Y., and Hindia, M. N. (2018): "An overview of Internet of Things (IoT) and data analytics in agriculture: Benefits and challenges," in: *IEEE Internet of Things Journal*, Vol. 5, No. 5, pp. 3758–3773. https://doi.org/10.1109/JIOT.2018.2844296

Mohanty, S. P., Hughes, D. P., and Salathé, M. (2016): "Using deep learning for image-based plant disease detection," in: *Frontiers in Plant Science*, Vol. 7, Article 1419. https://doi.org/10.3389/fpls.2016.01419

Howard, A. G., Zhu, M., Chen, B., Kalenichenko, D., Wang, W., Weyand, T., Andreetto, M., and Adam, H. (2017): "MobileNets: Efficient Convolutional Neural Networks for Mobile Vision Applications," in: *arXiv preprint arXiv:1704.04861*.

World Bank (2023): "Agriculture overview: Nigeria," in: *The World Bank Group*. https://www.worldbank.org/en/topic/agriculture/overview
