import socket
from datetime import datetime, timezone

VERSION = "0.1.0"


def get_health():
    return {
        "version": VERSION,
        "hostname": socket.gethostname(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "healthy",
    }


if __name__ == "__main__":
    health = get_health()

    for key, value in health.items():
        print(f"{key}: {value}")