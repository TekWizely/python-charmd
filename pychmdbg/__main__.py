"""
pychmdbg: Start a PyCharm debug session and then run a user-specified Python target
in the same process, similar to how pdb delegates to the target.

Usage examples:
  - Using explicit separator (recommended):
      python -m pychmdbg --host 127.0.0.1 --port 5678 -- -m mypkg.mymod arg1 arg2
      python -m pychmdbg -- --version
      python -m pychmdbg -- script.py arg1 arg2
  - Without '--' (best-effort split at end of known options):
      python -m pychmdbg --host 127.0.0.1 --port 5678 -m mypkg.mymod arg1

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
from typing import List, Tuple, Optional


def _parse_args(argv: List[str]) -> Tuple[argparse.Namespace, List[str]]:
    parser = argparse.ArgumentParser(
        prog="pychmdbg",
        description=(
            "Start PyCharm debugger via pydevd_pycharm.settrace then run a Python "
            "target in the same process. Use '--' to separate debugger options "
            "from the follow-on Python target."
        ),
        add_help=True,
        allow_abbrev=False,
    )

    # Debugger connection options (MVP)
    parser.add_argument(
        "--host",
        default="localhost", # 127.0.0.1
        help="PyCharm debug server host (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5678,
        help="PyCharm debug server port (default: 5678)",
    )
    parser.add_argument(
        "--suspend",
        action="store_true",
        help="Suspend on start (default: False)",
    )
    # stdout/stderr redirection to debug console
    parser.add_argument(
        "--stdout-to-server",
        dest="stdout_to_server",
        action="store_true",
        default=True,
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
        default=True,
        help="Redirect stderr to debug server (default: True)",
    )
    parser.add_argument(
        "--no-stderr-to-server",
        dest="stderr_to_server",
        action="store_false",
        help="Do not redirect stderr to debug server",
    )

    # Parse known args, leave the rest as follow-on target and its args
    # This allows using either '--' or end-of-known-args behavior.
    opts, remainder = parser.parse_known_args(argv)

    # If the user provided an explicit '--', argparse will leave it in remainder;
    # strip a leading '--' if present.
    if remainder and remainder[0] == "--":
        remainder = remainder[1:]

    return opts, remainder


def _start_debugger(opts: argparse.Namespace) -> None:
    try:
        import pydevd_pycharm  # type: ignore
    except ImportError as e:
        print(
            "pychmdbg error: pydevd_pycharm is not installed or importable.\n"
            "Install the PyCharm debug package (e.g., 'pip install pydevd-pycharm')\n"
            "and try again.",
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
    except Exception as e:  # Connection refused, timeouts, etc.
        print(
            f"pychmdbg error: failed to connect to debug server at {opts.host}:{opts.port}: {e}",
            file=sys.stderr,
        )
        # Typical failure when port is in use or server not listening
        raise SystemExit(111) from e  # 111 commonly used for connection refused


def _run_follow_on(args: List[str]) -> int:
    if not args:
        print(
            "pychmdbg error: no follow-on target provided.\n"
            "Examples:\n"
            "  pychmdbg -- -m mypkg.mymod arg1\n"
            "  pychmdbg -- script.py arg1 arg2\n"
            "  pychmdbg -- -c \"print('hello')\"",
            file=sys.stderr,
        )
        return 2

    # Emulate common python CLI forms: -m, -c, or script path
    if args[0] == "-m":
        if len(args) < 2:
            print("pychmdbg error: '-m' requires a module name", file=sys.stderr)
            return 2
        module = args[1]
        follow_argv = [module] + args[2:]
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
            print("pychmdbg error: '-c' requires a code string", file=sys.stderr)
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
        print(f"pychmdbg error: script not found: {script}", file=sys.stderr)
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


def main(argv: Optional[List[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    opts, follow_on = _parse_args(argv)

    # Initialize debugger connection first
    _start_debugger(opts)

    # Delegate to the follow-on target in this same interpreter
    return _run_follow_on(follow_on)


if __name__ == "__main__":
    raise SystemExit(main())
