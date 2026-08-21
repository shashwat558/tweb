from __future__ import annotations

from tweb.networking.client import NetworkClient, NetworkError
from tweb.parser.html import HTMLParser
from tweb.parser.elements import Document
from tweb.renderer.terminal import TerminalRenderer


class BrowserEngine:
    def __init__(self) -> None:
        self._client = NetworkClient()
        self._parser = HTMLParser()
        self._renderer = TerminalRenderer()

    async def navigate(self, url: str) -> Document:
        response = await self._client.fetch(url)
        html = response.text
        document = self._parser.parse(html, str(response.url))
        return document

    async def submit_form(self, url: str, method: str, data: dict[str, str]) -> Document:
        response = await self._client.submit(url, method, data)
        html = response.text
        document = self._parser.parse(html, str(response.url))
        return document

    async def run(self, url: str) -> None:
        try:
            document = await self.navigate(url)
            self._renderer.render(document)
        except NetworkError as e:
            raise SystemExit(str(e))
