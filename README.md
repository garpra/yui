# Yui - AppImage Manager for Linux

Yui is a CLI (Command Line Interface) tool designed to manage AppImage applications on Linux. With Yui, you can install, update, remove, and list AppImage applications directly from GitHub repositories. It also handles automatic integration with your Linux desktop menu.

## Features

- **Easy Installation** - Just provide the GitHub `owner/repo`, and Yui automatically downloads the latest AppImage version.
- **Desktop Integration** - Automatically extracts `.desktop` files and icons so applications appear in your application launcher.
- **Bulk Updates** - Update all installed AppImage applications with a single command.
- **Local Repo Management** - Stores application metadata in a local repository (JSON) for version tracking.
- **Security** - GitHub URL validation and file locking for safe operations.

## Technology Stack

- **Python**
- **argparse** - CLI argument parsing.
- **requests** - HTTP client for interacting with the GitHub API.
- **filelock** - File locking for secure repository access.
- **pytest & pytest-mock** - Testing framework.
- **subprocess** - Mounts AppImages for metadata extraction.

## Installation

### Prerequisites

- Python 3.9 or newer
- Linux
- The target application must have AppImage files available as _release assets_ in its GitHub repository

### Installation Steps

You can install Yui using the provided Makefile (recommended) or manually.

#### Using Makefile (Recommended)

1. Clone this repository:

```bash
git clone https://github.com/garpra/yui.git
cd yui
```

2. Setup the environment and install dependencies:

```bash
make setup
```

3. (Optional) Build a standalone executable:

```bash
make build
```

This will create a single `yui` binary that can be run without requiring Python or a virtual environment.

#### Manual Installation

1. Clone this repository:

```bash
git clone https://github.com/garpra/yui.git
cd yui
```

2. Create and activate a virtual environment (optional, but recommended):

```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run Yui:

```bash
python app.py --help
```

### Makefile Commands

| Command      | Description                                         |
| ------------ | --------------------------------------------------- |
| `make setup` | Create virtual environment and install dependencies |
| `make build` | Build a standalone executable using Nuitka          |
| `make clean` | Remove virtual environment and build artifacts      |

## Usage

### Install an Application

Install an AppImage from a GitHub repository using the `owner/repo` format:

```bash
python app.py install owner/repo
```

Example:

```bash
python app.py install jmeter/jmeter
```

### List Installed Applications

Display all applications managed by Yui:

```bash
python app.py list
```

### Update All Applications

Update all installed AppImage applications to their latest versions:

```bash
python app.py update
```

### Remove an Application

Uninstall a managed application:

```bash
python app.py delete owner/repo
```

## Data & Directories

Yui stores its data in `~/.local/share/yui/` (customizable via the `YUI_DATA_DIR` environment variable):

| Path                            | Description                               |
| ------------------------------- | ----------------------------------------- |
| `~/.local/share/yui/appimage/`  | Downloaded AppImage files                 |
| `~/.local/share/yui/repos.json` | Metadata for installed applications       |
| `~/.local/share/applications/`  | `.desktop` files (Linux menu integration) |
| `~/.local/share/icons/yui/`     | Application icons                         |

## Testing

Run the full suite of unit tests:

```bash
pytest
```
