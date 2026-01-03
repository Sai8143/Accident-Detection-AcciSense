from sqlalchemy import Column, String, Float, DateTime
from app.database import Base
from datetime import datetime
import uuid

class Accident(Base):
    __tablename__ = "accidents"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    image_path = Column(String, nullable=True)   # photo or "video_frame"

    accident_type = Column(
        String,
        nullable=False,
        default="unknown"   # photo / video
    )

    status = Column(
        String,
        nullable=False,
        default="potential"  # potential / confirmed
    )

    timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
