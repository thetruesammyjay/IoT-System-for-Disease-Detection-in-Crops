# Five-Class Tomato MobileNetV2 Training

This workflow prepares and evaluates a whole-image classifier for the following PlantVillage tomato classes, in this fixed output order:

| Index | Project label | PlantVillage directory |
|---:|---|---|
| 0 | Bacterial Spot | `Tomato___Bacterial_spot` |
| 1 | Early Blight | `Tomato___Early_blight` |
| 2 | Late Blight | `Tomato___Late_blight` |
| 3 | Leaf Mould | `Tomato___Leaf_Mold` |
| 4 | Septoria Leaf Spot | `Tomato___Septoria_leaf_spot` |

The initial model does not include a healthy class. A low-confidence runtime result is recorded as uncertain instead of healthy.

## 1. Install Training Dependencies

Use Python 3.11 and synchronize the optional training dependency group:

```powershell
uv sync --extra training
```

Training can run on a CPU, but a CUDA-capable GPU is strongly preferred. The first use of pretrained MobileNetV2 may download official ImageNet weights. Use `--no-pretrained` only when those weights cannot be obtained.

## 2. Obtain and Arrange PlantVillage

Download or otherwise obtain the PlantVillage dataset through a source you are permitted to use. The dataset itself is not committed to this repository. The preparation script searches below the supplied root for the five exact class-directory names listed above, so both of these layouts are accepted:

```text
PlantVillage/
  Tomato___Bacterial_spot/
  ...
```

```text
PlantVillage/
  color/
    Tomato___Bacterial_spot/
    ...
```

## 3. Validate Images and Create Splits

Run the preparation module from the repository root:

```powershell
uv run python -m models.training.dataset_prep `
  --dataset-root "C:\path\to\PlantVillage" `
  --output-dir data/processed/tomato_5class `
  --seed 42
```

The script verifies readable image files, rejects images smaller than 32 x 32 pixels, removes exact within-class duplicates, and stops if identical image content appears under different labels. Images are sorted and shuffled independently per class using the recorded seed. Each class is then divided into approximately 80% training, 10% validation, and 10% test data, with at least one image in every split.

The preparation output contains:

- `train.csv`, used for parameter learning and augmentation.
- `validation.csv`, used for checkpoint selection and early stopping.
- `test.csv`, used once for final evaluation.
- `metadata.json`, containing the source root, seed, ratios, class order, split counts, invalid images, and removed duplicates.
- `class_to_index.json`, preserving the output-index contract used during deployment.

The manifests reference source images without copying them. Do not move the source dataset after preparing the manifests. Re-run preparation if its location changes.

## 4. Train MobileNetV2

```powershell
uv run python -m models.training.train `
  --data-dir data/processed/tomato_5class `
  --output-dir models/training/runs/baseline `
  --epochs 30 `
  --batch-size 32 `
  --seed 42
```

The default workflow uses ImageNet-pretrained MobileNetV2 weights, replaces the final layer with five outputs, freezes the feature extractor for the first three epochs, and then fine-tunes the complete network at a reduced learning rate. Training uses random resized crops, horizontal flips, and moderate colour jitter. Validation uses deterministic resize, centre crop, and ImageNet normalization.

Class-balanced cross-entropy reduces the influence of unequal class sizes. The best checkpoint is selected by validation macro F1-score, with validation loss used as a tie-breaker. Early stopping occurs after seven epochs without improvement. The test manifest is never opened by the training script.

Training artifacts include:

- `best_model.pt`, the best validation checkpoint.
- `history.csv`, machine-readable epoch measurements.
- `history.json`, the same history with full numeric precision.

On Windows, the default `--workers 0` is the safest setting. A larger value may improve data loading after the baseline run is stable.

## 5. Evaluate the Held-Out Test Set

```powershell
uv run python -m models.training.evaluate `
  --checkpoint models/training/runs/baseline/best_model.pt `
  --data-dir data/processed/tomato_5class `
  --output-dir models/evaluation/baseline
```

Evaluation generates:

- `metrics.json`, containing accuracy, macro precision, macro recall, macro F1-score, per-class precision, per-class recall, per-class F1-score, and support.
- `predictions.csv`, containing every test image, actual class, predicted class, confidence, correctness, and all five probabilities.
- `confusion_matrix.csv`, containing the numerical 5 x 5 matrix.
- `confusion_matrix.png`, containing the labelled matrix for the results chapter.

The confusion-matrix rows are actual classes and its columns are predicted classes. Preserve the generated files with the checkpoint, source dataset version, split metadata, seed, and software commit used for the experiment.

## 6. Export the Best Checkpoint to ONNX

After evaluation confirms that the checkpoint is suitable for deployment, export it:

```powershell
uv run python -m models.training.export_onnx `
  --checkpoint models/training/runs/baseline/best_model.pt `
  --output models/onnx/tomato_mobilenet_v2.onnx
```

The exporter validates the ONNX graph and compares its logits with the original PyTorch model using the same input. Export stops if the outputs differ beyond a small numerical tolerance. It then writes `tomato_mobilenet_v2.metadata.json` beside the model. The metadata preserves the five-class order, input dimensions, normalization values, tensor names, model version, ONNX opset, source-checkpoint hash, and ONNX-file hash.

Classify a local image through ONNX Runtime:

```powershell
uv run python main.py --classify --backend onnx --image "C:\path\to\tomato-leaf.jpg"
```

The runtime verifies the model hash and metadata contract before inference. It refuses to start if the model was modified, if its classes are reordered, or if its preprocessing requirements differ from the application configuration.

## 7. Reproducibility Record

For each reported run, retain the following information:

- Dataset source and version.
- `metadata.json` and all three manifests.
- Git commit identifier.
- Python, PyTorch, Torchvision, CUDA, and GPU versions.
- Seed, batch size, epoch limit, learning rates, and augmentation settings.
- Best checkpoint epoch and validation measurements.
- Final test metrics and confusion matrix.

Do not report metrics from the deterministic software simulator as model results. Only measurements generated from the held-out PlantVillage test manifest and the trained checkpoint belong in the experimental findings.
