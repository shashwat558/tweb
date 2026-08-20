import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from tweb.browser.engine import BrowserEngine
from tweb.networking.client import NetworkError


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
