# Rice Leaf Disease Detection

## About this project
This is my final year project in Data Science.
I plan to compare YOLOv8 and YOLO11 for rice leaf disease detection.

## Project aim
The aim is to detect rice leaf diseases in pictures and show
the predicted disease names with bounding boxes.

## Disease classes
- Bacterial leaf blight
- Brown spot
- Leaf smut

These are the labels supplied by the dataset. Their biological correctness still needs review.

## Current progress
- Selected the project topic.
- Found and downloaded a public labelled dataset.
- Checked 6,715 images and their label files on 16 October 2026.
- Generated local examples showing the supplied boxes.
- Found incorrect folder paths and exact duplicate images across data splits.
- Formal YOLO training has not started.

See [the dataset check](reports/DATASET_CHECK.md) for the actual findings and [the code explanation](docs/CODE_WALKTHROUGH.md) for a simple walkthrough.

## Dataset source
The downloaded archive came from [Kaggle](https://www.kaggle.com/datasets/hiramscud/rice-disease-detection-dataset-of-6000-images).
Its metadata identifies [DreamyDaisy rice version 4 on Roboflow](https://universe.roboflow.com/dreamydaisy-cdagn/rice-dyl9n/dataset/4) and states CC BY 4.0.
Images and dataset archives are not redistributed here. Check the source licence and give attribution when using the data.

## Run the inspection
Use a Python environment with Pillow installed:

```text
python -m pip install -r requirements.txt
python inspect_dataset.py "path/to/archive (1).zip" --output reports
```

The original archive is not changed. The script writes a JSON report and a preview picture locally. It does not train YOLO.

## Planned work
1. Review the class mapping and empty labels.
2. Correct paths in a prepared copy and create a split that keeps duplicate and related images together.
3. Train YOLOv8 and YOLO11 using the same agreed data split.
4. Compare their detection results and speed.
5. Build a simple image upload page.

## Student
Ma Yingkai
