"""Tests for Dynaconf settings configuration."""

from settings.settings import settings


def test_settings_load():
    """Ensure configuration loads correctly."""
    # Check that essential settings exist
    essential_settings = [
        "project_name",
        "data_dir",
        "models_dir",
        "parties_tracked",
        "timeout_seconds",
        "log_level",
    ]

    for setting in essential_settings:
        assert hasattr(settings, setting), f"Missing setting: {setting}"
        assert settings.get(setting) is not None, f"Setting {setting} is None"


def test_environment_is_valid():
    """Test that environment setting is valid."""
    env = settings.get("environment", "development")
    assert env in [
        "development",
        "staging",
        "production",
    ], f"Invalid environment: {env}"


def test_parties_tracked_is_list():
    """Test that parties_tracked is a list."""
    parties = settings.get("parties_tracked", [])
    assert isinstance(parties, list)
    assert len(parties) > 0
    # Check for expected parties
    expected_parties = ["Reform UK", "Labour", "Conservative", "Green Party"]
    for party in expected_parties:
        assert party in parties


def test_log_level_is_valid():
    """Test that log level is valid."""
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    log_level = settings.get("log_level", "INFO").upper()
    assert log_level in valid_levels


def test_timeout_is_positive():
    """Test that timeout is a positive number."""
    timeout = settings.get("timeout_seconds", 30)
    assert isinstance(timeout, (int, float))
    assert timeout > 0
