from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Input, Static


class StatusBar(Static):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._status = "Ready"

    def compose(self) -> ComposeResult:
        yield Static(self._status, id="status-text")

    def set_status(self, status: str) -> None:
        self._status = status
        self.query_one("#status-text", Static).update(status)


class ContentView(Static):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._content = ""

    def set_content(self, content: str) -> None:
        self._content = content
        self.update(content)

    def get_content(self) -> str:
        return self._content
