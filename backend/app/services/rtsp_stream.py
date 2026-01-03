import cv2
import time
from app.services.video_detector import detect_video_accident
from app.services.notifier import notify_emergency


def process_rtsp_stream(rtsp_url: str, latitude: float, longitude: float):
    """
    Continuously processes RTSP CCTV stream.
    Triggers alert only on confirmed accident.
    """

    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print("❌ RTSP stream not accessible")
        return

    print("✅ RTSP stream connected")

    frame_count = 0
    skip_frames = 3   # process every 3rd frame (performance)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Frame read failed, retrying...")
            time.sleep(1)
            continue

        frame_count += 1

        if frame_count % skip_frames != 0:
            continue

        accident = detect_video_accident(frame)

        if accident:
            print("🚨 ACCIDENT DETECTED FROM RTSP")
            notify_emergency(latitude, longitude)
            break

    cap.release()

def process_camera_stream(source, latitude, longitude):
    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print("❌ Camera not accessible")
        return

    print("✅ Camera connected")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        accident = detect_video_accident(frame)

        if accident:
            print("🚨 ACCIDENT DETECTED FROM CAMERA")
            notify_emergency(latitude, longitude)
            break

    cap.release()
