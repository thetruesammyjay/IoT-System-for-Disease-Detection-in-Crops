# CHAPTER FIVE

# SUMMARY, CONCLUSION AND RECOMMENDATIONS

## 5.1 Summary of Findings

This study designed and implemented a prototype Internet of Things system for tomato disease classification and environmental monitoring. The system combines image acquisition, a MobileNetV2 classifier, temperature and humidity measurements, local data storage, a REST API, and a browser dashboard. It is intended to operate at the edge so that the main monitoring workflow does not depend on a continuous internet connection. Development followed an iterative approach because the software, model, sensors, and target hardware required separate implementation and integration checks.

The classifier was trained for five PlantVillage tomato disease classes: Bacterial Spot, Early Blight, Late Blight, Leaf Mould, and Septoria Leaf Spot. Dataset preparation validated image files, removed exact duplicates, and produced reproducible training, validation, and test manifests using seed 42. Eight duplicate Late Blight images were removed, leaving 7,751 unique images. Of these, 6,203 were assigned to training, 774 to validation, and 774 to testing. The held-out test set was kept separate from training and model selection.

The selected MobileNetV2 checkpoint was produced at epoch 5, evaluated on the held-out test set, and exported to ONNX. The model achieved 97.93% accuracy and a 97.97% macro F1-score, exceeding the study's 85% targets for those two measures on this controlled test set. Macro precision was 98.09% and macro recall was 97.90%. All five class F1-scores exceeded 96%; Leaf Mould had the highest F1-score at 99.48%, while Early Blight had the lowest recall at 95.00%. Septoria Leaf Spot had the lowest precision at 94.62% and received several false-positive predictions from the other classes. These metrics apply to the PlantVillage test images; performance on field photographs remains to be measured.

The application implements a shared pipeline for simulated and ONNX inference. It converts images to RGB, resizes them to 224 by 224 pixels, applies ImageNet normalisation, and produces one predicted disease class with its probability distribution. A confidence threshold of 0.70 marks a result as accepted; a lower-confidence result is stored as uncertain. The five-class model has no healthy or open-set class. Its uncertain status identifies a low-confidence result among the configured classes; it does not identify healthy leaves or unrecognised diseases.

The software includes generated leaf-like images and repeatable simulated temperature and humidity measurements for desktop development and testing. The physical camera and DHT22 adapters are implemented, and the SQLite repository saves a classification together with its associated sensor reading in one transaction. The Flask API supports detection and sensor queries, monitoring controls, uploaded-image inference, and CSV or JSON exports. The dashboard presents system status, recent classifications, environmental trends, and image-upload analysis. The recorded automated test run passed all 36 tests, and desktop functional tests exercised the route from simulated or supplied images through storage and dashboard retrieval.

The extent to which the objectives were achieved is summarized below.

| Study objective | Finding |
|---|---|
| Design the Raspberry Pi, camera, sensor, and accelerator architecture | The modular architecture, configuration, and hardware adapters were prepared. Physical integration and acceptance testing remain outstanding. |
| Train and evaluate a five-class MobileNetV2 model | Achieved on the held-out PlantVillage test set; accuracy and macro F1-score exceeded the 85% targets. |
| Export the model and deploy it on Hailo hardware | ONNX export and desktop ONNX Runtime inference were completed. Hailo compilation, runtime integration, and NPU testing remain outstanding. |
| Implement image preprocessing and classification | Implemented for simulation and ONNX inference, with confidence-aware accepted and uncertain statuses. |
| Read DHT22 measurements and associate them with detections | Sensor adapters and database association are implemented. Physical sensor reliability and environmental-disease relationships have not been measured. |
| Persist classifications, readings, and alerts | Classification and sensor records are stored transactionally in SQLite. Alert delivery, alert logging, and configurable retention are not implemented. |
| Provide a REST API, dashboard, and reports | API, dashboard, monitoring controls, image uploads, and CSV/JSON exports are implemented and covered by software tests. Formal farmer usability testing remains outstanding. |
| Send high-severity email or SMS alerts | Not implemented in the current prototype. |
| Test the complete system and measure performance | Automated software tests and desktop simulations were completed. Physical hardware, Hailo, sustained-operation, and target-device performance measurements remain outstanding. |

Chapter Three defined further engineering targets, including at least 10 frames per second, a capture-to-database cycle of no more than 500 milliseconds, at least 95% successful DHT22 readings, CPU utilisation below 70%, RAM use below 4 GB, local API responses within 200 milliseconds, and alert delivery within 60 seconds when network access is available. Chapter Four reports that these targets have not yet been established on the physical Raspberry Pi. The 17.398 millisecond ONNX pipeline time recorded for one desktop image demonstrates desktop compatibility; Raspberry Pi and Hailo performance remains unmeasured.

## 5.2 Conclusions

The study demonstrates that a tomato disease classification workflow can be organised as a local edge application that joins image results with environmental readings and preserves them for review. The implemented prototype provides the core software path from image input to classification, database storage, API access, and dashboard presentation. Simulation made it possible to exercise this path on a development computer without the physical camera or sensor.

The MobileNetV2 model met the stated accuracy and macro F1-score targets on the held-out PlantVillage test set. This supports the use of transfer learning with a compact image-classification architecture for the selected five disease classes under the dataset's controlled conditions. The result establishes a baseline for further evaluation. Field generalisation, detection before visible symptoms, and reductions in crop loss remain unmeasured.

The environmental sensor association adds temperature and humidity context to each stored classification. The study confirms that the software can record these values with a detection, but it does not establish a statistical relationship between environmental conditions and disease occurrence. Such a conclusion requires reliable physical readings collected over time alongside verified disease labels.

The API, dashboard, monitoring controls, database, and report exports provide the functional basis for local monitoring. Their software behaviour was tested. Formal user evaluation and access from a second device on a physical local network remain unmeasured, so usability among farmers has not yet been established.

Overall, the work produced a tested software prototype and a strong controlled-dataset model baseline. Completion of the intended Raspberry Pi AI HAT+ deployment remains conditional on physical testing of the camera and DHT22, ONNX benchmarking on the Pi, and Hailo compilation and runtime integration. The evidence currently supports describing the project as an edge-oriented prototype; physical hardware and field validation are still pending.

## 5.3 Recommendations

Based on the implementation and evaluation, the following actions are recommended:

1. **Complete staged hardware integration.** First verify the Pi Camera Module 3 and DHT22 independently using the hardware diagnostic procedure. Compare the DHT22 with reference instruments and record successful readings, failed reads, retries, and measurement differences.

2. **Benchmark the complete workflow on the Raspberry Pi.** Run the ONNX model on the Pi CPU after the camera and sensor are stable. Record inference and capture-to-database latency, throughput, CPU use, RAM use, device temperature, and behaviour during sustained monitoring. Report the test conditions and compare measured values with the targets in Chapter Three.

3. **Complete and verify Hailo deployment.** Record the installed AI HAT+ accelerator variant and compatible software versions before compiling the ONNX model to HEF. Compare class outputs and confidence behaviour on the same test inputs across desktop ONNX, Raspberry Pi CPU, and Hailo inference.

4. **Validate the model with representative tomato images.** Collect and label images under varied lighting, backgrounds, leaf positions, growth stages, and symptom conditions. Use a separate field or greenhouse test set to measure generalisation. Preserve the PlantVillage result as a controlled baseline and report field results separately.

5. **Keep predictions within a human-reviewed decision process.** Present uncertain cases for inspection and make clear that the result supports a decision. The configured disease severity represents alert priority; lesion area and biological disease stage require separate validated measurements. Review confidence calibration before using the threshold to guide operational alerts.

6. **Complete alert and data-management functions if they remain in scope.** Add notification delivery, cooldown rules, an alert log, and tests for successful delivery and failure recovery. Define retention and backup procedures for stored records and images.

7. **Evaluate the dashboard with intended users and prepare it for deployment.** Ask farmers or agricultural extension workers to assess whether the labels, confidence, history, and environmental readings support their workflow. Before access beyond a controlled trusted network, add authentication, HTTPS, service supervision, and a documented recovery process.

## 5.4 Contribution to Knowledge

This study contributes an implemented and testable design for combining tomato leaf image classification with environmental monitoring on a local edge-oriented system. Its contributions are specific to the prototype and evidence produced in this work:

1. **An integrated monitoring workflow.** The system connects image acquisition, five-class disease inference, temperature and humidity readings, transactional local storage, API access, and dashboard presentation in one software pipeline. Each classification record retains the model output and its associated sensor measurement for later review.

2. **A reproducible five-class model workflow.** Dataset validation, duplicate detection, seeded split manifests, MobileNetV2 transfer learning, held-out evaluation, and ONNX export provide a repeatable path from PlantVillage images to a deployable model. The reported metrics and confusion matrix establish a controlled baseline for later comparisons.

3. **A model compatibility and integrity contract.** The ONNX metadata records the disease class order, input dimensions, normalisation values, tensor names, model version, and file hash. Runtime checks use this information to reject a model whose file or inference contract does not match the application configuration.

4. **A simulation path for development and verification.** Interchangeable image, sensor, and inference components let the application exercise the same storage, API, and dashboard path on a desktop computer. This supports software integration testing before physical hardware is available.

5. **Documented boundaries between model evidence and deployment evidence.** The study reports controlled test-set results and software test outcomes while identifying physical sensor, Raspberry Pi, Hailo, field-generalisation, and alert-delivery evidence that remains to be collected. This provides a clear baseline and test plan for subsequent work.

The contribution is an applied system design and reproducible prototype evaluation using established machine-learning and IoT components. The results provide a basis for further field data collection and hardware validation.

## 5.5 Future Work

Future development can extend the prototype in several connected directions. The first is physical deployment: verify the Raspberry Pi camera and DHT22, benchmark ONNX inference on the Pi CPU, and then complete Hailo model compilation and runtime integration. The planned performance targets should be measured under repeatable conditions, including warm-up, sustained operation, and full capture-to-storage cycles.

A second direction is broader model validation. A field-collected tomato image set, reviewed by knowledgeable annotators, would help measure the effect of natural backgrounds, lighting, overlapping leaves, and mixed symptoms. The class scope could be extended deliberately to include healthy leaves and an appropriate unknown or out-of-scope handling strategy. The image pipeline could also be extended from whole-image classification to leaf or lesion localisation, while keeping any severity estimate tied to a validated measurement method.

A third direction is to implement the Kaizen feedback process described in the project framework. With suitable human review, uncertain and misclassified cases could be labelled, organised into versioned datasets, and considered for scheduled retraining. Each updated model should be evaluated against a fixed held-out set and a separate field set before deployment; it should not update itself from unverified predictions.

Further work can examine whether repeated, verified disease detections are associated with temperature and humidity patterns over time. Longer monitoring periods and additional reference measurements would be needed before drawing conclusions about disease risk. Additional sensors, such as leaf-wetness or soil-moisture sensors, could be evaluated if they address a defined research question and can be integrated without making the system impractical for its intended users.

Finally, future versions may add alert delivery with delivery logs and offline queuing, WebSocket updates if polling proves insufficient, multi-device monitoring, configurable data retention, and stronger deployment security. These extensions should be prioritized through user feedback and measured system needs.
