import math
from typing import Tuple

# Earth radius in kilometers
EARTH_RADIUS_KM = 6371.0


def haversine_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calculate the great-circle distance between two GPS coordinates
    using the Haversine formula.

    Returns:
        Distance in kilometers (float)
    """

    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(
        math.radians, [lat1, lon1, lat2, lon2]
    )

    # Differences
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(lat1) * math.cos(lat2) *
        math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_KM * c


def is_within_radius(
    source: Tuple[float, float],
    target: Tuple[float, float],
    radius_km: float
) -> bool:
    """
    Check if target location is within given radius (km)
    from source location.
    """

    distance = haversine_distance(
        source[0], source[1],
        target[0], target[1]
    )

    return distance <= radius_km
