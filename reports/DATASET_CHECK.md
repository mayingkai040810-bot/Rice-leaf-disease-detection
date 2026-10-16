# Dataset check on 16 October 2026

This is a preparation check, not a model training result. The original ZIP was read without changing its files.

## Source actually inspected

- Archive filename: `archive (1).zip`.
- Download source supplied by the student: [Kaggle dataset](https://www.kaggle.com/datasets/hiramscud/rice-disease-detection-dataset-of-6000-images).
- The archive YAML identifies [DreamyDaisy rice version 4](https://universe.roboflow.com/dreamydaisy-cdagn/rice-dyl9n/dataset/4), with CC BY 4.0 stated in its metadata.
- This differs from the previously discussed version 3. Do not copy version 3 split counts into the dissertation.
- No image files or dataset archive are included in this repository.

## Actual counts

| Split | Images | Matching labels | Boxes | Empty labels |
|---|---:|---:|---:|---:|
| Training | 5,372 | 5,372 | 19,304 | 49 |
| Validation | 671 | 671 | 2,482 | 10 |
| Test | 672 | 672 | 2,411 | 8 |
| Total | 6,715 | 6,715 | 24,197 | 67 |

All images decoded successfully at 587 by 587 pixels. Every image had exactly one matching label by filename. All non-empty label rows had five fields, valid class IDs, finite normalised coordinates and positive box dimensions. No checked box crossed an image edge by more than 0.001 in normalised coordinates. These are format checks, not proof of correct disease labels or precise boxes.

The YAML class order is:

0. Bacteria_Leaf_Blight
1. Brown_Spot
2. Leaf_smut

## Problems that need attention

1. **The folder layout does not match YOLO's normal pairing.** Pictures are in `images/train`, `images/val`, `images/test`. Labels are in `labels/train2`, `labels/val2`, `labels/test2`. All 6,715 expected standard label paths are therefore absent, even though filenames match. In a prepared copy, use `labels/train`, `labels/val`, `labels/test`.
2. **YAML paths are wrong for the archive layout.** It contains `../train/images`, `../valid/images`, `../test/images`. A prepared copy with the current image layout needs `images/train`, `images/val`, `images/test`, plus an appropriate dataset root.
3. **Exact duplicate leakage exists.** There are 1,103 groups of repeated decoded pixel content within the full dataset. Of these, 383 groups contain images from more than one split. This proves that the supplied splits are not independent at the exact-image level. A group is not an image count.
4. **Related exports may also leak.** There are 531 filename-prefix groups spanning splits. A prefix before `.rf.` is a clue about a shared source image, not proof of a unique plant. Related exports should be reviewed and grouped before a new split is agreed. Different filenames can still contain related images.
5. **There are 67 empty labels.** They may be intended background images or missed annotations. Review them before deciding to retain or exclude them; do not automatically assign a disease label.
6. **Some names raise a class question.** Some files named `Blast_...` carry class 2, `Leaf_smut`. Names are not ground truth, and this check cannot establish the biological diagnosis. Verify the source mapping and ask for disease expertise before changing any labels.

## Sample box review

Nine labelled previews were generated, three per supplied class. They are local inspection examples, not model predictions. In these examples the annotation scope varies: class 0 includes large leaf regions, class 1 includes small spots, and class 2 includes local discoloured patches. This is a visual observation from a small sample, not a complete annotation-quality assessment.

The preview file and detailed JSON are kept locally in `reports/`. They are ignored by Git to avoid republishing dataset images or large generated files.

## Decision and next steps

Do not use the supplied split as the final formal evaluation split. Before training, agree the class mapping, review empty labels, group duplicates and related exports, create a separate prepared copy, and write corrected YAML paths. Record the new split in a manifest so YOLOv8 and YOLO11 use exactly the same data.

No model has been trained during this check. No files were removed, moved or relabelled in the original archive. Near-duplicate detection beyond shared filename prefixes, annotation consistency across exact copies, and expert disease verification remain outstanding.

## Repeat the check

Install Pillow, then run:

```text
python inspect_dataset.py "path/to/archive (1).zip" --output reports
```

The script is designed for this archive's three-class mapping. Adapt and verify that mapping before using it on another dataset. Only process trusted archives of a manageable size; the script reads decoded image content into memory.
