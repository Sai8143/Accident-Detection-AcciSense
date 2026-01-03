from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from datetime import datetime
import os
import cv2
import numpy as np

from app.database import SessionLocal, engine
from app.models import Accident, Base
from app.schemas import AccidentResponse, HealthResponse

from app.services.photo_detector import detect_photo_accident_score
from app.services.video_detector import detect_video_accident
from app.services.temporal_filter import temporal_vote
from app.services.decision_engine import AccidentDecision, decide
from app.services.notifier import notify_emergency, log_no_accident
from app.services.rtsp_stream import process_rtsp_stream
import threading
from app.services.rtsp_stream import process_camera_stream
import threading


# -------------------------
# Database Initialization
# -------------------------
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CCTV Accident Detection API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -------------------------
# Root
# -------------------------
@app.get("/")
def root():
    return {"status": "Backend running"}

# -------------------------
# Health
# -------------------------
@app.get("/health", response_model=HealthResponse)
def health():
    return {"health": "OK"}

# -------------------------
# PHOTO-BASED (POTENTIAL)
# -------------------------
@app.post("/alert", response_model=AccidentResponse)
async def receive_alert(
    image: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...)
):
    filename = f"{uuid4()}.jpg"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(await image.read())

    # Photo confidence score
    score = detect_photo_accident_score(filepath)

    # Temporal voting (reduces false positives)
    is_potential = temporal_vote(score)

    if not is_potential:
        log_no_accident(latitude, longitude)
        return {
            "message": "No accident detected",
            "image_saved_as": filename,
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": datetime.utcnow()
        }

    # ⚠️ Potential accident only
    return {
        "message": "⚠️ Potential accident detected – awaiting CCTV video confirmation",
        "image_saved_as": filename,
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": datetime.utcnow()
    }

# -------------------------
# VIDEO-BASED (CONFIRMED)
# -------------------------
@app.post("/video-frame")
async def video_frame(
    frame: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...)
):
    img = cv2.imdecode(
        np.frombuffer(await frame.read(), np.uint8),
        cv2.IMREAD_COLOR
    )

    if img is None:
        return {"message": "Invalid frame"}

    video_result = detect_video_accident(img)
    decision = decide(False, video_result)

    if decision == AccidentDecision.ACCIDENT_CONFIRMED:
        # Store confirmed accident
        db = SessionLocal()
        accident = Accident(
            latitude=latitude,
            longitude=longitude,
            image_path="video_frame"
        )
        db.add(accident)
        db.commit()
        db.close()

        notify_emergency(latitude, longitude)

        return {
            "message": "🚨 Accident confirmed via CCTV video",
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": datetime.utcnow()
        }

    log_no_accident(latitude, longitude)
    return {"message": "No accident detected"}

@app.post("/start-rtsp")
def start_rtsp_monitoring(
    rtsp_url: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...)
):
    thread = threading.Thread(
        target=process_rtsp_stream,
        args=(rtsp_url, latitude, longitude),
        daemon=True
    )
    thread.start()

    return {
        "message": "RTSP CCTV monitoring started",
        "rtsp_url": rtsp_url
    }

@app.post("/start-camera")
def start_camera(
    camera_index: int = Form(0),
    latitude: float = Form(...),
    longitude: float = Form(...)
):
    thread = threading.Thread(
        target=process_camera_stream,
        args=(camera_index, latitude, longitude),
        daemon=True
    )
    thread.start()

    return {"message": "Camera monitoring started"}