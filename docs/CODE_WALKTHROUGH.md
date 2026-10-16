# Understanding the dataset check

## What the program does

The program reads the ZIP, matches each picture with its label, checks the numbers and draws sample boxes. It does not train a model.

1. `argparse` reads the ZIP path and output folder from your command.
2. `ZipFile` opens the archive without extracting or changing it.
3. The program lists pictures and labels. A picture and its label should have the same filename before the extension.
4. It reads each label row. The first number is the class ID. The next four numbers describe the centre, width and height of a box.
5. It checks that the class ID is allowed and the coordinates are valid. This can catch broken numbers, but it cannot prove that a disease name is correct.
6. `Pillow` opens each picture. The program compares decoded pixel content to find exact duplicates. It also checks filename prefixes for possible related exports.
7. `ImageDraw` draws the saved boxes on nine examples. These boxes come from the labels, not a trained model.
8. It writes a JSON report and one preview image in the output folder.

## How box coordinates work

For an image 587 pixels wide, a normalised centre x value of 0.5 means the box is centred at 293.5 pixels from the left. A width of 0.2 means the box is 117.4 pixels wide. The script converts these numbers into left, top, right and bottom positions for drawing.

Do not use filename words to predict the disease. During training, YOLO learns from image content and the supplied labels. During prediction, the model receives a picture and produces its own boxes and class scores.

## Why repeated pictures matter

Training pictures are used to learn. Validation pictures help choose model settings. Test pictures are used for the final agreed evaluation. If exactly the same picture is in training and testing, the test can be easier than detecting a new picture. Our check found this problem, so the split needs repair before formal comparison.

An empty label can be valid when there is no target in a picture. It can also mean someone missed a target. We need to inspect the picture before deciding.

## What I can say in a supervisor meeting

I checked the dataset structure and generated some pictures with their labelled boxes. The images and labels match by filename, but the folder names and YAML paths need correction. I also found identical pictures in different data splits. My next step is to review the labels and prepare a fair split before training YOLOv8 and YOLO11.

## Practise with the code

- Find where `NAMES` defines the three class IDs.
- Explain why `leaf001.jpg` should match `leaf001.txt`.
- Read one label row and explain its five values.
- Open the local preview and distinguish a supplied box from a predicted box.
- Explain why a valid coordinate does not prove a correct disease label.

## Recording progress with Git

The repository stores the code and short reports. It does not store the dataset or Python environment. A commit is a saved set of file changes with a short description. Read each change before committing it, and use a message that describes the actual work, such as `Add dataset inspection script`.
