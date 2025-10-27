# charmd

A PyCharm debug session helper that starts a debug server and then runs your Python target in the same process.

---

### TOC
* [Requirements](#requirements)
* [Quick Start](#quick-start)
* [Installation](#installation)
* [Installing pydevd-pycharm](#installing-pydevd-pycharm)
sdf
---

### Requirements

- Python 3.8 or higher
- [pydevd-pycharm](https://pypi.org/project/pydevd-pycharm/) package (see [installing pydevd-pycharm](#installing-pydevd-pycharm) below)

**Note:** `charmd` does not automatically install `pydevd-pycharm` as a dependency. This is intentional, as PyCharm installations ship with their own preferred version of the library that should be used for debugging.

## Quick start

_usage_
```text
charmd [debug-options ...] [--] (-m module | -c command | pyfile) [args ...]
```

**Note:** `charmd` is good at distinguishing debug options from the target specification.  In cases where they may be ambiguity, you can use `--` to clearly specify the start of the target specification.

_examples_
```text
charmd -m mypkg.mymod arg1
charmd -c "print('hello')"
charmd -- script.py arg1 arg2
```

_debug options_
```text
  -h, --help             Show this help message and exit
  --version              Show program's version number and exit
 
  --host HOST            PyCharm debug server host (default: localhost)
  --port PORT            PyCharm debug server port (default: 5678)
  --suspend              Suspend on start (default: False)

  --stdout-to-server     Redirect stdout to debug server (default: True)
  --no-stdout-to-server  Do not redirect stdout to debug server

  --stderr-to-server     Redirect stderr to debug server (default: True)
  --no-stderr-to-server  Do not redirect stderr to debug server
 
  --pydevd-path PATH     Path to the pydevd-pycharm module directory.

  --conf-init            Create a charmd.conf file with current settings and exit.
 ```

## Installation

### From PyPI (Recommended)

Install the latest stable version from [PyPI](https://pypi.org/project/charmd/) using pip:

```bash
pip install charmd
```

To install for the current user only:

```bash
pip install --user charmd
```

To upgrade an existing installation:

```bash
pip install --upgrade charmd
```

### From Wheel File

Wheel (`.whl`) files are available as release assets on the [GitHub releases page](https://github.com/tekwizely/pycharm_debug/releases). Download the desired version and install it directly:

```bash
pip install charmd-*.whl
```

Replace `*` with the specific version number, or use the exact filename.

### From Source (Clone Repository)

#### Standard Installation

Clone the repository and install using pip:

```bash
git clone https://github.com/tekwizely/pycharm_debug.git
cd pycharm_debug
pip install .
```

#### Editable/Development Installation

For development work, install in editable mode so changes take effect immediately:

```bash
git clone https://github.com/tekwizely/pycharm_debug.git
cd pycharm_debug
pip install -e .
```

This allows you to modify the source code and test changes without reinstalling.

#### Running Without Installation

You can also run `charmd` directly from the cloned repository without installing:

```bash
git clone https://github.com/tekwizely/pycharm_debug.git
cd pycharm_debug
python charmd.py [options]
# or
python -m charmd [options]
```

### Verifying Installation

After installation, verify that `charmd` is properly installed:

```bash
charmd --version
```

Or:

```bash
python -m charmd --version
```

### Uninstalling

To remove `charmd`:

```bash
pip uninstall charmd
```

## Installing pydevd-pycharm

You have two options for installing the `pydevd-pycharm` package:

### Option 1: Use the egg file from PyCharm installation

You can use the `pydevd-pycharm.egg` file directly from your PyCharm installation directory:

**Linux/Windows:**
```
<PyCharm directory>/debug-egg/pydevd-pycharm.egg
```

**MacOS:**
```
<PyCharm directory>/Contents/debug-eggs/pydevd-pycharm.egg
```

For example, on MacOS:
```
/Applications/PyCharm.app/Contents/debug-eggs/pydevd-pycharm.egg
```

### Option 2: Install using pip

Install the `pydevd-pycharm` package matching your PyCharm version:

```bash
pip install pydevd-pycharm~=<version of PyCharm on the local machine>
```

For example, if your PyCharm version is 242.20224.428:

```bash
pip install pydevd-pycharm~=242.20224.428
```

To find your PyCharm version, go to **PyCharm** → **About PyCharm** (or **Help** → **About** on some platforms).


You can configure `charmd` to use this path via the `pydevd_path` setting in your configuration file or the `--pydevd-path` command-line option.

For more information, see the [JetBrains Remote Debugging documentation](https://www.jetbrains.com/help/pycharm/remote-debugging-with-product.html#remote-debug-config).

----------
## License

The `tekwizely/python-charmd` project is released under the [MIT](https://opensource.org/licenses/MIT) License.  See `LICENSE` file.
