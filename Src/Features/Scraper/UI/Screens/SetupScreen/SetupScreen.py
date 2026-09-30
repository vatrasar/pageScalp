"""
Screen: SetupScreen
Purpose: Provides an interactive wizard for configuring crawl parameters (URL, scope, exclusions, character limits, output).
Available Functionalities:
  - Seed URL input and validation
  - Strict URL prefix boundary confirmation
  - Upfront path exclusion rules configuration
  - Character limit threshold configuration
  - Output filename configuration
Key UI elements:
  - BannerComponent
  - Questionary interactive text inputs and confirmations
Navigation:
  - Navigate From: main.py entrypoint
  - Navigate To: DashboardScreen
"""

from urllib.parse import urlparse
import re
from typing import Optional, List
import questionary
from rich.console import Console
from Src.Features.Scraper.Domain.CrawlConfiguration import CrawlConfiguration
from Src.Features.Scraper.Domain.CrawlScopeMode import CrawlScopeMode
from Src.Features.Scraper.UI.FeatureComponents.BannerComponent import BannerComponent


class SetupScreen:
    """
    Guides the user through interactive crawl session configuration.
    """

    def __init__(self, console: Console) -> None:
        self._console = console
        self._banner = BannerComponent()

    def prompt_configuration(self) -> Optional[CrawlConfiguration]:
        """
        Executes the questionary prompt sequence to construct a CrawlConfiguration.
        
        Invoked by:
        - main.py CLI entrypoint when run in interactive mode.
        """
        self._console.print(self._banner.render())
        self._console.print("[dim cyan]Configure your crawl parameters below:[/dim cyan]\n")

        seed_url = self._prompt_seed_url()
        if not seed_url:
            return None

        parsed = urlparse(seed_url)
        suggested_prefix = parsed.path.rstrip("/")
        default_filename = self._generate_default_filename(parsed.netloc, suggested_prefix)

        initial_exclusions = self._prompt_initial_exclusions()
        max_pages = self._prompt_integer("Maximum number of pages to crawl:", default=100)
        max_chars = self._prompt_integer(
            "Character limit per file before splitting (for NotebookLM):", default=1000000
        )
        output_file = self._prompt_output_file(default_filename)

        return CrawlConfiguration(
            seed_url=seed_url,
            scope_mode=CrawlScopeMode.PATH_PREFIX,
            path_prefix=suggested_prefix,
            excluded_patterns=initial_exclusions,
            max_pages=max_pages,
            max_characters_per_file=max_chars,
            output_destination=output_file,
            concurrency=5,
            delay_seconds=0.1,
            enable_review=True,
        )

    def _prompt_seed_url(self) -> Optional[str]:
        response = questionary.text(
            "Enter starting website/documentation URL:",
            validate=lambda val: True if val.startswith("http://") or val.startswith("https://")
            else "Please enter a valid URL starting with http:// or https://",
        ).ask()
        return response.strip() if response else None

    def _prompt_initial_exclusions(self) -> List[str]:
        response = questionary.text(
            "Any paths or URL patterns to exclude upfront? (optional, comma-separated e.g. /legacy, /bola/kula):",
            default="",
        ).ask()
        if not response:
            return []
        return [pattern.strip() for pattern in response.split(",") if pattern.strip()]

    def _prompt_integer(self, message: str, default: int) -> int:
        response = questionary.text(
            message,
            default=str(default),
            validate=lambda val: True if val.isdigit() and int(val) > 0 else "Enter a positive number",
        ).ask()
        return int(response) if response else default

    def _prompt_output_file(self, default_name: str) -> str:
        response = questionary.text(
            "Output Markdown file destination:",
            default=default_name,
        ).ask()
        return response.strip() if response else default_name

    def _generate_default_filename(self, host: str, path: str) -> str:
        clean_host = host.replace("www.", "").split(":")[0]
        sanitized_path = re.sub(r"[^\w-]", "_", path).strip("_")
        base = f"{clean_host}_{sanitized_path}" if sanitized_path else clean_host
        return f"{base}_documentation.md"
