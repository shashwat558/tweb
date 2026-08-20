from tweb.browser.history import BrowserHistory


class TestBrowserHistory:
    def test_push_and_current(self) -> None:
        h = BrowserHistory()
        h.push("https://a.com")
        assert h.current == "https://a.com"

    def test_back(self) -> None:
        h = BrowserHistory()
        h.push("https://a.com")
        h.push("https://b.com")
        h.push("https://c.com")

        assert h.back() == "https://b.com"
        assert h.back() == "https://a.com"
        assert h.back() is None

    def test_forward(self) -> None:
        h = BrowserHistory()
        h.push("https://a.com")
        h.push("https://b.com")
        h.push("https://c.com")

        h.back()
        h.back()
        assert h.forward() == "https://b.com"
        assert h.forward() == "https://c.com"
        assert h.forward() is None

    def test_forward_cleared_on_new_push(self) -> None:
        h = BrowserHistory()
        h.push("https://a.com")
        h.push("https://b.com")
        h.push("https://c.com")

        h.back()
        h.back()
        h.push("https://d.com")

        assert h.forward() is None
        assert h.current == "https://d.com"

    def test_can_go_back(self) -> None:
        h = BrowserHistory()
        assert h.can_go_back() is False
        h.push("https://a.com")
        assert h.can_go_back() is False
        h.push("https://b.com")
        assert h.can_go_back() is True

    def test_can_go_forward(self) -> None:
        h = BrowserHistory()
        assert h.can_go_forward() is False
        h.push("https://a.com")
        h.push("https://b.com")
        h.back()
        assert h.can_go_forward() is True
        h.forward()
        assert h.can_go_forward() is False

    def test_empty_history(self) -> None:
        h = BrowserHistory()
        assert h.current is None
        assert h.back() is None
        assert h.forward() is None
