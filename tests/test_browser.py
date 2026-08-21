import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from tweb.browser.engine import BrowserEngine
from tweb.networking.client import NetworkClient, NetworkError


class TestBrowserEngine:
    @pytest.mark.asyncio
    async def test_navigate_fetches_and_parses(self) -> None:
        engine = BrowserEngine()
        mock_response = MagicMock()
        mock_response.text = "<html><head><title>Test</title></head><body><p>Hello</p></body></html>"
        mock_response.url = "https://example.com"

        with patch.object(engine._client, "fetch", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_response
            doc = await engine.navigate("https://example.com")

            assert doc.title == "Test"
            assert len(doc.blocks) == 1
            mock_fetch.assert_called_once_with("https://example.com")

    @pytest.mark.asyncio
    async def test_navigate_handles_network_error(self) -> None:
        engine = BrowserEngine()

        with patch.object(engine._client, "fetch", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = NetworkError("Connection failed")
            with pytest.raises(NetworkError, match="Connection failed"):
                await engine.navigate("https://example.com")

    @pytest.mark.asyncio
    async def test_submit_form_get(self) -> None:
        engine = BrowserEngine()
        mock_response = MagicMock()
        mock_response.text = "<html><head><title>Results</title></head><body><p>Found</p></body></html>"
        mock_response.url = "https://example.com/search?q=hello"

        with patch.object(engine._client, "submit", new_callable=AsyncMock) as mock_submit:
            mock_submit.return_value = mock_response
            doc = await engine.submit_form("https://example.com/search", "GET", {"q": "hello"})

            assert doc.title == "Results"
            assert len(doc.blocks) == 1
            mock_submit.assert_called_once_with("https://example.com/search", "GET", {"q": "hello"})

    @pytest.mark.asyncio
    async def test_submit_form_post(self) -> None:
        engine = BrowserEngine()
        mock_response = MagicMock()
        mock_response.text = "<html><head><title>Posted</title></head><body><p>Done</p></body></html>"
        mock_response.url = "https://example.com/submit"

        with patch.object(engine._client, "submit", new_callable=AsyncMock) as mock_submit:
            mock_submit.return_value = mock_response
            doc = await engine.submit_form("https://example.com/submit", "POST", {"comment": "test"})

            assert doc.title == "Posted"
            mock_submit.assert_called_once_with("https://example.com/submit", "POST", {"comment": "test"})

    @pytest.mark.asyncio
    async def test_submit_form_handles_network_error(self) -> None:
        engine = BrowserEngine()

        with patch.object(engine._client, "submit", new_callable=AsyncMock) as mock_submit:
            mock_submit.side_effect = NetworkError("Timeout")
            with pytest.raises(NetworkError, match="Timeout"):
                await engine.submit_form("https://example.com", "GET", {})
