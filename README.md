# charmd

CLI to start a PyCharm debug session and then run a Python target in the same interpreter process, so instrumentation remains active and mostly invisible to the target.

## Installation
```bash
pip install charmd
```

## Quick start
```bash
charmd -- --version
charmd -- -m mypkg.mymod arg1
charmd -- script.py arg1 arg2
charmd -- -c "print('hello')"
```

## Options (debugger)
- `--host` (default: `localhost`)
- `--port` (default: `5678`)
- `--suspend`
- `--[no-]stdout-to-server` (default: on)
- `--[no-]stderr-to-server` (default: on)

## Repository
https://github.com/TekWizely/charmd
