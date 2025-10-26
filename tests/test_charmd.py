"""Minimal test for charmd package."""

from src.charmd import __version__


def test_version():
    """Test that __version__ is set."""
    assert __version__ is not None
    assert isinstance(__version__, str)
