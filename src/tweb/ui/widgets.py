from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static


class StatusBar(Static):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._status = "Ready"

    def compose(self) -> ComposeResult:
        yield Static(self._status, id="status-text")

    def set_status(self, status: str) -> None:
        self._status = status
        self.query_one("#status-text", Static).update(status)


class ContentView(Widget):
    can_focus = True
    can_focus_children = False

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._content = ""
        self._rich_content: Text | None = None

    def compose(self) -> ComposeResult:
        yield Static(self._content, id="content-text")

    def set_content(self, content: str | Text) -> None:
        if isinstance(content, Text):
            self._rich_content = content
            self._content = content.plain
        else:
            self._content = content
            self._rich_content = None
        static = self.query_one("#content-text", Static)
        if self._rich_content:
            static.update(self._rich_content)
        else:
            static.update(content)

    def get_content(self) -> str:
        return self._content
