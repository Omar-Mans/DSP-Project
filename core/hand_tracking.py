"""Hand tracking module using MediaPipe Tasks API."""

import cv2
import time
import os

try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
except Exception as exc:
    raise ImportError(
        "MediaPipe Tasks could not be initialized. Install mediapipe>=0.10.30. "
        f"Original error: {exc}"
    )

# Standard Hand Landmark Connections for drawing
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),          # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),          # Index finger
    (5, 9), (9, 10), (10, 11), (11, 12),     # Middle finger
    (9, 13), (13, 14), (14, 15), (15, 16),   # Ring finger
    (13, 17), (17, 18), (18, 19), (19, 20),  # Pinky
    (0, 17)                                  # Palm
]

class HandTracker:
    """Detects hands and returns landmark coordinates in pixels."""

    def __init__(self, max_hands=1, detection_conf=0.70, tracking_conf=0.70):
        # The hand_landmarker.task model is required. 
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'hand_landmarker.task')
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}. Download from mediapipe models page.")
            
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_conf,
            min_hand_presence_confidence=tracking_conf,
            min_tracking_confidence=tracking_conf,
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.timestamp_ms = 0

    def process(self, frame_bgr, draw=True):
        """Return hand landmarks and optionally draw the hand skeleton."""
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        
        # Ensure monotonic timestamp for VIDEO running mode
        current_time_ms = int(time.time() * 1000)
        if current_time_ms <= self.timestamp_ms:
            current_time_ms = self.timestamp_ms + 1
        self.timestamp_ms = current_time_ms
        
        results = self.detector.detect_for_video(mp_image, self.timestamp_ms)
        h, w = frame_bgr.shape[:2]
        hands_data = []

        if results.hand_landmarks:
            for hand_lms in results.hand_landmarks:
                points = []
                # First convert to pixel coordinates
                for idx, lm in enumerate(hand_lms):
                    points.append({
                        "id": idx,
                        "x": int(lm.x * w),
                        "y": int(lm.y * h),
                        "z": lm.z,
                    })
                hands_data.append(points)
                
                if draw:
                    # Draw connections
                    for connection in HAND_CONNECTIONS:
                        start_idx = connection[0]
                        end_idx = connection[1]
                        
                        start_point = (points[start_idx]["x"], points[start_idx]["y"])
                        end_point = (points[end_idx]["x"], points[end_idx]["y"])
                        
                        cv2.line(frame_bgr, start_point, end_point, (0, 255, 0), 2)
                        
                    # Draw landmarks
                    for point in points:
                        cv2.circle(frame_bgr, (point["x"], point["y"]), 5, (0, 0, 255), -1)
                        
        return frame_bgr, hands_data
