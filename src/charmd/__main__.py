"""
charmd: Start a PyCharm debug session and then run a user-specified Python target
in the same process, similar to how pdb delegates to the target.

Usage examples:
  - Using explicit separator (recommended):
      python -m charmd --host 127.0.0.1 --port 5678 -- -m mypkg.mymod arg1 arg2
      python -m charmd -- --version
      python -m charmd -- script.py arg1 arg2
  - Without '--' (best-effort split at end of known options):
      python -m charmd --host 127.0.0.1 --port 5678 -m mypkg.mymod arg1

Notes:
- The follow-on invocation runs inside this same Python interpreter so that the
  debug instrumentation remains active and mostly invisible to the target.
- Supported follow-on forms mirror common Python invocations:
  * -m <module> [args]
  * -c <code> [args]
  * <script_path> [args]
- Interpreter-level flags (e.g., -O, -X) are not supported in-process.
"""

from __future__ import annotations

import argparse
import os
import runpy
import sys
from typing import Any, List, Optional, Tuple

from . import __version__


def _port_str_to_int(s: str) -> int:
    """Converts a port string to an integer, ignoring commas and surrounding whitespace."""
    return int(s.replace(",", "").strip())


def _load_config() -> dict[str, Any]:
    """
    Reads configuration from `charmd.conf` in the current working directory.
    Values are parsed into appropriate types.
    """
    config_path = os.path.join(os.getcwd(), "charmd.conf")
    if not os.path.exists(config_path):
        return {}

    config = {}
    with open(config_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                # Split into key and raw value; strip key but preserve value for further handling
                key_part, value_part = line.split("=", 1)
                key = key_part.strip()

                # For detection of quoted values, strip outer whitespace only for checking.
                # If the trimmed value is quoted with matching single/double quotes, extract
                # the inner content and preserve any whitespace inside the quotes.
                value_trimmed = value_part.strip()
                if (
                    len(value_trimmed) >= 2
                    and value_trimmed[0] == value_trimmed[-1]
                    and value_trimmed[0] in ("'", '"')
                ):
                    value = value_trimmed[1:-1]
                else:
                    # Unquoted values: strip leading/trailing whitespace as before
                    value = value_part.strip()

                # Coerce to intended types
                if key == "port":
                    try:
                        config[key] = _port_str_to_int(value)
                    except ValueError:
                        pass  # Ignore malformed port
                elif key in ("suspend", "stdout_to_server", "stderr_to_server"):
                    config[key] = value.lower() in ("true", "1", "yes", "y", "on")
                elif key in ("host", "pydevd_path"):
                    config[key] = value
    return config


def _parse_args(argv: List[str]) -> Tuple[argparse.Namespace, List[str]]:
    parser = argparse.ArgumentParser(
        prog="charmd",
        description=(
            "Start PyCharm debugger via pydevd_pycharm.settrace then run a Python "
            "target in the same process. Use '--' to separate debugger options "
            "from the follow-on Python target."
        ),
        add_help=True,
        allow_abbrev=False,
    )

    # Version flag
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    # Debugger connection options (MVP)
    parser.add_argument(
        "--host",
        default="localhost",  # 127.0.0.1
        help="PyCharm debug server host (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=_port_str_to_int,
        default=5678,
        help="PyCharm debug server port (default: 5678)",
    )
    parser.add_argument(
        "--suspend",
        action="store_true",
        default=False,
        help="Suspend on start (default: False)",
    )
    # stdout/stderr redirection to debug console
    parser.add_argument(
        "--stdout-to-server",
        dest="stdout_to_server",
        action="store_true",
        help="Redirect stdout to debug server (default: True)",
    )
    parser.add_argument(
        "--no-stdout-to-server",
        dest="stdout_to_server",
        action="store_false",
        help="Do not redirect stdout to debug server",
    )
    parser.add_argument(
        "--stderr-to-server",
        dest="stderr_to_server",
        action="store_true",
        help="Redirect stderr to debug server (default: True)",
    )
    parser.add_argument(
        "--no-stderr-to-server",
        dest="stderr_to_server",
        action="store_false",
        help="Do not redirect stderr to debug server",
    )
    parser.add_argument(
        "--pydevd-path",
        default=None,
        help="Path to the pydevd-pycharm module directory.",
    )
    # Conf-init action
    parser.add_argument(
        "--conf-init",
        action="store_true",
        help="Create a charmd.conf file with current settings and exit.",
    )

    # Set hardcoded defaults for paired flags
    parser.set_defaults(stdout_to_server=True, stderr_to_server=True)

    # Layering of settings:
    # 1. Hardcoded defaults (in add_argument or set_defaults)
    # 2. Project-specific config file
    # 3. Command-line arguments
    parser.set_defaults(**_load_config())

    # Parse known args, leave the rest as follow-on target and its args
    # This allows using either '--' or end-of-known-args behavior.
    opts, remainder = parser.parse_known_args(argv)

    # If the user provided an explicit '--', argparse will leave it in remainder;
    # strip a leading '--' if present.
    if remainder and remainder[0] == "--":
        remainder = remainder[1:]

    return opts, remainder


def _create_config_file(opts: argparse.Namespace) -> int:
    """
    Creates a charmd.conf file with the current settings.
    If the file already exists, it reports it and exits.
    """
    config_path = os.path.join(os.getcwd(), "charmd.conf")
    if os.path.exists(config_path):
        print(f"Configuration file already exists at: {config_path}", file=sys.stderr)
        return 1

    try:
        with open(config_path, "w") as f:
            f.write("# charmd configuration file\n")
            f.write("# Lines starting with '#' are comments.\n")
            f.write("#\n")
            f.write(f"host = {opts.host}\n")
            f.write(f"port = {opts.port}\n")
            f.write(f"suspend = {str(opts.suspend).lower()}\n")
            f.write(f"stdout_to_server = {str(opts.stdout_to_server).lower()}\n")
            f.write(f"stderr_to_server = {str(opts.stderr_to_server).lower()}\n")
            if opts.pydevd_path:
                f.write(f"pydevd_path = {opts.pydevd_path}\n")
            else:
                f.write("#pydevd_path = <path to pydevd_pycharm module>\n")
        print(f"Configuration file created at: {config_path}")
        return 0
    except IOError as e:
        print(f"Error creating configuration file: {e}", file=sys.stderr)
        return 1


def _start_debugger(opts: argparse.Namespace) -> bool:
    if opts.pydevd_path:
        sys.path.append(opts.pydevd_path)

    try:
        import pydevd_pycharm  # type: ignore
    except ImportError as e:
        print(
            "charmd error: pydevd_pycharm is not installed or importable.\n"
            "Install the PyCharm debug package (e.g., 'pip install pydevd-pycharm~=<PyCharm version>')\n"
            "or specify its location with --pydevd-path.",
            file=sys.stderr,
        )
        raise SystemExit(2) from e

    try:
        # Connect to the PyCharm debug server
        pydevd_pycharm.settrace(
            host=opts.host,
            port=opts.port,
            stdout_to_server=opts.stdout_to_server,
            stderr_to_server=opts.stderr_to_server,
            suspend=opts.suspend,
        )
        return True
    except Exception as e:  # Connection refused, timeouts, etc.
        print(
            f"charmd error: failed to connect to debug server at {opts.host}:{opts.port}: {e}",
            file=sys.stderr,
        )
        # Typical failure when port is in use or server not listening
        raise SystemExit(111) from e  # 111 commonly used for connection refused


def _run_follow_on(args: List[str]) -> int:

    sys.path.append(os.path.abspath(os.getcwd()))

    # Emulate common python CLI forms: -m, -c, or script path
    if args[0] == "-m":
        if len(args) < 2:
            print("charmd error: '-m' requires a module name", file=sys.stderr)
            return 2
        module = args[1]
        # Set sys.argv as if running `python -m module ...`
        old_argv = sys.argv
        sys.argv = [module] + args[2:]
        try:
            runpy.run_module(module, run_name="__main__", alter_sys=True)
            return 0
        except SystemExit as se:
            code = se.code if isinstance(se.code, int) else 1
            return code
        finally:
            sys.argv = old_argv

    if args[0] == "-c":
        if len(args) < 2:
            print("charmd error: '-c' requires a code string", file=sys.stderr)
            return 2
        code = args[1]
        # For `python -c code [arg1 ...]`, sys.argv[0] is '-c'
        old_argv = sys.argv
        sys.argv = ["-c"] + args[2:]
        try:
            glb = {"__name__": "__main__", "__file__": None}
            exec(code, glb, None)
            return 0
        except SystemExit as se:
            code = se.code if isinstance(se.code, int) else 1
            return code
        finally:
            sys.argv = old_argv

    # Otherwise treat first arg as a script path
    script = args[0]
    if not os.path.exists(script):
        print(f"charmd error: script not found: {script}", file=sys.stderr)
        return 2

    # Set sys.argv as if running `python script.py ...`
    old_argv = sys.argv
    sys.argv = [script] + args[1:]
    try:
        runpy.run_path(script, run_name="__main__")
        return 0
    except SystemExit as se:
        code = se.code if isinstance(se.code, int) else 1
        return code
    finally:
        sys.argv = old_argv


def _stop_debugger():
    """Safely stops the debugger if it was started."""
    if "pydevd_pycharm" in sys.modules:
        pydevd_pycharm = sys.modules["pydevd_pycharm"]
        pydevd_pycharm.stoptrace()


def main(argv: Optional[List[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    opts, follow_on = _parse_args(argv)

    if opts.conf_init:
        return _create_config_file(opts)

    # Bail early if no follow-on configured
    if not follow_on:
        print(
            "charmd error: no follow-on target provided.\n"
            "Examples:\n"
            "  charmd -- -m mypkg.mymod arg1\n"
            "  charmd -- script.py arg1 arg2\n"
            "  charmd -- -c \"print('hello')\"",
            file=sys.stderr,
        )
        return 2

    debug_started = False
    try:
        # Initialize debugger connection first
        debug_started = _start_debugger(opts)

        # Delegate to the follow-on target in this same interpreter
        return _run_follow_on(follow_on)
    finally:
        if debug_started:
            _stop_debugger()
            debug_started = False


if __name__ == "__main__":
    raise SystemExit(main())
