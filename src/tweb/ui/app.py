from __future__ import annotations

import textwrap

from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Footer, Header, Input, LoadingIndicator, Static

from tweb.browser.engine import BrowserEngine
from tweb.browser.history import BrowserHistory
from tweb.parser.elements import (
    Blockquote,
    CodeBlock,
    Document,
    Form,
    Heading,
    HorizontalRule,
    Image,
    Link,
    List,
    Paragraph,
    Table,
)
from tweb.ui.keybindings import BINDINGS
from tweb.ui.widgets import ContentView, StatusBar


class TWebInput(Input):
    class FocusContent(Message):
        pass

    def on_key(self, event) -> None:
        if event.key == "escape":
            event.stop()
            self.post_message(self.FocusContent())


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

    #loading {
        dock: top;
        height: 1;
        display: none;
    }

    #loading.visible {
        display: block;
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
            yield TWebInput(placeholder="Enter URL...", id="url-input", value=self._initial_url)
        with Vertical(id="find-bar"):
            yield TWebInput(placeholder="Find in page... (Enter to search)", id="find-input")
        yield ContentView(id="content")
        yield LoadingIndicator(id="loading")
        yield StatusBar(id="status-bar")
        yield Footer()

    @on(TWebInput.FocusContent)
    def _handle_focus_content(self) -> None:
        find_bar = self.query_one("#find-bar")
        if self._find_visible:
            find_bar.remove_class("visible")
            self._find_visible = False
            self._find_matches = []
            self._find_index = 0
        self.query_one("#content", ContentView).focus()

    def _get_content_width(self) -> int:
        if self.size.width > 0:
            return self.size.width - 4
        return 80

    def _wrap(self, text: str, width: int, indent: str = "") -> list[str]:
        wrapped = textwrap.wrap(text, width=width, initial_indent=indent, subsequent_indent=indent)
        return wrapped if wrapped else [indent + text] if text else [""]

    def on_mount(self) -> None:
        self._load_page(self._initial_url)

    def _show_loading(self) -> None:
        loading = self.query_one("#loading")
        loading.add_class("visible")

    def _hide_loading(self) -> None:
        loading = self.query_one("#loading")
        loading.remove_class("visible")

    @work(exclusive=True, group="page_load")
    async def _load_page(self, url: str, from_history: bool = False) -> None:
        status_bar = self.query_one("#status-bar", StatusBar)
        content = self.query_one("#content", ContentView)
        url_input = self.query_one("#url-input", TWebInput)

        status_bar.set_status(f"Loading {url}...")
        url_input.value = url
        self._current_url = url
        self._selected_link = -1
        self._links = []
        self._find_matches = []
        self._find_index = 0
        self._show_loading()

        try:
            document = await self._engine.navigate(url)
            self._document = document
            self._links = document.links
            rich_text = self._format_document(document)
            content.set_content(rich_text)
            status_bar.set_status(f"{document.title} - {url}")
            if not from_history:
                self._history.push(url)
            content.focus()
        except Exception as e:
            error_text = Text()
            error_text.append(f"Error loading {url}:\n", style="bold red")
            error_text.append(str(e), style="red")
            content.set_content(error_text)
            status_bar.set_status("Error loading page")
            content.focus()
        finally:
            self._hide_loading()

    def _format_document(self, document: Document) -> Text:
        w = self._get_content_width()
        result = Text()

        result.append("═" * w + "\n", style="bold white")
        result.append(f"  {document.title}\n", style="bold white on blue")
        result.append("═" * w + "\n\n", style="bold white")

        for block in document.blocks:
            result.append_text(self._render_block(block, w))
            result.append("\n")

        if document.links:
            result.append("─" * w + "\n", style="dim")
            result.append("  Links:\n", style="bold cyan")
            for i, link in enumerate(document.links):
                marker = "▶ " if i == self._selected_link else "  "
                marker_style = "bold yellow" if i == self._selected_link else ""
                result.append(marker, style=marker_style)
                result.append(f"[{link.index + 1}] ", style="bold cyan")
                result.append(f"{link.text}\n", style="underline cyan")
            result.append("─" * w + "\n", style="dim")

        return result

    def _render_block(self, block, w: int) -> Text:
        result = Text()

        if isinstance(block, Heading):
            prefix = "#" * block.level
            style = {1: "bold white", 2: "bold bright_white", 3: "bold"}.get(block.level, "bold")
            for line in self._wrap(block.text, w - len(prefix) - 1):
                result.append(f"{prefix} {line}\n", style=style)

        elif isinstance(block, Paragraph):
            if block.parts:
                self._render_rich_paragraph(result, block, w)
            else:
                for line in self._wrap(block.text, w):
                    result.append(f"{line}\n")

        elif isinstance(block, Link):
            result.append(f"  [{block.index + 1}] ", style="bold cyan")
            result.append(f"{block.text}\n", style="underline cyan")

        elif isinstance(block, Image):
            alt_text = block.alt or "image"
            result.append(f"  [Image: {alt_text}]\n", style="dim italic")

        elif isinstance(block, CodeBlock):
            inner_w = w - 4
            result.append("  ┌" + "─" * inner_w + "┐\n", style="dim")
            lines = block.code.split("\n")
            if not lines:
                lines = [""]
            for line in lines:
                display = line[:inner_w].ljust(inner_w)
                result.append(f"  │ {display} │\n", style="on grey11")
            result.append("  └" + "─" * inner_w + "┘\n", style="dim")

        elif isinstance(block, List):
            for i, item in enumerate(block.items):
                bullet = f"  {i + 1}." if block.ordered else "  •"
                for item_block in item.blocks:
                    if isinstance(item_block, Paragraph):
                        for line in self._wrap(item_block.text, w - len(bullet) - 1):
                            result.append(f"{bullet} {line}\n")
                        bullet = "   " if block.ordered else "  "
                    elif isinstance(item_block, Link):
                        result.append(f"{bullet} ", style="")
                        result.append(f"[{item_block.index + 1}] ", style="bold cyan")
                        result.append(f"{item_block.text}\n", style="underline cyan")
                        bullet = "   " if block.ordered else "  "

        elif isinstance(block, Table):
            self._render_table(result, block, w)

        elif isinstance(block, HorizontalRule):
            result.append("─" * w + "\n", style="dim")

        elif isinstance(block, Form):
            self._render_form(result, block, w)

        elif isinstance(block, Blockquote):
            for sub_block in block.blocks:
                inner = self._render_block(sub_block, w - 4)
                for line in inner.plain.split("\n"):
                    if line.strip():
                        result.append(f"  ▸ {line}\n", style="italic dim")
                    else:
                        result.append("\n")

        return result

    def _render_rich_paragraph(self, result: Text, block: Paragraph, w: int) -> None:
        full_text = block.text
        wrapped_lines = self._wrap(full_text, w)

        if not wrapped_lines:
            return

        parts_by_offset: dict[int, tuple[int, object]] = {}
        pos = 0
        for part in block.parts:
            idx = full_text.find(part.content, pos)
            if idx >= 0:
                parts_by_offset[idx] = (idx + len(part.content), part)
            pos = idx + len(part.content) if idx >= 0 else pos

        for line in wrapped_lines:
            line_stripped = line.strip()
            line_start = full_text.find(line_stripped)
            if line_start < 0:
                result.append(f"{line}\n")
                continue

            current = line_start
            line_end = line_start + len(line_stripped)

            while current < line_end:
                styled = False
                for start_offset, (end_offset, part) in parts_by_offset.items():
                    if start_offset <= current < end_offset:
                        style_parts = []
                        if part.bold:
                            style_parts.append("bold")
                        if part.italic:
                            style_parts.append("italic")
                        if part.underline:
                            style_parts.append("underline")
                        if part.code:
                            style_parts.append("on grey11")
                        style = " ".join(style_parts) if style_parts else ""

                        seg_start = max(current, start_offset)
                        seg_end = min(line_end, end_offset)
                        segment = full_text[seg_start:seg_end]
                        result.append(segment, style=style)
                        current = seg_end
                        styled = True
                        break

                if not styled:
                    next_styled = line_end
                    for start_offset in parts_by_offset:
                        if start_offset > current:
                            next_styled = min(next_styled, start_offset)
                            break
                    segment = full_text[current:next_styled]
                    result.append(segment)
                    current = next_styled

            result.append("\n")

    def _render_table(self, result: Text, table: Table, w: int) -> None:
        if not table.rows:
            return

        num_cols = max(len(row.cells) for row in table.rows)
        max_col_w = max(10, (w - num_cols * 3) // max(num_cols, 1))

        col_widths = [0] * num_cols
        for row in table.rows:
            for i, cell in enumerate(row.cells):
                col_widths[i] = min(max(col_widths[i], len(cell.text)), max_col_w)

        header_rows = [row for row in table.rows if any(c.header for c in row.cells)]
        data_rows = [row for row in table.rows if not any(c.header for c in row.cells)]

        sep = "┼".join("─" * (cw + 2) for cw in col_widths)

        def render_row(row: TableRow) -> None:
            parts = []
            for i, cell in enumerate(row.cells):
                width = col_widths[i] if i < len(col_widths) else 10
                text = cell.text[:width].ljust(width)
                parts.append(f" {text} ")
            line = "│".join(parts)
            style = "bold" if any(c.header for c in row.cells) else ""
            result.append(f"{line}\n", style=style)

        for row in header_rows:
            render_row(row)
        if header_rows and data_rows:
            result.append(f"{sep}\n", style="dim")
        for row in data_rows:
            render_row(row)

        if not header_rows:
            result.append(f"{sep}\n", style="dim")

    def _render_form(self, result: Text, form: Form, w: int) -> None:
        inner_w = w - 4
        result.append("  ┌" + "─" * inner_w + "┐\n", style="dim")
        for field in form.fields:
            name = field.name or field.field_type
            if field.field_type == "textarea":
                result.append(f"  │ {name}:\n", style="bold")
                result.append(f"  │ {'─' * inner_w} │\n", style="dim")
            else:
                placeholder = field.placeholder or name
                result.append(f"  │ {name}: [{placeholder}]{' ' * max(0, inner_w - len(name) - len(placeholder) - 4)}│\n", style="bold")
        result.append(f"  │ {form.submit_text}{' ' * max(0, inner_w - len(form.submit_text) - 2)}│\n", style="bold white on blue")
        result.append("  └" + "─" * inner_w + "┘\n", style="dim")

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

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "url-input":
            url = event.value.strip()
            if url:
                from tweb.cli import normalize_url
                url = normalize_url(url)
                self._load_page(url)
        elif event.input.id == "find-input":
            query = event.value.strip()
            self._find_query = query
            self._perform_find(query)

    async def action_focus_url(self) -> None:
        url_input = self.query_one("#url-input", TWebInput)
        url_input.focus()

    async def action_focus_content(self) -> None:
        find_bar = self.query_one("#find-bar")
        if self._find_visible:
            find_bar.remove_class("visible")
            self._find_visible = False
            self._find_matches = []
            self._find_index = 0
        self.query_one("#content", ContentView).focus()

    async def action_toggle_find(self) -> None:
        find_bar = self.query_one("#find-bar")
        self._find_visible = not self._find_visible
        if self._find_visible:
            find_bar.add_class("visible")
            find_input = self.query_one("#find-input", TWebInput)
            find_input.focus()
        else:
            find_bar.remove_class("visible")
            self._find_matches = []
            self._find_index = 0
            self.query_one("#content", ContentView).focus()

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
        self._load_page(self._current_url)

    def action_scroll_up(self) -> None:
        self.query_one("#content", ContentView).scroll_up()

    def action_scroll_down(self) -> None:
        self.query_one("#content", ContentView).scroll_down()

    def action_page_up(self) -> None:
        self.query_one("#content", ContentView).scroll_page_up()

    def action_page_down(self) -> None:
        self.query_one("#content", ContentView).scroll_page_down()

    def action_scroll_home(self) -> None:
        self.query_one("#content", ContentView).scroll_home()

    def action_scroll_end(self) -> None:
        self.query_one("#content", ContentView).scroll_end()

    def action_select_next_link(self) -> None:
        if not self._links:
            return
        self._selected_link = min(self._selected_link + 1, len(self._links) - 1)
        if self._document:
            content = self.query_one("#content", ContentView)
            content.set_content(self._format_document(self._document))

    def action_select_prev_link(self) -> None:
        if not self._links:
            return
        self._selected_link = max(self._selected_link - 1, 0)
        if self._document:
            content = self.query_one("#content", ContentView)
            content.set_content(self._format_document(self._document))

    async def action_open_selected_link(self) -> None:
        if 0 <= self._selected_link < len(self._links):
            link = self._links[self._selected_link]
            self._load_page(link.url)

    async def action_go_back(self) -> None:
        url = self._history.back()
        if url:
            self._load_page(url, from_history=True)

    async def action_go_forward(self) -> None:
        url = self._history.forward()
        if url:
            self._load_page(url, from_history=True)
