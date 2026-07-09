from pathlib import Path


def get_landing_page() -> str:
    """Reads and returns the HTML content for the landing page."""
    template_path = Path(__file__).parent / "templates" / "index.html"
    return template_path.read_text(encoding="utf-8")
