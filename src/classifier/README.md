# Classifier: Healthy or Unhealthy Detection Model

This directory contains the code and resources for the classification model used to predict the health status of individuals ("Healthy" or "Unhealthy") based on thermal imaging data and associated health metrics.

---

## Features

- **Hybrid Classification Model**:
  - **CNN Module**: Extracts spatial features from thermal images.
  - **Dense Network**: Processes handcrafted statistical features.
  - Combines these streams to create a unified feature representation for classification.

- **Data Handling**:
  - Reads preprocessed datasets from the pipeline.
  - Supports thermal images and tabular health metrics.

- **Training and Evaluation**:
  - Implements data augmentation, early stopping, and model checkpointing.
  - Outputs accuracy and classification metrics.

---

## Requirements

The required Python libraries are listed in `requirements.txt`. Install them with:

```
pip install -r requirements.txt
```

---

## Model Details

- **CNN Module**:
  - Input: 128x128 grayscale thermal images.
  - Layers: Convolutional, MaxPooling, Dropout.
  - Output: Feature vector representing spatial patterns.

- **Dense Network**:
  - Input: Statistical features (e.g., temperature metrics, variance).
  - Layers: Fully connected dense layers.
  - Output: Combined representation for classification.

---

## Results

The model achieves robust performance metrics, integrating deep learning with handcrafted features for better generalization across datasets.

---

## Future Improvements

- Integrate additional data sources for better model generalization.
- Experiment with other architectures like Transformers or ResNet.
- Optimize hyperparameters using advanced search techniques.

---
