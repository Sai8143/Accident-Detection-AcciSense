import cv2
import numpy as np
from ultralytics import YOLO

# YOLO for vehicle detection
model = YOLO("yolov8n.pt")
VEHICLE_CLASSES = [2, 3, 5, 7]  # car, bike, bus, truck

# Background subtractor (CCTV static camera)
bg_subtractor = cv2.createBackgroundSubtractorMOG2(
    history=200, varThreshold=32, detectShadows=False
)

# Rolling history
motion_history = []
collision_history = []

MAX_HISTORY = 8
MIN_WARMUP_FRAMES = 15


def detect_video_accident(frame) -> bool:
    """
    CCTV-based accident detection.
    Designed for static traffic cameras.
    """

    frame = cv2.resize(frame, (640, 480))

    # 1️⃣ Background subtraction
    fg_mask = bg_subtractor.apply(frame)

    # Remove noise
    fg_mask = cv2.medianBlur(fg_mask, 5)

    fg_pixels = cv2.countNonZero(fg_mask)
    fg_ratio = fg_pixels / fg_mask.size

    # 2️⃣ Vehicle detection
    results = model(frame, conf=0.4, classes=VEHICLE_CLASSES)

    boxes = []
    for r in results:
        for box in r.boxes:
            boxes.append(tuple(map(int, box.xyxy[0])))

    if len(boxes) < 2:
        motion_history.clear()
        collision_history.clear()
        return False

    # 3️⃣ Collision proximity
    collision = False
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if _iou(boxes[i], boxes[j]) > 0.10:
                collision = True
                break

    motion_history.append(fg_ratio)
    collision_history.append(collision)

    if len(motion_history) > MAX_HISTORY:
        motion_history.pop(0)
        collision_history.pop(0)

    # Wait until background stabilizes
    if len(motion_history) < MIN_WARMUP_FRAMES:
        return False

    # 4️⃣ Chaos detection (lower threshold)
    chaos_detected = max(motion_history) > 0.05

    # 5️⃣ Temporal correlation
    collision_frames = sum(collision_history)
    motion_frames = sum(1 for m in motion_history if m > 0.05)

    return (
        chaos_detected and
        collision_frames >= 2 and
        motion_frames >= 2
    )


def _iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    inter = max(0, xB - xA) * max(0, yB - yA)
    if inter == 0:
        return 0.0

    areaA = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    areaB = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    return inter / (areaA + areaB - inter)
