from __future__ import annotations


class BrowserHistory:
    def __init__(self) -> None:
        self._back: list[str] = []
        self._current: str | None = None
        self._forward: list[str] = []

    @property
    def current(self) -> str | None:
        return self._current

    def push(self, url: str) -> None:
        if self._current is not None:
            self._back.append(self._current)
        self._current = url
        self._forward.clear()

    def back(self) -> str | None:
        if not self._back:
            return None
        if self._current is not None:
            self._forward.append(self._current)
        self._current = self._back.pop()
        return self._current

    def forward(self) -> str | None:
        if not self._forward:
            return None
        if self._current is not None:
            self._back.append(self._current)
        self._current = self._forward.pop()
        return self._current

    def can_go_back(self) -> bool:
        return len(self._back) > 0

    def can_go_forward(self) -> bool:
        return len(self._forward) > 0
