# Best Practices for Publishing Python Packages to PyPI with GitHub Actions

This comprehensive guide provides best practices for automating PyPI package publishing using GitHub Actions, based on analysis of popular Python projects and official PyPA recommendations.

## Attribution

This document was created through research of 80+ sources including popular PyPI projects, official Python Packaging Authority documentation, and community best practices.

Generated with assistance from Perplexity AI (https://www.perplexity.ai)

## Table of Contents

1. [Overview](#overview)
2. [Authentication: Trusted Publishing vs API Tokens](#authentication-trusted-publishing-vs-api-tokens)
3. [Project Structure and Configuration](#project-structure-and-configuration)
4. [Complete Workflow Examples](#complete-workflow-examples)
5. [Build Process Best Practices](#build-process-best-practices)
6. [Testing Strategy](#testing-strategy)
7. [Version Management](#version-management)
8. [Security and Code Quality](#security-and-code-quality)
9. [Advanced Topics](#advanced-topics)
10. [Common Pitfalls and Solutions](#common-pitfalls-and-solutions)

---

## Overview

Modern Python package publishing to PyPI should be automated, secure, and reproducible. GitHub Actions provides an excellent platform for this automation, and when combined with Trusted Publishing (OpenID Connect), eliminates the need for managing long-lived API tokens.

### Key Principles

- **Use Trusted Publishing** for secure, token-free authentication
- **Separate build and publish jobs** for security isolation
- **Test before publishing** to catch issues early
- **Use GitHub Releases** as triggers for PyPI publishing
- **Generate attestations** to verify package provenance
- **Follow semantic versioning** for version management

---

## Authentication: Trusted Publishing vs API Tokens

### Trusted Publishing (Recommended)

Trusted Publishing uses OpenID Connect (OIDC) to authenticate GitHub Actions with PyPI without requiring API tokens. This is the **recommended approach** for all new projects.

#### Benefits:
- **No credential management**: No tokens to create, store, or rotate
- **Improved security**: Short-lived credentials that expire automatically
- **Better auditability**: Direct link between published packages and source code
- **Reduced attack surface**: No long-lived tokens that can be compromised

#### Setting Up Trusted Publishing

1. **Configure PyPI (for new projects):**
   - Go to https://pypi.org/manage/account/publishing/
   - Add a "pending publisher" with:
     - **PyPI Project Name**: Your package name (exactly as in `pyproject.toml`)
     - **Owner**: Your GitHub username or organization
     - **Repository name**: Your repository name
     - **Workflow name**: e.g., `publish.yml`
     - **Environment name**: Leave empty or use "pypi" (optional but recommended)

2. **For existing projects:**
   - Go to your project page on PyPI
   - Navigate to "Manage" → "Publishing"
   - Add the trusted publisher configuration

3. **Workflow configuration:**
```yaml
permissions:
  id-token: write  # REQUIRED for trusted publishing
  contents: read

environment:
  name: pypi  # Optional but recommended
  url: https://pypi.org/p/your-package-name

steps:
  - name: Publish to PyPI
    uses: pypa/gh-action-pypi-publish@release/v1
    # No password or token needed!
```

### API Tokens (Legacy Approach)

While still supported, API tokens are **not recommended** for new projects. If you must use them:

```yaml
steps:
  - name: Publish to PyPI
    uses: pypa/gh-action-pypi-publish@release/v1
    with:
      password: ${{ secrets.PYPI_API_TOKEN }}
```

**Important**: Store tokens as repository secrets and use project-scoped tokens (not account-wide).

---

## Project Structure and Configuration

### Essential Files

Your project should include these files:

```
your-project/
├── .github/
│   └── workflows/
│       ├── ci.yml          # Continuous integration (tests, linting)
│       └── publish.yml     # Publishing to PyPI
├── src/
│   └── your_package/
│       ├── __init__.py
│       └── __version__.py  # Optional: version management
├── tests/
│   └── test_*.py
├── pyproject.toml          # Modern packaging configuration
├── README.md
├── LICENSE
└── CHANGELOG.md            # Optional but recommended
```

### pyproject.toml Configuration

Use modern `pyproject.toml` for all configuration:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "your-package-name"
version = "0.1.0"  # Or use dynamic versioning
description = "A short description of your package"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "you@example.com"}
]
keywords = ["keyword1", "keyword2"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "requests>=2.28.0",
    "click>=8.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

[project.urls]
Homepage = "https://github.com/yourusername/your-package"
Documentation = "https://your-package.readthedocs.io"
Repository = "https://github.com/yourusername/your-package"
Issues = "https://github.com/yourusername/your-package/issues"
Changelog = "https://github.com/yourusername/your-package/blob/main/CHANGELOG.md"

[project.scripts]
your-cli = "your_package.cli:main"

# Tool configurations
[tool.black]
line-length = 88
target-version = ["py39", "py310", "py311", "py312"]

[tool.ruff]
line-length = 88
select = ["E", "F", "W", "B", "C90"]
target-version = "py39"

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
addopts = "-ra -q --cov=your_package --cov-report=term-missing"
```

---

## Complete Workflow Examples

### Example 1: Basic Publish Workflow (Recommended)

This is the **minimal recommended workflow** using Trusted Publishing:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  build:
    name: Build distribution
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.x"
      
      - name: Install build dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build
      
      - name: Build package
        run: python -m build
      
      - name: Store distribution packages
        uses: actions/upload-artifact@v4
        with:
          name: python-package-distributions
          path: dist/

  publish-to-pypi:
    name: Publish to PyPI
    needs: [build]
    runs-on: ubuntu-latest
    
    environment:
      name: pypi
      url: https://pypi.org/p/your-package-name
    
    permissions:
      id-token: write  # IMPORTANT: mandatory for trusted publishing
    
    steps:
      - name: Download distributions
        uses: actions/download-artifact@v4
        with:
          name: python-package-distributions
          path: dist/
      
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

### Example 2: Complete CI/CD Pipeline

A comprehensive workflow that includes testing, TestPyPI, and production PyPI:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  release:
    types: [published]

jobs:
  test:
    name: Test on Python ${{ matrix.python-version }}
    runs-on: ubuntu-latest
    
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
      
      - name: Run tests
        run: pytest -v --cov --cov-report=xml
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        if: matrix.python-version == '3.11'
        with:
          file: ./coverage.xml

  lint:
    name: Linting and Code Quality
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install black ruff mypy
      
      - name: Check formatting with Black
        run: black --check .
      
      - name: Lint with Ruff
        run: ruff check .
      
      - name: Type check with MyPy
        run: mypy src/

  build:
    name: Build distribution
    needs: [test, lint]
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for versioning
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.x"
      
      - name: Install build dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build
      
      - name: Build package
        run: python -m build
      
      - name: Verify build
        run: |
          python -m pip install twine
          twine check dist/*
      
      - name: Store distribution packages
        uses: actions/upload-artifact@v4
        with:
          name: python-package-distributions
          path: dist/

  publish-to-testpypi:
    name: Publish to TestPyPI
    needs: [build]
    runs-on: ubuntu-latest
    if: github.event_name == 'release'
    
    environment:
      name: testpypi
      url: https://test.pypi.org/p/your-package-name
    
    permissions:
      id-token: write
    
    steps:
      - name: Download distributions
        uses: actions/download-artifact@v4
        with:
          name: python-package-distributions
          path: dist/
      
      - name: Publish to TestPyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/

  publish-to-pypi:
    name: Publish to PyPI
    needs: [publish-to-testpypi]
    runs-on: ubuntu-latest
    if: github.event_name == 'release'
    
    environment:
      name: pypi
      url: https://pypi.org/p/your-package-name
    
    permissions:
      id-token: write
    
    steps:
      - name: Download distributions
        uses: actions/download-artifact@v4
        with:
          name: python-package-distributions
          path: dist/
      
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

### Example 3: Workflow with Attestations

Generate cryptographic attestations for package provenance (recommended for enhanced security):

```yaml
name: Publish with Attestations

on:
  release:
    types: [published]

jobs:
  build:
    name: Build distribution
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.x"
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build
      
      - name: Build package
        run: python -m build
      
      - name: Store distribution packages
        uses: actions/upload-artifact@v4
        with:
          name: python-package-distributions
          path: dist/

  publish-to-pypi:
    name: Publish to PyPI
    needs: [build]
    runs-on: ubuntu-latest
    
    environment:
      name: pypi
      url: https://pypi.org/p/your-package-name
    
    permissions:
      id-token: write
      attestations: write
      contents: read
    
    steps:
      - name: Download distributions
        uses: actions/download-artifact@v4
        with:
          name: python-package-distributions
          path: dist/
      
      - name: Generate artifact attestation
        uses: actions/attest-build-provenance@v1
        with:
          subject-path: 'dist/*'
      
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        # Attestations are automatically included starting with v1.8.0
```

---

## Build Process Best Practices

### Use the `build` Package

Always use the `build` package (PEP 517) instead of calling `setup.py` directly:

```yaml
- name: Install build
  run: python -m pip install build

- name: Build package
  run: python -m build
```

This creates both source distribution (`.tar.gz`) and wheel (`.whl`) files.

### Verify Your Build

Before publishing, verify your distribution:

```yaml
- name: Verify build
  run: |
    pip install twine
    twine check dist/*
```

### Test Installation Locally

Before publishing, test that your package installs correctly:

```bash
# Build locally
python -m build

# Test installation
pip install dist/*.whl

# Test import
python -c "import your_package; print(your_package.__version__)"
```

### Build Artifacts

Store build artifacts for debugging and verification:

```yaml
- name: Store distribution packages
  uses: actions/upload-artifact@v4
  with:
    name: python-package-distributions
    path: dist/
    retention-days: 30  # Keep for 30 days
```

---

## Testing Strategy

### Multi-Version Testing

Test against multiple Python versions using a matrix strategy:

```yaml
jobs:
  test:
    name: Test Python ${{ matrix.python-version }}
    runs-on: ${{ matrix.os }}
    
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
        os: [ubuntu-latest, windows-latest, macos-latest]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
      
      - name: Run tests
        run: pytest -v --cov
```

### Pre-Publish Testing

Always run tests before publishing:

```yaml
jobs:
  test:
    # ... test job

  build:
    needs: [test]  # Only build after tests pass
    # ... build job

  publish:
    needs: [build]  # Only publish after build succeeds
    # ... publish job
```

### Testing Against TestPyPI

Use TestPyPI to verify your package before production:

```yaml
publish-to-testpypi:
  name: Publish to TestPyPI
  environment:
    name: testpypi
    url: https://test.pypi.org/p/your-package
  steps:
    - name: Publish to TestPyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        repository-url: https://test.pypi.org/legacy/
```

**Note**: TestPyPI has separate credentials and uses a different trusted publisher configuration.

---

## Version Management

### Semantic Versioning

Follow semantic versioning (SemVer) for your releases:

- **MAJOR** version: Incompatible API changes
- **MINOR** version: Backward-compatible functionality
- **PATCH** version: Backward-compatible bug fixes

Example: `1.2.3` → `1.2.4` (patch) → `1.3.0` (minor) → `2.0.0` (major)

### Version Management Strategies

#### Option 1: Manual Versioning

Update version in `pyproject.toml` manually:

```toml
[project]
version = "1.2.3"
```

Then create a Git tag:

```bash
git tag -a v1.2.3 -m "Release version 1.2.3"
git push origin v1.2.3
```

#### Option 2: Single-Source Version

Use a version file and dynamic reading:

```python
# src/your_package/__version__.py
__version__ = "1.2.3"
```

```toml
# pyproject.toml
[project]
dynamic = ["version"]

[tool.setuptools.dynamic]
version = {attr = "your_package.__version__"}
```

#### Option 3: Git Tag-Based Versioning (setuptools-scm)

Automatically generate version from Git tags:

```toml
[build-system]
requires = ["setuptools>=61.0", "setuptools-scm[toml]>=7.0"]

[project]
dynamic = ["version"]

[tool.setuptools_scm]
write_to = "src/your_package/_version.py"
```

Then in your package:

```python
from ._version import __version__
```

#### Option 4: Python Semantic Release

Automate version bumping based on commit messages:

```yaml
- name: Python Semantic Release
  uses: python-semantic-release/python-semantic-release@v8
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
```

This requires conventional commit messages:
- `feat:` → minor version bump
- `fix:` → patch version bump
- `BREAKING CHANGE:` → major version bump

### Release Workflow

1. **Update version** (if not using automation)
2. **Update CHANGELOG.md**
3. **Commit changes**: `git commit -m "Bump version to 1.2.3"`
4. **Create and push tag**: `git tag v1.2.3 && git push origin v1.2.3`
5. **Create GitHub Release** (triggers publish workflow)

---

## Security and Code Quality

### Code Formatting and Linting

#### Black (Code Formatter)

```yaml
- name: Check formatting
  run: |
    pip install black
    black --check .
```

Configuration in `pyproject.toml`:

```toml
[tool.black]
line-length = 88
target-version = ["py39"]
```

#### Ruff (Fast Linter)

```yaml
- name: Lint with Ruff
  run: |
    pip install ruff
    ruff check .
```

Configuration:

```toml
[tool.ruff]
line-length = 88
select = ["E", "F", "W", "B", "C90", "I"]
target-version = "py39"
```

#### Type Checking (MyPy)

```yaml
- name: Type check
  run: |
    pip install mypy
    mypy src/
```

### Security Scanning

#### Bandit (Security Linter)

```yaml
- name: Security check with Bandit
  run: |
    pip install bandit
    bandit -r src/
```

#### Safety (Dependency Vulnerability Scanner)

```yaml
- name: Check dependencies
  run: |
    pip install safety
    safety check
```

### Complete Quality Workflow

```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      
      - name: Install dependencies
        run: |
          pip install black ruff mypy bandit safety
          pip install -e ".[dev]"
      
      - name: Format check
        run: black --check .
      
      - name: Lint
        run: ruff check .
      
      - name: Type check
        run: mypy src/
      
      - name: Security scan
        run: bandit -r src/
      
      - name: Dependency check
        run: safety check --json
```

---

## Advanced Topics

### Building Wheels for Multiple Platforms

For packages with C extensions, use `cibuildwheel`:

```yaml
jobs:
  build_wheels:
    name: Build wheels on ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-13, macos-14]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Build wheels
        uses: pypa/cibuildwheel@v2.16.0
        env:
          CIBW_SKIP: "cp36-* cp37-* cp38-* pp* *-win32"
      
      - uses: actions/upload-artifact@v4
        with:
          name: cibw-wheels-${{ matrix.os }}-${{ strategy.job-index }}
          path: ./wheelhouse/*.whl
```

### Conditional Publishing

Publish only on tags:

```yaml
on:
  push:
    tags:
      - 'v*'  # Trigger on tags like v1.0.0
```

Or only from main branch:

```yaml
if: github.event_name == 'push' && github.ref == 'refs/heads/main'
```

### Environment Protection

Use GitHub Environments for additional protection:

1. Go to Settings → Environments → New environment
2. Add protection rules:
   - Required reviewers
   - Wait timer
   - Deployment branches

```yaml
environment:
  name: pypi
  url: https://pypi.org/p/your-package
```

### Dry-Run Mode

Test publishing without actually uploading:

```yaml
- name: Dry run publish
  run: |
    pip install twine
    twine upload --repository testpypi --skip-existing dist/* --verbose
```

### Multi-Package Repositories (Monorepo)

For monorepos with multiple packages:

```yaml
strategy:
  matrix:
    package:
      - package-a
      - package-b

steps:
  - name: Build package
    run: python -m build packages/${{ matrix.package }}
```

---

## Common Pitfalls and Solutions

### Pitfall 1: Version Conflicts

**Problem**: Publishing the same version twice fails.

**Solution**: 
- Never reuse version numbers
- Use unique version numbers for each release
- Consider using pre-release versions (e.g., `1.0.0rc1`) for testing

### Pitfall 2: Missing Files in Distribution

**Problem**: Important files not included in package.

**Solution**: Use `MANIFEST.in` or configure `pyproject.toml`:

```toml
[tool.setuptools]
include-package-data = true

[tool.setuptools.packages.find]
where = ["src"]
include = ["your_package*"]

[tool.setuptools.package-data]
your_package = ["py.typed", "*.pyi"]
```

### Pitfall 3: Broken Dependencies

**Problem**: Package installs but imports fail due to missing dependencies.

**Solution**:
- Test installation in clean environment
- Specify all required dependencies in `pyproject.toml`
- Use `pip check` to verify dependencies

### Pitfall 4: Large Package Size

**Problem**: Package is unnecessarily large.

**Solution**:
- Exclude test files, docs, and unnecessary data
- Use `.gitignore` patterns
- Check package contents: `tar -tzf dist/*.tar.gz`

### Pitfall 5: Workflow Runs Twice

**Problem**: Workflow triggers on both push and release.

**Solution**: Use conditional execution:

```yaml
if: github.event_name == 'release' && github.event.action == 'published'
```

### Pitfall 6: Token Permissions

**Problem**: Trusted Publishing fails with permission errors.

**Solution**: Ensure correct permissions:

```yaml
permissions:
  id-token: write  # Required
  contents: read    # Recommended
```

### Pitfall 7: Build Reproducibility

**Problem**: Builds differ between local and CI.

**Solution**:
- Pin build dependencies
- Use `python -m build` consistently
- Set environment variables for reproducible builds

---

## Quick Reference: Publishing Checklist

### Before First Release

- [ ] Create PyPI account
- [ ] Set up Trusted Publisher on PyPI
- [ ] Configure `pyproject.toml` with all metadata
- [ ] Add LICENSE file
- [ ] Write README.md with usage examples
- [ ] Set up GitHub workflow
- [ ] Test build locally
- [ ] Verify package contents

### For Each Release

- [ ] Update version number
- [ ] Update CHANGELOG.md
- [ ] Run tests locally
- [ ] Commit changes
- [ ] Create and push Git tag
- [ ] Create GitHub Release
- [ ] Verify workflow runs successfully
- [ ] Test installation from PyPI
- [ ] Announce release

---

## Additional Resources

### Official Documentation
- [PyPA Packaging Guide](https://packaging.python.org/)
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [pypa/gh-action-pypi-publish](https://github.com/marketplace/actions/pypi-publish)

### Tools
- [build](https://pypa-build.readthedocs.io/) - PEP 517 package builder
- [twine](https://twine.readthedocs.io/) - Package upload tool
- [cibuildwheel](https://cibuildwheel.readthedocs.io/) - Build wheels for multiple platforms
- [setuptools-scm](https://setuptools-scm.readthedocs.io/) - Version from Git tags

### Example Projects
- [requests](https://github.com/psf/requests) - Popular HTTP library
- [httpx](https://github.com/encode/httpx) - Modern HTTP client
- [black](https://github.com/psf/black) - Code formatter
- [pydantic-core](https://github.com/pydantic/pydantic-core) - Rust-based validation library

---

## Conclusion

Publishing Python packages to PyPI using GitHub Actions is straightforward when following best practices:

1. **Use Trusted Publishing** for secure authentication
2. **Separate concerns** with distinct build, test, and publish jobs
3. **Test thoroughly** across Python versions and platforms
4. **Follow semantic versioning** for clear version management
5. **Maintain code quality** with linting and security scanning
6. **Generate attestations** for package provenance
7. **Use GitHub Releases** as the trigger for publishing

By following these practices, you'll have a robust, secure, and maintainable CI/CD pipeline for your Python packages.

---

*Last Updated: October 2025*
*Based on analysis of popular PyPI projects and official PyPA guidelines*
