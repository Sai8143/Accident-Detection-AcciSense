import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
VEHICLE_CLASSES = [2, 3, 5, 7]


def detect_photo_accident_score(image_path: str) -> float:
    """
    Returns accident likelihood score (0.0 – 1.0)
    """

    frame = cv2.imread(image_path)
    if frame is None:
        return 0.0

    frame = cv2.resize(frame, (640, 480))
    results = model(frame, conf=0.5, classes=VEHICLE_CLASSES)

    scores = []

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
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

            texture_variance = np.var(gray)

            score = 0.0

            if edge_density > 0.18:
                score += 0.4
            if texture_variance > 800:
                score += 0.4
            if len(contours) >= 4:
                score += 0.2

            scores.append(min(score, 1.0))

    return max(scores) if scores else 0.0
