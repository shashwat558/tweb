from __future__ import annotations

from rich.console import Console

from tweb.parser.elements import Document
from tweb.renderer.document import DocumentRenderer


class TerminalRenderer:
    def __init__(self) -> None:
        self._console = Console()
        self._doc_renderer = DocumentRenderer(width=self._console.width)

    def render(self, document: Document) -> None:
        self._doc_renderer.set_width(self._console.width)
        renderable = self._doc_renderer.render(document)
        self._console.print(renderable)
