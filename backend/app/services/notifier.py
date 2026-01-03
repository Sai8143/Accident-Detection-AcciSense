# from datetime import datetime

# def notify_services(latitude: float, longitude: float) -> None:
#     """
#     Notify emergency services about confirmed accident.
#     Currently logs notifications.
#     Can be extended to SMS, Email, Push notifications.
#     """

#     timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

#     print("\n================ EMERGENCY ALERT ================")
#     print("🚨 ACCIDENT CONFIRMED")
#     print(f"🕒 Time (UTC): {timestamp}")
#     print(f"📍 Location: Latitude {latitude}, Longitude {longitude}")
#     print("🏥 Hospital Services: NOTIFIED")
#     print("🚓 Police Department: NOTIFIED")
#     print("🚑 Ambulance Services: NOTIFIED")
#     print("=================================================\n")

from datetime import datetime

def notify_emergency(latitude: float, longitude: float) -> None:
    """
    Trigger emergency notifications.
    Used ONLY when accident is CONFIRMED.
    """

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    print("\n================ EMERGENCY ALERT ================")
    print("🚨 ACCIDENT CONFIRMED")
    print(f"🕒 Time (UTC): {timestamp}")
    print(f"📍 Location: Latitude {latitude}, Longitude {longitude}")
    print("🏥 Hospital Services: NOTIFIED")
    print("🚓 Police Department: NOTIFIED")
    print("🚑 Ambulance Services: NOTIFIED")
    print("=================================================\n")


def log_no_accident(latitude: float, longitude: float) -> None:
    """
    Silent logging for normal conditions.
    Used when NO accident is detected.
    """

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    print(
        f"[INFO] {timestamp} | No accident detected "
        f"at ({latitude}, {longitude})"
    )
