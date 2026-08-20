from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import Footer, Header, Input, Static

from tweb.browser.engine import BrowserEngine
from tweb.browser.history import BrowserHistory
from tweb.parser.elements import Document, Link
from tweb.ui.keybindings import BINDINGS
from tweb.ui.widgets import ContentView, StatusBar


class TWebApp(App):
    CSS = """
    #url-bar {
        dock: top;
        height: 3;
        background: $surface;
        border-bottom: solid $primary;
    }

    #url-input {
        width: 100%;
    }

    #find-bar {
        dock: top;
        height: 3;
        background: $surface;
        border-bottom: solid $primary;
        display: none;
    }

    #find-bar.visible {
        display: block;
    }

    #find-input {
        width: 100%;
    }

    #content {
        height: 1fr;
        overflow-y: auto;
        padding: 1 2;
    }

    #content:focus {
        background: $surface;
    }

    #status-bar {
        dock: bottom;
        height: 1;
        background: $surface;
        border-top: solid $primary;
    }
    """

    BINDINGS = BINDINGS

    def __init__(self, initial_url: str) -> None:
        super().__init__()
        self._initial_url = initial_url
        self._engine = BrowserEngine()
        self._history = BrowserHistory()
        self._current_url = initial_url
        self._links: list[Link] = []
        self._selected_link: int = -1
        self._document: Document | None = None
        self._find_visible = False
        self._find_query = ""
        self._find_index = 0
        self._find_matches: list[int] = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="url-bar"):
            yield Input(placeholder="Enter URL...", id="url-input", value=self._initial_url)
        with Vertical(id="find-bar"):
            yield Input(placeholder="Find in page... (Enter to search)", id="find-input")
        yield ContentView(id="content")
        yield StatusBar(id="status-bar")
        yield Footer()

    async def on_mount(self) -> None:
        await self._load_page(self._initial_url)

    def _focus_content(self) -> None:
        content = self.query_one("#content", ContentView)
        content.focus()

    async def _load_page(self, url: str, from_history: bool = False) -> None:
        status_bar = self.query_one("#status-bar", StatusBar)
        content = self.query_one("#content", ContentView)
        url_input = self.query_one("#url-input", Input)

        status_bar.set_status(f"Loading {url}...")
        url_input.value = url
        self._current_url = url
        self._selected_link = -1
        self._links = []
        self._find_matches = []
        self._find_index = 0

        try:
            document = await self._engine.navigate(url)
            self._document = document
            self._links = document.links
            content.set_content(self._format_document(document))
            status_bar.set_status(f"{document.title} - {url}")
            if not from_history:
                self._history.push(url)
            self._focus_content()
        except Exception as e:
            content.set_content(f"Error: {e}")
            status_bar.set_status("Error loading page")
            self._focus_content()

    def _format_document(self, document) -> str:
        lines = []
        lines.append(f"{'=' * 60}")
        lines.append(f"  {document.title}")
        lines.append(f"{'=' * 60}")
        lines.append("")

        for block in document.blocks:
            lines.extend(self._render_block(block))
            lines.append("")

        if document.links:
            lines.append("─" * 60)
            lines.append("  Links:")
            for i, link in enumerate(document.links):
                marker = "▶" if i == self._selected_link else " "
                lines.append(f"  {marker}[{link.index + 1}] {link.text}")
            lines.append("─" * 60)

        return "\n".join(lines)

    def _render_block(self, block) -> list[str]:
        from tweb.parser.elements import (
            CodeBlock,
            Form,
            Heading,
            HorizontalRule,
            Image,
            List,
            Paragraph,
            Table,
        )

        if isinstance(block, Heading):
            prefix = "#" * block.level
            return [f"{prefix} {block.text}"]

        elif isinstance(block, Paragraph):
            return [block.text]

        elif isinstance(block, Link):
            return [f"  [{block.index + 1}] {block.text}"]

        elif isinstance(block, Image):
            return [f"  [Image: {block.alt}]"]

        elif isinstance(block, CodeBlock):
            lines = ["  ┌" + "─" * 58 + "┐"]
            for line in block.code.split("\n"):
                lines.append(f"  │ {line:<56} │")
            lines.append("  └" + "─" * 58 + "┘")
            return lines

        elif isinstance(block, List):
            lines = []
            for i, item in enumerate(block.items):
                bullet = f"  {i + 1}." if block.ordered else "  •"
                for item_block in item.blocks:
                    if isinstance(item_block, Paragraph):
                        lines.append(f"{bullet} {item_block.text}")
                    elif isinstance(item_block, Link):
                        lines.append(f"{bullet} [{item_block.index + 1}] {item_block.text}")
            return lines

        elif isinstance(block, Table):
            return self._render_table(block)

        elif isinstance(block, HorizontalRule):
            return ["─" * 60]

        elif isinstance(block, Form):
            return self._render_form(block)

        return []

    def _render_table(self, table) -> list[str]:
        if not table.rows:
            return []

        num_cols = max(len(row.cells) for row in table.rows)
        col_widths = [0] * num_cols
        for row in table.rows:
            for i, cell in enumerate(row.cells):
                col_widths[i] = max(col_widths[i], len(cell.text))

        lines = []
        for row in table.rows:
            parts = []
            for i, cell in enumerate(row.cells):
                width = col_widths[i] if i < len(col_widths) else 10
                text = cell.text.ljust(width)
                parts.append(f" {text} ")
            lines.append("│".join(parts))

        sep = "┼".join("─" * (w + 2) for w in col_widths)
        lines.append(sep)

        return lines

    def _render_form(self, form) -> list[str]:
        lines = []
        lines.append("  ┌" + "─" * 58 + "┐")
        for field in form.fields:
            if field.field_type == "textarea":
                lines.append(f"  │ {field.name or 'Text'}:                           │")
                lines.append(f"  │ {'─' * 56} │")
            else:
                placeholder = field.placeholder or field.name or field.field_type
                input_box = f"[{placeholder}]"
                lines.append(f"  │ {field.name or field.field_type}: {input_box:<48} │")
        lines.append(f"  │ [{form.submit_text:<54}] │")
        lines.append("  └" + "─" * 58 + "┘")
        return lines

    def _update_content(self) -> None:
        if self._document:
            content = self.query_one("#content", ContentView)
            content.set_content(self._format_document(self._document))

    def _perform_find(self, query: str) -> None:
        if not query or not self._document:
            self._find_matches = []
            self._find_index = 0
            return

        content = self.query_one("#content", ContentView)
        text = content.get_content()
        self._find_matches = []
        query_lower = query.lower()
        start = 0
        while True:
            idx = text.lower().find(query_lower, start)
            if idx == -1:
                break
            self._find_matches.append(idx)
            start = idx + 1

        self._find_index = 0
        status_bar = self.query_one("#status-bar", StatusBar)
        if self._find_matches:
            status_bar.set_status(f"Found {len(self._find_matches)} matches")
        else:
            status_bar.set_status("No matches found")

    def _content_is_focused(self) -> bool:
        content = self.query_one("#content", ContentView)
        return content.has_focus

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "url-input":
            url = event.value.strip()
            if url:
                from tweb.cli import normalize_url
                url = normalize_url(url)
                await self._load_page(url)
        elif event.input.id == "find-input":
            query = event.value.strip()
            self._find_query = query
            self._perform_find(query)

    async def action_focus_url(self) -> None:
        url_input = self.query_one("#url-input", Input)
        url_input.focus()

    async def action_focus_content(self) -> None:
        find_bar = self.query_one("#find-bar")
        if self._find_visible:
            find_bar.remove_class("visible")
            self._find_visible = False
            self._find_matches = []
            self._find_index = 0
        self._focus_content()

    async def action_toggle_find(self) -> None:
        find_bar = self.query_one("#find-bar")
        self._find_visible = not self._find_visible
        if self._find_visible:
            find_bar.add_class("visible")
            find_input = self.query_one("#find-input", Input)
            find_input.focus()
        else:
            find_bar.remove_class("visible")
            self._find_matches = []
            self._find_index = 0
            self._focus_content()

    async def action_find_next(self) -> None:
        if self._find_matches:
            self._find_index = (self._find_index + 1) % len(self._find_matches)
            status_bar = self.query_one("#status-bar", StatusBar)
            status_bar.set_status(
                f"Match {self._find_index + 1} of {len(self._find_matches)}"
            )

    async def action_find_prev(self) -> None:
        if self._find_matches:
            self._find_index = (self._find_index - 1) % len(self._find_matches)
            status_bar = self.query_one("#status-bar", StatusBar)
            status_bar.set_status(
                f"Match {self._find_index + 1} of {len(self._find_matches)}"
            )

    async def action_reload(self) -> None:
        await self._load_page(self._current_url)

    def action_scroll_up(self) -> None:
        if not self._content_is_focused():
            return
        content = self.query_one("#content", ContentView)
        content.scroll_up()

    def action_scroll_down(self) -> None:
        if not self._content_is_focused():
            return
        content = self.query_one("#content", ContentView)
        content.scroll_down()

    def action_page_up(self) -> None:
        if not self._content_is_focused():
            return
        content = self.query_one("#content", ContentView)
        content.scroll_page_up()

    def action_page_down(self) -> None:
        if not self._content_is_focused():
            return
        content = self.query_one("#content", ContentView)
        content.scroll_page_down()

    def action_scroll_home(self) -> None:
        if not self._content_is_focused():
            return
        content = self.query_one("#content", ContentView)
        content.scroll_home()

    def action_scroll_end(self) -> None:
        if not self._content_is_focused():
            return
        content = self.query_one("#content", ContentView)
        content.scroll_end()

    def action_select_next_link(self) -> None:
        if not self._content_is_focused() or not self._links:
            return
        self._selected_link = min(self._selected_link + 1, len(self._links) - 1)
        self._update_content()

    def action_select_prev_link(self) -> None:
        if not self._content_is_focused() or not self._links:
            return
        self._selected_link = max(self._selected_link - 1, 0)
        self._update_content()

    async def action_open_selected_link(self) -> None:
        if not self._content_is_focused():
            return
        if 0 <= self._selected_link < len(self._links):
            link = self._links[self._selected_link]
            await self._load_page(link.url)

    async def action_go_back(self) -> None:
        url = self._history.back()
        if url:
            await self._load_page(url, from_history=True)

    async def action_go_forward(self) -> None:
        url = self._history.forward()
        if url:
            await self._load_page(url, from_history=True)
