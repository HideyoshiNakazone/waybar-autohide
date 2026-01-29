# Waybar Autohide

A lightweight Python script that automatically hides and shows [Waybar](https://github.com/Alexays/Waybar) based on window overlap and cursor position in [Hyprland](https://hyprland.org/).

## Features

- **Auto-hide on overlap**: Automatically hides Waybar when a window overlaps with the bar area
- **Cursor reveal**: Shows Waybar when the cursor approaches the top of the screen
- **Multi-monitor support**: Configure which monitors should have auto-hide enabled
- **Configurable refresh rate**: Adjust how often the script checks for changes

## Requirements

- Python >= 3.12
- [uv](https://github.com/astral-sh/uv) (for running the script)
- Hyprland window manager
- Waybar

## Installation

```bash
# Install to ~/.local/bin (default)
make install

# Or specify a custom path
make install INSTALL_PATH=/usr/local/bin
```

## Usage

Simply run the script:

```bash
waybar-autohide
```

### Recommended Usage

Add to your Hyprland config to start on launch:

```
exec-once = waybar-autohide
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WAYBAR_AUTOHIDE_MONITORS` | Comma-separated list of monitor IDs to enable auto-hide (e.g., `0,1`) | All monitors |
| `WAYBAR_AUTOHIDE_STATE` | Initial Waybar state: `1` (visible) or `0` (hidden) | `1` |
| `WAYBAR_AUTOHIDE_REFRESH_RATE` | Polling interval in seconds | `0.5` |
| `WAYBAR_AUTOHIDE_BAR_HEIGHT` | Height of the Waybar in pixels | `50` |
| `WAYBAR_AUTOHIDE_HEIGHT_THRESHOLD` | Additional threshold for overlap detection in pixels | `20` |
| `WAYBAR_AUTOHIDE_PROCNAME` | Process name of Waybar | `waybar` |

### Example

```bash
# Enable auto-hide only on monitor 0, starting hidden, with faster refresh
WAYBAR_AUTOHIDE_MONITORS=0 \
WAYBAR_AUTOHIDE_STATE=0 \
WAYBAR_AUTOHIDE_REFRESH_RATE=0.25 \
waybar-autohide
```


## How It Works

1. Polls Hyprland for active workspaces and window positions
2. Checks if any window overlaps with the Waybar area
3. Monitors cursor position to reveal the bar when the cursor approaches the top
4. Sends `SIGUSR1` to Waybar to toggle visibility

## Development

```bash
# Install dev dependencies and sync
make setup-dev

# Lint the code
make lint

# Format the code
make format
```

## License

GPLv2
