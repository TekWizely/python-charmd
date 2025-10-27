"""Minimal test for charmd package."""

import pytest

from src.charmd import __version__, main


def test_version():
    """Test that __version__ is set."""
    assert __version__ is not None
    assert isinstance(__version__, str)


def test_version_flag(capsys):
    """Test that --version flag prints version and exits."""
    # Run charmd with --version flag - should exit with code 0
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])

    # Should exit with code 0
    assert exc_info.value.code == 0

    # Capture output
    captured = capsys.readouterr()

    # Should print "charmd <version>" to stdout
    output = captured.out.strip()
    assert output == f"charmd {__version__}"

    # Should not print to stderr
    assert captured.err == ""
