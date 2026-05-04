"""Gesture feature extraction from hand landmarks."""

import math


def dist(a, b):
    """Euclidean distance between two landmark dicts."""
    return math.hypot(a["x"] - b["x"], a["y"] - b["y"])


def fingers_up(points):
    """Return [thumb, index, middle, ring, pinky], where 1 means up."""
    if len(points) < 21:
        return [0, 0, 0, 0, 0]

    fingers = []
    # Thumb logic depends on mirrored view; this is enough for UI feedback.
    fingers.append(1 if points[4]["x"] > points[3]["x"] else 0)

    for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        fingers.append(1 if points[tip]["y"] < points[pip]["y"] else 0)
    return fingers


def pinch_distance(points):
    """Distance between thumb tip and index tip."""
    if len(points) < 21:
        return 0
    return dist(points[4], points[8])


def normalized_pinch(points):
    """Pinch normalized by palm size, useful for volume mapping."""
    if len(points) < 21:
        return 0.0
    palm = max(dist(points[0], points[9]), 1.0)
    return pinch_distance(points) / palm


def is_mouse_move_gesture(points):
    """Index up and middle down means move cursor."""
    f = fingers_up(points)
    return f[1] == 1 and f[2] == 0


def is_click_gesture(points, threshold=42):
    """Index and middle fingertips close together means click."""
    if len(points) < 21:
        return False
    f = fingers_up(points)
    return f[1] == 1 and f[2] == 1 and dist(points[8], points[12]) < threshold
