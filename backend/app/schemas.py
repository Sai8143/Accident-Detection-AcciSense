from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AccidentResponse(BaseModel):
    message: str
    latitude: float
    longitude: float
    timestamp: datetime

    image_saved_as: Optional[str] = None
    accident_type: Optional[str] = None   # photo / video
    status: Optional[str] = None           # potential / confirmed


class HealthResponse(BaseModel):
    health: str
