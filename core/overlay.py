"""Drawing helpers for clean visual feedback."""

import cv2


def draw_hud(frame, mode, status, fps, volume=None, filter_name=None):
    """Draw a compact HUD on top of the video frame."""
    h, w = frame.shape[:2]
    cv2.rectangle(frame, (10, 10), (430, 120), (10, 10, 10), -1)
    cv2.rectangle(frame, (10, 10), (430, 120), (70, 170, 255), 2)
    cv2.putText(frame, f"Mode: {mode}", (25, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (80, 220, 255), 2)
    cv2.putText(frame, f"Status: {status}", (25, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (230, 230, 230), 2)
    cv2.putText(frame, f"FPS: {fps:.1f}", (25, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (120, 255, 120), 2)
    if filter_name:
        cv2.putText(frame, f"DSP: {filter_name}", (w - 310, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 220, 120), 2)
    if volume is not None:
        x1, y1, x2, y2 = w - 80, 130, w - 45, 420
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
        fill_y = int(y2 - (y2 - y1) * (volume / 100))
        cv2.rectangle(frame, (x1, fill_y), (x2, y2), (70, 220, 255), -1)
        cv2.putText(frame, f"{volume}%", (w - 105, y2 + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (70, 220, 255), 2)
    return frame
