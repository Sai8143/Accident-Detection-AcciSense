from enum import Enum


class AccidentDecision(str, Enum):
    NO_ACCIDENT = "NO_ACCIDENT"
    POTENTIAL_ACCIDENT = "POTENTIAL_ACCIDENT"
    ACCIDENT_CONFIRMED = "ACCIDENT_CONFIRMED"


def decide(photo_result: bool, video_result: bool) -> AccidentDecision:
    """
    Decide accident status based on detection inputs.

    Priority:
    1. Video-based confirmation (highest)
    2. Photo-based potential detection
    3. No accident
    """

    if video_result:
        return AccidentDecision.ACCIDENT_CONFIRMED

    if photo_result:
        return AccidentDecision.POTENTIAL_ACCIDENT

    return AccidentDecision.NO_ACCIDENT
