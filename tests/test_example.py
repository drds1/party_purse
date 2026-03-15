# tests/test_settings.py
from settings import settings

def test_settings_load():
    """Ensure configuration loads correctly."""
    # Default values exist
    assert hasattr(settings, "PROJECT_NAME")
    assert hasattr(settings, "DATA_DIR")
    assert hasattr(settings, "MODELS_DIR")

    # Environment is one of the known environments
    assert settings.get("ENVIRONMENT", "development") in ["development", "staging", "production"]