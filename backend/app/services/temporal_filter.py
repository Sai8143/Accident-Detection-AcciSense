from collections import deque

WINDOW_SIZE = 5
THRESHOLD = 0.65

photo_scores = deque(maxlen=WINDOW_SIZE)


def temporal_vote(score: float) -> bool:
    """
    Returns True if accident is consistently detected
    """
    photo_scores.append(score)

    if len(photo_scores) < WINDOW_SIZE:
        return False

    positives = sum(1 for s in photo_scores if s >= THRESHOLD)
    return positives >= 3
