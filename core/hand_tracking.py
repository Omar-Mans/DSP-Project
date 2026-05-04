"""Hand tracking module using MediaPipe Hands."""

import cv2

try:
    import mediapipe as mp
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
except Exception as exc:
    raise ImportError(
        "MediaPipe Hands could not be initialized. Install mediapipe==0.10.14. "
        f"Original error: {exc}"
    )


class HandTracker:
    """Detects one hand and returns landmark coordinates in pixels."""

    def __init__(self, max_hands=1, detection_conf=0.70, tracking_conf=0.70):
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_conf,
            min_tracking_confidence=tracking_conf,
        )
        self.mp_hands = mp_hands
        self.mp_draw = mp_draw

    def process(self, frame_bgr, draw=True):
        """Return hand landmarks and optionally draw the hand skeleton."""
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        h, w = frame_bgr.shape[:2]
        hands_data = []

        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:
                points = []
                for idx, lm in enumerate(hand_lms.landmark):
                    points.append({
                        "id": idx,
                        "x": int(lm.x * w),
                        "y": int(lm.y * h),
                        "z": lm.z,
                    })
                hands_data.append(points)
                if draw:
                    self.mp_draw.draw_landmarks(
                        frame_bgr,
                        hand_lms,
                        self.mp_hands.HAND_CONNECTIONS,
                    )
        return frame_bgr, hands_data
