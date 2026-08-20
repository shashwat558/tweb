import argparse
import sys

from tweb import __version__


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url:
        return url
    if "://" not in url:
        url = "https://" + url
    return url


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="tweb",
        description="A terminal-based web browser",
    )
    parser.add_argument(
        "url",
        nargs="?",
        help="URL to open",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with detailed error output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    if not args.url:
        print("Usage: tweb <URL>")
        print("Example: tweb https://example.com")
        sys.exit(1)

    url = normalize_url(args.url)

    try:
        from tweb.ui.app import TWebApp
        app = TWebApp(initial_url=url)
        app.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if args.debug:
            raise
        _print_error(str(e))
        sys.exit(1)


def _print_error(message: str) -> None:
    width = min(60, max(40, len(message) + 6))
    print()
    print(f"{'─' * width}")
    print(f"  Error")
    print()
    print(f"  {message}")
    print()
    print(f"{'─' * width}")
