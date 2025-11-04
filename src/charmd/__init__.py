"""charmd package

Provides a CLI to start a PyCharm debug session and then run a Python target
within the same interpreter process so the instrumentation is transparent.

You can invoke via:
  - python -m charmd -- [python-args]
  - charmd -- [python-args]  (after installing the package)

See charmd.__main__ for details.
"""

from __future__ import annotations

__all__ = ["main", "__version__"]
__version__ = "0.2.5"

# Re-export main for console_scripts entry-point convenience
from .__main__ import main  # noqa: F401
