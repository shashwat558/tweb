# tweb — Terminal Web Browser

A modern, keyboard-first, terminal-native web browser built with Python.

## Features

- **URL navigation** — Open any website directly in your terminal
- **HTML rendering** — Clean, readable text output with support for headings, lists, tables, code blocks, and more
- **Interactive links** — Navigate between pages with keyboard shortcuts
- **Scrolling** — PageUp/PageDown, Home/End for long pages
- **Back/forward history** — Navigate your browsing history
- **Find in page** — Search for text with Ctrl+F
- **Basic forms** — Fill out and submit simple forms
- **Session support** — Cookies persist across pages
- **Error handling** — Friendly terminal error messages

## Installation

```bash
# Clone the repository
git clone https://github.com/shashwat558/tweb.git
cd tweb

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"
```

## Usage

```bash
# Open a URL
tweb https://example.com

# Open without scheme (automatically adds https://)
tweb example.com

# Show help
tweb --help

# Show version
tweb --version

# Debug mode (shows tracebacks)
tweb --debug https://example.com
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+Q` | Quit |
| `Ctrl+L` | Focus URL bar |
| `Ctrl+R` | Reload page |
| `Ctrl+F` | Find in page |
| `Alt+←` | Go back |
| `Alt+→` | Go forward |
| `j` / `↓` | Select next link / Scroll down |
| `k` / `↑` | Select previous link / Scroll up |
| `Enter` | Open selected link |
| `PageUp` | Scroll up one page |
| `PageDown` | Scroll down one page |
| `Home` | Scroll to top |
| `End` | Scroll to bottom |

## Architecture

```
tweb/
├── pyproject.toml
├── README.md
├── tests/
│   ├── test_browser.py
│   ├── test_history.py
│   ├── test_parser.py
│   └── test_url.py
└── src/
    └── tweb/
        ├── __init__.py
        ├── __main__.py
        ├── cli.py
        ├── browser/
        │   ├── engine.py
        │   └── history.py
        ├── parser/
        │   ├── html.py
        │   └── elements.py
        ├── renderer/
        │   ├── document.py
        │   └── terminal.py
        ├── networking/
        │   └── client.py
        └── ui/
            ├── app.py
            ├── widgets.py
            └── keybindings.py
```

### Components

- **CLI** — Argument parsing and application entry point
- **NetworkClient** — HTTP client with session/cookie support
- **HTMLParser** — Parses HTML into an intermediate document representation
- **DocumentRenderer** — Converts documents to Rich renderables
- **BrowserEngine** — Orchestrates fetch → parse → render
- **TWebApp** — Textual-based terminal UI

## Limitations

- No JavaScript execution
- No CSS layout (terminal-friendly rendering only)
- No image rendering (shows `[Image: alt text]`)
- No tab support
- Limited form support (GET forms only)

## Roadmap

- [ ] Tab support
- [ ] Bookmarks
- [ ] Downloads
- [ ] JavaScript engine
- [ ] Image rendering (Kitty/Sixel)
- [ ] CSS layout engine
- [ ] Extensions
- [ ] AI assistant

## Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with debug output
tweb --debug https://example.com
```

## License

MIT
