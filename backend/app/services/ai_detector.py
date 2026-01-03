import cv2
import numpy as np
from ultralytics import YOLO

# Load YOLOv8 lightweight model
model = YOLO("yolov8n.pt")

# COCO vehicle classes
VEHICLE_CLASSES = [2, 3, 5, 7]  # car, motorcycle, bus, truck


def iou(boxA, boxB):
    """Compute Intersection over Union (IoU)"""
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


def vehicle_damage_score(roi):
    """
    Lightweight damage scoring inside vehicle ROI
    """
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(blur, 120, 240)
    edge_density = np.count_nonzero(edges) / edges.size

    contours, _ = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    large_contours = [
        c for c in contours if cv2.contourArea(c) > 0.02 * roi.size
    ]

    texture_variance = np.var(gray)

    if (
        edge_density > 0.20 and
        len(large_contours) >= 3 and
        texture_variance > 800
    ):
        return True

    return False


def detect_potential_accident(image_path: str) -> bool:
    """
    CCTV-based potential accident detector.

    Conditions:
    - Vehicle overlap (collision-like)
    - Damage detected on at least one involved vehicle

    Returns:
        True  -> Potential accident
        False -> Normal traffic
    """

    frame = cv2.imread(image_path)
    if frame is None:
        return False

    frame = cv2.resize(frame, (640, 480))

    # Step 1️⃣ Detect vehicles
    results = model(frame, conf=0.5, classes=VEHICLE_CLASSES)

    boxes = []
    for r in results:
        for box in r.boxes:
            boxes.append(tuple(map(int, box.xyxy[0])))

    if len(boxes) < 2:
        return False

    # Step 2️⃣ Check overlapping vehicles
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if iou(boxes[i], boxes[j]) > 0.15:

                # Step 3️⃣ Check damage on involved vehicles
                for (x1, y1, x2, y2) in [boxes[i], boxes[j]]:
                    roi = frame[y1:y2, x1:x2]
                    if roi.size == 0:
                        continue

                    if vehicle_damage_score(roi):
                        return True

    return False
