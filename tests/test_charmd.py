"""Minimal test for charmd package."""

import subprocess
import sys

from src.charmd import __version__


def test_version():
    """Test that __version__ is set."""
    assert __version__ is not None
    assert isinstance(__version__, str)


def test_version_flag():
    """Test that --version flag prints version and exits."""
    # Run charmd with --version flag
    result = subprocess.run(
        [sys.executable, "-m", "charmd", "--version"],
        capture_output=True,
        text=True,
    )

    # Should exit with code 0
    assert result.returncode == 0

    # Should print "charmd <version>" to stdout
    output = result.stdout.strip()
    assert output == f"charmd {__version__}"

    # Should not print to stderr
    assert result.stderr == ""
