"""
Component: BannerComponent
Purpose: Displays the stylized application logo and introductory tagline in the terminal.
Usage:
  - Inputs: None
  - Outputs: Rich Panel object printable by Console
  - Bindings: None
Key UI elements:
  - ASCII art typography logo
  - Subtitle badge: "High-speed documentation crawler & Markdown generator for NotebookLM"
  - Gradient border styling
Used In:
  - SetupScreen
  - DashboardScreen
  - SummaryScreen
"""

from rich.panel import Panel
from rich.align import Align
from rich.text import Text


class BannerComponent:
    """
    Renders the primary application header banner.
    """

    LOGO_TEXT = (
        r"  _____                      _____            _       " "\n"
        r" |  __ \                    / ____|          | |      " "\n"
        r" | |__) |__ _  __ _   ___  | (___   ___  __ _| |_ __  " "\n"
        r" |  ___// _` |/ _` | / _ \  \___ \ / __|/ _` | | '_ \ " "\n"
        r" | |   | (_| | (_| ||  __/  ____) | (__| (_| | | |_) |" "\n"
        r" |_|    \__,_|\__, | \___| |_____/ \___|\__,_|_| .__/ " "\n"
        r"               __/ |                           | |    " "\n"
        r"              |___/                            |_|    "
    )

    def render(self) -> Panel:
        """
        Builds and returns the styled banner panel.
        
        Invoked by:
        - SetupScreen
        - DashboardScreen
        - SummaryScreen
        """
        logo = Text(self.LOGO_TEXT, style="cyan bold")
        tagline = Text(
            "\n🚀 High-speed documentation crawler & Markdown generator for Google NotebookLM\n",
            style="bright_white bold",
        )
        version_badge = Text("Version 1.0.0 | Strict URL Prefix Scoping", style="dim cyan")

        content = Text.assemble(logo, "\n", tagline, version_badge)
        aligned_content = Align.center(content)

        return Panel(
            aligned_content,
            border_style="bright_blue",
            padding=(1, 2),
        )
