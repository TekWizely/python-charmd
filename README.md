# charmd

A command-line utility that streamlines your PyCharm debugging workflow by allowing you to launch and debug Python scripts directly from the terminal, eliminating the need for manual Run Configurations.

## Why charmd?

PyCharm's debugger is powerful, but debugging scripts with different arguments or configurations typically means editing Run Configurations through the IDE. This becomes cumbersome when:
- You need to debug one-off commands with unique CLI arguments
- You're testing different script variations or parameter combinations
- You want the simplicity of command-line debugging (like `pdb` or `debugpy`) with PyCharm's full IDE debugging experience

`charmd` eliminates this friction by letting you debug any Python command directly from the terminal.

---

## TOC
* [Requirements](#requirements)
* [Quick Start](#quick-start)
* [Locating or Installing pydevd-pycharm](#locating-or-installing-pydevd-pycharm)
  * [Use the library from your PyCharm installation](#option-1-use-the-library-from-your-pycharm-installation)
  * [Install using pip](#option-2-install-using-pip)
* [Configuration File](#configuration-file)
  * [File Location](#file-location)
  * [Creating the Configuration File](#creating-the-configuration-file)
    * [Automatic Generation](#option-1-automatic-generation)
    * [Manual Creation](#option-2-manual-creation)
  * [Configuration Options](#configuration-options)
  * [File Format](#file-format)
  * [Configuration Precedence](#configuration-precedence)
  * [Example Workflow](#example-workflow)
* [Installation](#installation)
  * [From PyPI (Recommended)](#from-pypi-recommended)
  * [From Wheel File](#from-wheel-file)
  * [From Source (Clone Repository)](#from-source-clone-repository)
  * [Verifying Installation](#verifying-installation)
  * [Uninstalling](#uninstalling)
* [Troubleshooting](#troubleshooting)

---

## Requirements

- Python 3.8 or higher
- [pydevd-pycharm](https://pypi.org/project/pydevd-pycharm/) package (see [Locating or Installing pydevd-pycharm](#locating-or-installing-pydevd-pycharm) below)

**Note:** `charmd` does not automatically install `pydevd-pycharm` as a dependency. This is intentional, as PyCharm installations ship with their own preferred version of the library that should be used for debugging. See [Locating or Installing pydevd-pycharm](#locating-or-installing-pydevd-pycharm) below.

## Quick start

**⚠️ Important:** Before running any `charmd` command, ensure that:
 - PyCharm's Python Debug Server is running and listening on the configured host and port (default: localhost:5678)
 - You set breakpoints in your code where you want to pause execution

See [PyCharm's Debug Documentation](https://www.jetbrains.com/help/pycharm/debugging-code.html) for more information.

_usage_
```text
charmd [debug-options ...] [--] (-m module | -c command | pyfile) [args ...]
```

**Note:** `charmd` is good at distinguishing debug options from the target specification.  In cases where they may be ambiguity, you can use `--` to clearly specify the start of the target specification.

_examples_
```bash
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

## Locating or Installing pydevd-pycharm

`charmd` requires the `pydevd-pycharm` library to communicate with PyCharm's debug server. You can either locate an existing installation (if PyCharm is installed) or install a compatible version via pip.

### Option 1: Use the library from your PyCharm installation

If you have PyCharm installed, you can point `charmd` to the bundled `pydevd-pycharm.egg` file in your PyCharm installation directory:

**Linux/Windows:**
```
<PyCharm directory>/debug-egg/pydevd-pycharm.egg
```

**MacOS:**
```
<PyCharm directory>/Contents/debug-eggs/pydevd-pycharm.egg
```

_alternative_:
```
<PyCharm directory>/Contents/plugins/python-ce/helpers/pydev
```

For example, on MacOS:
```
/Applications/PyCharm.app/Contents/debug-eggs/pydevd-pycharm.egg
```

Configure `charmd` to use this path via the `pydevd_path` setting in your [configuration file](#configuration-file) or the `--pydevd-path` command-line option.

### Option 2: Install using pip

If PyCharm is not installed on your system, install the `pydevd-pycharm` package matching your PyCharm version:

```bash
pip install pydevd-pycharm~=<version of PyCharm on the local machine>
```

For example, if your PyCharm version is 242.20224.428:

```bash
pip install pydevd-pycharm~=242.20224.428
```

To find your PyCharm version, go to **PyCharm** → **About PyCharm** (or **Help** → **About** on some platforms).

For more information, see the [JetBrains Remote Debugging documentation](https://www.jetbrains.com/help/pycharm/remote-debugging-with-product.html#remote-debug-config).

## Configuration File

`charmd` supports a configuration file for setting default debug options on a per-project basis. This eliminates the need to specify common options on the command line for every invocation.

### File Location

The configuration file must be named `charmd.conf` and placed in the current working directory (the directory from which you run `charmd`).

### Creating the Configuration File

#### Option 1: Automatic Generation

Use the `--conf-init` flag to generate a configuration file with your current settings:

```bash
charmd --host 192.168.1.100 --port 5679 --suspend --conf-init
```

This creates a `charmd.conf` file in the current directory with the specified settings.

#### Option 2: Manual Creation

Create a `charmd.conf` file manually with your preferred text editor:

```properties
# charmd configuration file
# Lines starting with '#' are comments.

host = localhost
port = 5678
suspend = false
stdout_to_server = true
stderr_to_server = true
#pydevd_path = /path/to/pydevd_pycharm
```

### Configuration Options

All command-line debug options can be configured in the file:

| Option             | Type    | Default     | Description                             |
|--------------------|---------|-------------|-----------------------------------------|
| `host`             | string  | `localhost` | PyCharm debug server host               |
| `port`             | integer | `5678`      | PyCharm debug server port               |
| `suspend`          | boolean | `false`     | Suspend execution on start              |
| `stdout_to_server` | boolean | `true`      | Redirect stdout to debug server         |
| `stderr_to_server` | boolean | `true`      | Redirect stderr to debug server         |
| `pydevd_path`      | string  | (none)      | Path to pydevd-pycharm module directory |

### File Format

- **Key-value pairs:** Use `key = value` syntax
- **Comments:** Lines starting with `#` are ignored
- **Whitespace:** Leading and trailing whitespace is trimmed
- **Quotes:** Values can be quoted with single or double quotes to preserve internal whitespace
  ```
  host = "my host with spaces"
  pydevd_path = '/Applications/PyCharm.app/Contents/debug-eggs'
  ```
- **Boolean values:** Accepted values are `true`, `false`, `1`, `0`, `yes`, `no`, `y`, `n`, `on`, `off` (case-insensitive)

### Configuration Precedence

Settings are applied in the following order (later sources override earlier ones):

1. **Built-in defaults** (e.g., `host=localhost`, `port=5678`)
2. **Configuration file** (`charmd.conf` in current directory)
3. **Command-line arguments** (highest priority)

This allows you to set project-wide defaults in `charmd.conf` and override them on a per-invocation basis when needed.

### Example Workflow

```bash
# Set up project-specific debug configuration
cd /path/to/myproject
charmd --host 192.168.1.100 --port 5679 --conf-init

# Now run with config file defaults
charmd -- myscript.py

# Override specific settings when needed
charmd --suspend -- myscript.py
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

Wheel (`.whl`) files are available as release assets on the [GitHub releases page](https://github.com/tekwizely/python-charmd/releases). Download the desired version and install it directly:

```bash
pip install charmd-*.whl
```

Replace `*` with the specific version number, or use the exact filename.

### From Source (Clone Repository)

#### Standard Installation

Clone the repository and install using pip:

```bash
git clone https://github.com/tekwizely/python-charmd.git
cd python-charmd
pip install .
```

#### Editable/Development Installation

For development work, install in editable mode so changes take effect immediately:

```bash
git clone https://github.com/tekwizely/python-charmd.git
cd python-charmd
pip install -e .
```

This allows you to modify the source code and test changes without reinstalling.

#### Running Without Installation

You can also run `charmd` directly from the cloned repository without installing:

```bash
git clone https://github.com/tekwizely/python-charmd.git
cd python-charmd
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

------------------
## Troubleshooting

<!--
Each troubleshooting entry below follows a consistent, linkable pattern so issues are easy to find and act on. Use the template for future entries:

### Troubleshooting entry pattern
- Title: A short, descriptive title (use `###` so it appears in the TOC and is linkable)
- Issue: What you see (error messages, symptoms, and when it occurs)
- Solution: Concrete steps to resolve or work around the problem
- Example: Optional concrete command or config snippet demonstrating the fix
- Notes: Optional additional context or references
-->

### MacOS: pydevd attach.dylib missing when invoking a .py script

Issue

```
Expected: <PyCharm directory/.../pydevd-pycharm.egg/pydevd_attach_to_process/attach.dylib to exist.
```

This error can occur when running a Python script (for example `charmd -- myscript.py`).

On MacOS the packaged `pydevd-pycharm.egg` layout may not expose the bundled `attach.dylib` at the path `pydevd-pycharm` expects.

Solution

Point `charmd` at PyCharm's `pydev` helpers directory instead of the egg. You can pass the path via the `--pydevd-path` command-line option or set `pydevd_path` in `charmd.conf`:

```
<PyCharm directory>/Contents/plugins/python-ce/helpers/pydev
```

Example

```bash
charmd --pydevd-path "/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev" -- myscript.py
```

----------
## License

The `tekwizely/python-charmd` project is released under the [MIT](https://opensource.org/licenses/MIT) License.  See `LICENSE` file.
