"""
Styling definitions and color themes for the terminal user interface.
"""

from rich.theme import Theme

APP_THEME = Theme(
    {
        "primary": "cyan bold",
        "secondary": "bright_blue",
        "accent": "magenta bold",
        "success": "green bold",
        "warning": "yellow bold",
        "error": "red bold",
        "info": "white",
        "muted": "dim white",
        "highlight": "bright_cyan bold",
    }
)
