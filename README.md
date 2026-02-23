# Project setup
In this project we use uv, a package manager to easily manage dependencies

## uv

[`uv`](https://github.com/astral-sh/uv) is an extremely fast Python package installer and resolver, designed as a drop-in replacement for pip.

### Installation

You can install `uv` using pipx or pip:

```bash
pipx install uv
```
Or:
```bash
pip install uv
```

Alternatively, download a prebuilt binary from the [releases page](https://github.com/astral-sh/uv/releases).

### Basic Usage

- **Install dependencies from `pyproject.toml`:**
    ```bash
    uv pip install -r requirements.txt
    ```
- **Add a new package:**
    ```bash
    uv pip install requests
    ```
- **Sync your environment with `pyproject.toml` and `uv.lock`:**
    ```bash
    uv pip sync
    ```
- **Upgrade a package:**
    ```bash
    uv pip install --upgrade requests
    ```

For more commands and options, run:
```bash
uv --help
```

### Resources

- [uv documentation](https://github.com/astral-sh/uv)
- [uv on PyPI](https://pypi.org/project/uv/)