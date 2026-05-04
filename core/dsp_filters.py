import cv2
import numpy as np

class DSPFilters:

    @staticmethod
    def apply(frame, filter_name):

        if filter_name == "None":
            return frame

        # ================= BASIC =================

        if filter_name == "Grayscale":
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        if filter_name == "RGB View":
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

        if filter_name == "Binary Threshold":
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, th = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
            return cv2.cvtColor(th, cv2.COLOR_GRAY2BGR)

        if filter_name == "Inversion":
            return cv2.bitwise_not(frame)

        # ================= RESIZE =================

        if filter_name == "Resize Half":
            return cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

        # ================= CROP =================

        if filter_name == "Crop Center":
            h, w = frame.shape[:2]
            crop = frame[h//4:3*h//4, w//4:3*w//4]
            return cv2.resize(crop, (w, h))

        # ================= ROTATE =================

        if filter_name == "Rotate 90":
            rotated = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            return cv2.resize(rotated, (frame.shape[1], frame.shape[0]))

        # ================= FLIP =================

        if filter_name == "Flip Horizontal":
            return cv2.flip(frame, 1)

        if filter_name == "Flip Vertical":
            return cv2.flip(frame, 0)

        if filter_name == "Flip Both":
            return cv2.flip(frame, -1)

        # ================= CHANNELS =================

        if filter_name == "Split Channels":
            b, g, r = cv2.split(frame)
            zeros = np.zeros_like(b)

            blue = cv2.merge([b, zeros, zeros])
            green = cv2.merge([zeros, g, zeros])
            red = cv2.merge([zeros, zeros, r])

            top = np.hstack([blue, green])
            bottom = np.hstack([red, frame])

            combined = np.vstack([top, bottom])
            return cv2.resize(combined, (frame.shape[1], frame.shape[0]))

        # ================= HSV =================

        if filter_name == "HSV":
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        if filter_name == "Hue":
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            h, _, _ = cv2.split(hsv)
            return cv2.cvtColor(h, cv2.COLOR_GRAY2BGR)

        if filter_name == "Saturation":
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            _, s, _ = cv2.split(hsv)
            return cv2.cvtColor(s, cv2.COLOR_GRAY2BGR)

        if filter_name == "Value":
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            _, _, v = cv2.split(hsv)
            return cv2.cvtColor(v, cv2.COLOR_GRAY2BGR)

        # ================= SIMPLE FILTERS =================

        if filter_name == "Gaussian Blur":
            return cv2.GaussianBlur(frame, (7, 7), 0)

        if filter_name == "Median Filter":
            return cv2.medianBlur(frame, 5)

        # ================= BRIGHTNESS =================

        if filter_name == "Brightness":
            return cv2.convertScaleAbs(frame, alpha=1.0, beta=40)

        if filter_name == "Contrast":
            return cv2.convertScaleAbs(frame, alpha=1.4, beta=0)

        return frame


# ================= FILTER LIST =================

FILTERS = [
    "None",
    "Grayscale",
    "RGB View",
    "Binary Threshold",
    "Inversion",
    "Resize Half",
    "Crop Center",
    "Rotate 90",
    "Flip Horizontal",
    "Flip Vertical",
    "Flip Both",
    "Split Channels",
    "HSV",
    "Hue",
    "Saturation",
    "Value",
    "Gaussian Blur",
    "Median Filter",
    "Brightness",
    "Contrast"
]