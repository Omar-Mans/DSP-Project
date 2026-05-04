# DSP Project

A clean VS Code project for **Digital Signal Processing + Computer Vision** with only 3 working modes:

1. **Filters**
2. **Move Mouse**
3. **Volume Control**


---

## Main Features

- Real-time webcam preview.
- Hand tracking using MediaPipe.
- DSP image/video filters from the course sections.
- Mouse movement using hand gestures.
- Volume control using thumb-index distance.
- Stable Windows setup using pinned package versions.

---

## Model Requirement

This project requires the `hand_landmarker.task` file from MediaPipe Tasks. You must place this file in the project's root folder. You can download it directly from Google:
[Download hand_landmarker.task](https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task)

---

## How to Run from VS Code

1. Extract the zip file.
2. Open VS Code.
3. Choose **File > Open Folder**.
4. Select the folder named:

```text
DSP_Project
```

5. Open the VS Code terminal:

```text
Terminal > New Terminal
```

6. Install dependencies once:

```powershell
python -m pip install -r requirements.txt
```

If you had dependency conflicts before, run this first:

```powershell
python -m pip uninstall -y numpy opencv-python opencv-contrib-python mediapipe jax jaxlib
python -m pip install -r requirements.txt
```

7. Run the project:

```powershell
python main.py
```

Or open `main.py` and press the Run button in VS Code.

---

## Modes

### 1. Filters

Includes the relevant DSP / image-processing operations from the course:

- Grayscale
- BGR to RGB View
- Binary Threshold
- Inversion
- Inversion using 255 - image
- Resize Half
- Resize Scale 600x400
- Resize Stretch Nearest
- Crop Center ROI
- Rotate 90 Clockwise
- Flip Horizontal
- Flip Vertical
- Flip Both
- Split BGR Channels
- Merge BGR Channels
- HSV View
- Hue Channel
- Saturation Channel
- Value Channel
- Gaussian Blur
- Median Filter
- Bilateral Smooth
- Sharpen
- Canny Edges
- Sobel Edges
- Laplacian Edges
- Brightness Enhance
- Contrast Enhance
- Brightness + Contrast
- Salt Pepper Noise
- Gaussian Noise
- Speckle Noise
- Denoise Median
- Pillow BLUR
- Pillow CONTOUR
- Pillow DETAIL
- Pillow EDGE_ENHANCE
- Pillow EMBOSS
- Pillow SHARPEN
- Pillow SMOOTH
- Pillow Color Enhance

### 2. Move Mouse

- Raise only the index finger to move the cursor.
- Bring index and middle fingers close together to click.
- Cursor movement is smoothed and bounded to avoid screen corners.

### 3. Volume Control

- Move thumb and index finger apart to increase volume.
- Bring them close together to decrease volume.
- Uses `pycaw` if available.
- If `pycaw` fails, it uses Windows media keys as a fallback.

---

## DSP Concepts Used

- Video as a digital signal.
- Frame-by-frame video processing.
- Image represented as a NumPy array.
- Color space conversion.
- Thresholding.
- Image transformations: resize, crop, rotate, flip.
- Channel splitting and merging.
- HSV analysis.
- Image inversion.
- Noise simulation: salt-and-pepper, Gaussian, speckle.
- Noise reduction using median filtering.
- Filtering and enhancement.
- Feature extraction from hand landmarks.
- Mapping extracted features to system control.

---

## Troubleshooting

### Camera not opening
Try camera index 1 or 2 from the left sidebar.

### MediaPipe import issues
Use the pinned versions in `requirements.txt`.

### NumPy / OpenCV errors
Run:

```powershell
python -m pip uninstall -y numpy opencv-python opencv-contrib-python mediapipe jax jaxlib
python -m pip install -r requirements.txt
```

### Mouse moves too fast
Keep your hand inside the camera frame and use only the index finger in Move Mouse mode.

### Volume does not change exactly
This depends on the available Windows audio backend. The app tries `pycaw` first, then falls back to Windows media keys.
