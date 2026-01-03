import cv2
import numpy as np
from ultralytics import YOLO

# YOLO model for vehicle localization
model = YOLO("yolov8n.pt")

# Vehicle classes (COCO)
VEHICLE_CLASSES = [2, 3, 5, 7]  # car, motorcycle, bus, truck


def detect_crash(image_path: str) -> bool:
    """
    CCTV-based crash classifier (photo).

    Logic:
    - Detect vehicles using YOLO
    - Analyze ONLY vehicle regions
    - Look for damage patterns

    Returns:
        True  -> Potential crash
        False -> Normal traffic
    """

    frame = cv2.imread(image_path)
    if frame is None:
        return False

    frame = cv2.resize(frame, (640, 480))

    # Step 1️⃣ Detect vehicles
    results = model(frame, conf=0.5, classes=VEHICLE_CLASSES)

    vehicle_boxes = []
    for r in results:
        for box in r.boxes:
            vehicle_boxes.append(tuple(map(int, box.xyxy[0])))

    if not vehicle_boxes:
        return False

    # Step 2️⃣ Damage analysis inside vehicles
    for (x1, y1, x2, y2) in vehicle_boxes:
        roi = frame[y1:y2, x1:x2]
        if roi.size == 0:
            continue

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
