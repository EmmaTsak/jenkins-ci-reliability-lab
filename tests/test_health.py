from app.health import get_health


def test_health_status():
    result = get_health()

    assert result["status"] == "healthy"


def test_version():
    result = get_health()

    assert result["version"] == "0.1.0"